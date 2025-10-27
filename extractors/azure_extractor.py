import requests
from utils.schema_parser import parse_schema_tree

AZURE_REPO_URL = "https://raw.githubusercontent.com/Azure/azure-rest-api-specs/main/specification/{service}/resource-manager/readme.md"

def extract_azure_service_apis(service):
    # Placeholder since Azure Swagger spec requires OpenAPI parser
    # Real implementation would parse the .json OpenAPI docs from GitHub
    # Here we simulate with a mock structure

    output_data = [
        {
            "apiPath": "/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.Service/resource",
            "resource": service,
            "method": "createOrUpdate",
            "tree": [
                (0, "name (string)"),
                (0, "location (string)"),
                (0, "properties"),
                (1, "settingA (string)"),
                (1, "settingB (boolean)"),
            ]
        }
    ]
    return output_data
