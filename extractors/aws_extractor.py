import botocore.session
from utils.schema_parser import parse_schema_tree


def extract_aws_service_apis(service):

    session = botocore.session.get_session()
    loader = session.get_component('data_loader')
    service_model = loader.load_service_model(service, 'service-2')

    operations = service_model.get('operations', {})
    shapes = service_model.get('shapes', {})

    output_data = []

    for op_name, op_info in operations.items():
        input_shape_name = op_info.get('input', {}).get('shape')
        tree = []
        if input_shape_name and input_shape_name in shapes:
            schema = convert_shape_to_schema(input_shape_name, shapes)
            tree = parse_schema_tree(schema, {})

        http_info = op_info.get('http', {})
        api_path = http_info.get('requestUri') or op_name

        output_data.append({
            "apiPath": api_path,
            "resource": service,
            "method": op_name,
            "tree": tree
        })

    return output_data


def convert_shape_to_schema(shape_name, all_shapes, visiting=None):
    if not shape_name:
        return {"type": "object", "properties": {}}

    if visiting is None:
        visiting = set()

    if shape_name in visiting:
        return {"type": "object", "properties": {}}

    visiting.add(shape_name)
    try:
        shape = all_shapes.get(shape_name, {})
        shape_type = shape.get("type", "structure")

        if shape_type == "structure":
            schema = {"type": "object", "properties": {}}
            members = shape.get("members", {})
            for name, spec in members.items():
                member_shape_name = spec.get("shape")
                if member_shape_name:
                    schema["properties"][name] = convert_shape_to_schema(member_shape_name, all_shapes, visiting)
                else:
                    schema["properties"][name] = {"type": "string"}
            return schema

        if shape_type == "list":
            member_shape_name = shape.get("member", {}).get("shape")
            items_schema = convert_shape_to_schema(member_shape_name, all_shapes, visiting) if member_shape_name else {"type": "string"}
            return {"type": "array", "items": items_schema}

        return {"type": shape_type or "string"}
    finally:
        visiting.discard(shape_name)
