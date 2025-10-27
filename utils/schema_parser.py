def parse_schema_tree(schema, all_schemas, level=0):
    rows = []

    if "$ref" in schema:
        schema = all_schemas.get(schema["$ref"], {})

    schema_type = schema.get("type")
    if schema_type == "object":
        props = schema.get("properties", {})
        required_fields = set(schema.get("required", []))
        for prop, prop_schema in props.items():
            label = prop
            if prop in required_fields:
                label = f"{prop} (required)"
            type_str = prop_schema.get("type", "object")
            if type_str == "object":
                rows.append((level, label))
                rows.extend(parse_schema_tree(prop_schema, all_schemas, level + 1))
            elif type_str == "array" and "items" in prop_schema:
                rows.append((level, f"{label} [array]"))
                rows.extend(parse_schema_tree(prop_schema["items"], all_schemas, level + 1))
            else:
                type_info = f"{label} ({type_str})" if type_str else label
                rows.append((level, type_info))
    elif schema_type == "array" and "items" in schema:
        rows.extend(parse_schema_tree(schema["items"], all_schemas, level))
    return rows
