def parse_schema_tree(schema, all_schemas, level=0, visiting_refs=None, visiting_nodes=None):
    rows = []

    if "$ref" in schema:
        ref = schema["$ref"]
        if visiting_refs is None:
            visiting_refs = set()
        if ref in visiting_refs:
            return rows
        visiting_refs.add(ref)
        schema = all_schemas.get(ref, {})
        rows.extend(parse_schema_tree(schema, all_schemas, level, visiting_refs, visiting_nodes))
        visiting_refs.discard(ref)
        return rows

    if visiting_nodes is None:
        visiting_nodes = set()

    schema_id = id(schema)
    if schema_id in visiting_nodes:
        return rows
    visiting_nodes.add(schema_id)

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
                rows.extend(parse_schema_tree(prop_schema, all_schemas, level + 1, visiting_refs, visiting_nodes))
            elif type_str == "array" and "items" in prop_schema:
                rows.append((level, f"{label} [array]"))
                rows.extend(parse_schema_tree(prop_schema["items"], all_schemas, level + 1, visiting_refs, visiting_nodes))
            else:
                type_info = f"{label} ({type_str})" if type_str else label
                rows.append((level, type_info))
    elif schema_type == "array" and "items" in schema:
        rows.extend(parse_schema_tree(schema["items"], all_schemas, level, visiting_refs, visiting_nodes))

    visiting_nodes.discard(schema_id)
    return rows
