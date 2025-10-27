import requests
from utils.schema_parser import parse_schema_tree

DISCOVERY_URL = "https://discovery.googleapis.com/discovery/v1/apis"

def extract_gcp_service_apis(service):

    discovery_resp = requests.get(DISCOVERY_URL).json()
    service_entry = next((api for api in discovery_resp['items'] if api['name'] == service), None)

    if not service_entry:
        raise Exception(f"Service '{service}' not found in Google Discovery APIs.")

    api_desc_url = service_entry['discoveryRestUrl']
    api_desc = requests.get(api_desc_url).json()
    schemas = api_desc.get('schemas', {})

    base_url = api_desc.get('baseUrl')
    if not base_url:
        root_url = api_desc.get('rootUrl', '')
        service_path = api_desc.get('servicePath', '')
        base_url = f"{root_url}{service_path}"

    output_data = []

    def build_tree(method):
        request_info = method.get('request', {})
        schema_ref = request_info.get('$ref')
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
        for method_name, method in methods.items():
            tree = build_tree(method)
            method_path = method.get("flatPath") or method.get("path", "")
            api_path = build_full_url(method_path)
            resource_label = resource_name or service
            output_data.append({
                "apiPath": api_path,
                "resource": resource_label,
                "method": method_name,
                "tree": tree
            })

    def traverse_resources(prefix, resources):
        for resource_name, resource_data in resources.items():
            full_name = f"{prefix}.{resource_name}" if prefix else resource_name
            append_methods(full_name, resource_data.get('methods', {}))
            child_resources = resource_data.get('resources', {})
            if child_resources:
                traverse_resources(full_name, child_resources)

    # Top-level methods are associated with the service itself.
    append_methods(service, api_desc.get('methods', {}))
    traverse_resources("", api_desc.get('resources', {}))

    return output_data
