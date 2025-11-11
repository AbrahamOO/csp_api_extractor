import posixpath
import re
from typing import Dict, Iterable, List, Tuple

import requests
from requests import RequestException

from utils.schema_parser import parse_schema_tree

RAW_SPEC_BASE = "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main"
README_TEMPLATE = RAW_SPEC_BASE + "/specification/{service}/resource-manager/readme.md"
REQUEST_TIMEOUT = 30
HTTP_METHODS = {"get", "put", "post", "delete", "patch", "options", "head"}


def _fetch_text(url: str) -> str:
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except RequestException as exc:
        raise RuntimeError(f"Unable to download Azure README from {url}: {exc}") from exc


def _fetch_json(url: str) -> dict:
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except RequestException as exc:
        raise RuntimeError(f"Unable to download Azure OpenAPI document from {url}: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"Received invalid JSON payload from {url}: {exc}") from exc


def _extract_input_files(readme_text: str) -> List[str]:
    pattern = re.compile(r"input-file:\s*\n(?P<body>(?:[ \t]+\-\s+[^\n]+\n)+)", re.IGNORECASE)
    match = pattern.search(readme_text)
    if not match:
        return []
    files = []
    for line in match.group("body").splitlines():
        stripped = line.strip()
        if stripped.startswith("-"):
            path = stripped[1:].strip()
            if path:
                files.append(path)
    return files


def _resolve_spec_url(service: str, relative_path: str) -> str:
    base_dir = f"specification/{service}/resource-manager"
    relative_path = relative_path.lstrip("/")
    joined = posixpath.normpath(posixpath.join(base_dir, relative_path))
    return f"{RAW_SPEC_BASE}/{joined}"


def _build_schema_lookup(openapi_doc: dict) -> Dict[str, dict]:
    schemas = {}

    for name, schema in (openapi_doc.get("definitions") or {}).items():
        schemas[f"#/definitions/{name}"] = schema

    components = openapi_doc.get("components") or {}
    for name, schema in (components.get("schemas") or {}).items():
        schemas[f"#/components/schemas/{name}"] = schema

    return schemas


def _build_request_body_lookup(openapi_doc: dict) -> Dict[str, dict]:
    components = openapi_doc.get("components") or {}
    return components.get("requestBodies") or {}


def _build_component_parameters(openapi_doc: dict) -> Tuple[Dict[str, dict], Dict[str, dict]]:
    legacy_params = openapi_doc.get("parameters") or {}
    components = openapi_doc.get("components") or {}
    component_params = components.get("parameters") or {}
    return legacy_params, component_params


def _resolve_parameter_ref(ref: str, legacy_params: Dict[str, dict], component_params: Dict[str, dict]) -> dict:
    if ref.startswith("#/parameters/"):
        key = ref.split("/")[-1]
        return legacy_params.get(key, {})
    if ref.startswith("#/components/parameters/"):
        key = ref.split("/")[-1]
        return component_params.get(key, {})
    return {}


def _iter_parameters(parameter_list: Iterable[dict], legacy_params: Dict[str, dict], component_params: Dict[str, dict]):
    for param in parameter_list or []:
        if not isinstance(param, dict):
            continue
        if "$ref" in param:
            resolved = _resolve_parameter_ref(param["$ref"], legacy_params, component_params)
            if resolved:
                yield resolved
            continue
        yield param


def _dereference_request_body(request_body: dict, request_bodies: Dict[str, dict]) -> dict:
    if "$ref" not in request_body:
        return request_body
    ref = request_body["$ref"]
    if ref.startswith("#/components/requestBodies/"):
        key = ref.split("/")[-1]
        return request_bodies.get(key, {})
    return request_body


def _extract_schema_from_request(method_doc: dict, request_bodies: Dict[str, dict]):
    request_body = method_doc.get("requestBody")
    if isinstance(request_body, dict):
        deref = _dereference_request_body(request_body, request_bodies)
        content = deref.get("content") or {}
        for media in content.values():
            schema = media.get("schema")
            if schema:
                return schema
    return None


def _extract_schema_from_parameters(method_doc: dict, legacy_params: Dict[str, dict], component_params: Dict[str, dict]):
    for param in _iter_parameters(method_doc.get("parameters"), legacy_params, component_params):
        if param.get("in") == "body" and param.get("schema"):
            return param["schema"]
        if param.get("schema"):
            return param["schema"]
    return None


def _build_parameter_rows(method_doc: dict, legacy_params: Dict[str, dict], component_params: Dict[str, dict]):
    rows = []
    for param in _iter_parameters(method_doc.get("parameters"), legacy_params, component_params):
        name = param.get("name", "parameter")
        label = name
        if param.get("required"):
            label = f"{label} (required)"
        param_type = param.get("type") or param.get("schema", {}).get("type")
        if param_type:
            label = f"{label} ({param_type})"
        rows.append((0, label))
    return rows


def _build_tree(method_doc: dict, schemas: Dict[str, dict], legacy_params: Dict[str, dict], component_params: Dict[str, dict], request_bodies: Dict[str, dict]):
    schema = _extract_schema_from_request(method_doc, request_bodies)
    if not schema:
        schema = _extract_schema_from_parameters(method_doc, legacy_params, component_params)

    if schema:
        parsed = parse_schema_tree(schema, schemas)
        if parsed:
            return parsed

    return _build_parameter_rows(method_doc, legacy_params, component_params)


def extract_azure_service_apis(service):
    readme_url = README_TEMPLATE.format(service=service)
    readme_text = _fetch_text(readme_url)
    swagger_paths = _extract_input_files(readme_text)

    if not swagger_paths:
        raise RuntimeError(f"Could not locate 'input-file' entries in Azure README for '{service}'.")

    swagger_url = _resolve_spec_url(service, swagger_paths[0])
    openapi_doc = _fetch_json(swagger_url)

    schemas = _build_schema_lookup(openapi_doc)
    request_bodies = _build_request_body_lookup(openapi_doc)
    legacy_params, component_params = _build_component_parameters(openapi_doc)

    paths = openapi_doc.get("paths") or {}
    if not paths:
        raise RuntimeError(f"The Azure OpenAPI document for '{service}' does not contain any paths.")

    output_data = []

    for api_path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method_name, method_doc in path_item.items():
            if method_name.lower() not in HTTP_METHODS:
                continue
            method_label = method_doc.get("operationId") or method_name.upper()
            tree = _build_tree(method_doc, schemas, legacy_params, component_params, request_bodies)
            output_data.append(
                {
                    "apiPath": api_path,
                    "resource": api_path,
                    "method": method_label,
                    "tree": tree,
                }
            )

    return output_data
