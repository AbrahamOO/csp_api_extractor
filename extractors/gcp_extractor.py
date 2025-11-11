import requests
from requests import RequestException

from utils.schema_parser import parse_schema_tree

DISCOVERY_URL = "https://discovery.googleapis.com/discovery/v1/apis"
REQUEST_TIMEOUT = 30


def _fetch_json(url):
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except RequestException as exc:
        raise RuntimeError(f"Unable to download data from {url}: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"Received invalid JSON payload from {url}: {exc}") from exc


def extract_gcp_service_apis(service):
    if "@" in service:
        service_name, _, version = service.partition("@")
        service_key = service_name.lower()
        version_key = version.lower()
    else:
        service_name = service
        version = ""
        service_key = service.lower()
        version_key = ""

    discovery_resp = _fetch_json(DISCOVERY_URL)
    items = discovery_resp.get("items", [])

    service_candidates = [
        api for api in items if api.get("name", "").lower() == service_key
    ]

    if not service_candidates:
        raise RuntimeError(f"Service '{service_name}' not found in Google Discovery APIs.")

    service_entry = None
    if version_key:
        service_entry = next(
            (api for api in service_candidates if api.get("version", "").lower() == version_key),
            None,
        )
        if not service_entry:
            raise RuntimeError(f"Version '{version}' for service '{service_name}' was not found in Google Discovery APIs.")
    else:
        preferred = [
            api for api in service_candidates
            if not any(flag in (api.get("version", "").lower()) for flag in ("beta", "alpha", "preview"))
        ]
        service_entry = preferred[0] if preferred else service_candidates[0]

    api_desc_url = service_entry["discoveryRestUrl"]
    api_desc = _fetch_json(api_desc_url)
    schemas = api_desc.get("schemas", {}) or {}

    base_url = api_desc.get("baseUrl")
    if not base_url:
        root_url = api_desc.get("rootUrl", "")
        service_path = api_desc.get("servicePath", "")
        base_url = f"{root_url}{service_path}"

    output_data = []

    def build_tree(method):
        request_info = method.get("request", {})
        schema_ref = request_info.get("$ref")
        if schema_ref and schema_ref in schemas:
            schema = schemas.get(schema_ref, {})
            if schema:
                return parse_schema_tree(schema, schemas)
        return []

    def build_full_url(path):
        if not path:
            return base_url or ""
        if not base_url:
            return path
        return f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    def append_methods(resource_name, methods):
        for method_name, method in (methods or {}).items():
            tree = build_tree(method)
            method_path = method.get("flatPath") or method.get("path", "")
            api_path = build_full_url(method_path)
            resource_label = resource_name or service
            output_data.append(
                {
                    "apiPath": api_path,
                    "resource": resource_label,
                    "method": method_name,
                    "tree": tree,
                }
            )

    def traverse_resources(prefix, resources):
        for resource_name, resource_data in (resources or {}).items():
            full_name = f"{prefix}.{resource_name}" if prefix else resource_name
            append_methods(full_name, resource_data.get("methods", {}))
            child_resources = resource_data.get("resources", {})
            if child_resources:
                traverse_resources(full_name, child_resources)

    append_methods(service, api_desc.get("methods", {}))
    traverse_resources("", api_desc.get("resources", {}))

    return output_data
