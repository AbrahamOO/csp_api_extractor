from collections import OrderedDict

from openpyxl import Workbook

INVALID_SHEET_CHARS = set(r'[]:*?/\\')
MAX_SHEET_LENGTH = 31


def _make_sheet_title(label, existing_titles):
    cleaned = "".join(ch if ch not in INVALID_SHEET_CHARS else " " for ch in label or "Sheet")
    cleaned = cleaned.strip() or "Sheet"
    cleaned = cleaned[:MAX_SHEET_LENGTH]
    candidate = cleaned
    counter = 2
    while candidate in existing_titles:
        suffix = f" ({counter})"
        max_base = MAX_SHEET_LENGTH - len(suffix)
        base = cleaned[:max_base].rstrip() or cleaned[:max_base]
        candidate = f"{base}{suffix}"
        counter += 1
    existing_titles.add(candidate)
    return candidate


def _populate_sheet(ws, provider, service_label, api_data):
    target_label = (
        f"{service_label} API Action"
        if provider == "aws"
        else f"{service_label} REST Resource"
        if provider == "gcp"
        else f"{service_label} Resource Operation"
    )
    method_label = "API Method"

    max_level = 4
    for item in api_data:
        for level, _ in item.get("tree") or []:
            if isinstance(level, int):
                max_level = max(max_level, level)

    num_levels = max(5, max_level + 1)
    level_headers = [f"Level {idx}" for idx in range(1, num_levels + 1)]

    if provider == "aws":
        headers = [target_label, *level_headers]
        ws.append(headers)
        ws.freeze_panes = "A2"

        for item in api_data:
            action_name = item.get("method", "")
            tree_rows = item.get("tree") or []

            action_row = [action_name] + [""] * num_levels
            ws.append(action_row)

            for level, param in tree_rows:
                depth = level if isinstance(level, int) else 0
                depth = max(0, depth)
                if depth >= num_levels:
                    depth = num_levels - 1
                level_cells = [""] * num_levels
                level_cells[depth] = param
                indent_row = [""] + level_cells
                ws.append(indent_row)
    else:
        headers = [target_label, method_label, *level_headers]
        ws.append(headers)
        ws.freeze_panes = "A2"

        grouped = OrderedDict()
        for item in api_data:
            resource_key = item.get("resource") or service_label
            if resource_key not in grouped:
                grouped[resource_key] = []
            grouped[resource_key].append(item)

        for resource, methods in grouped.items():
            resource_written = False
            for method_entry in methods:
                method_name = method_entry.get("method", "")
                tree_rows = method_entry.get("tree") or []

                resource_cell = resource if not resource_written else ""
                resource_written = True

                method_row = [resource_cell, method_name] + [""] * num_levels
                ws.append(method_row)

                for level, param in tree_rows:
                    depth = level if isinstance(level, int) else 0
                    depth = max(0, depth)
                    if depth >= num_levels:
                        depth = num_levels - 1
                    level_cells = [""] * num_levels
                    level_cells[depth] = param
                    param_row = ["", ""] + level_cells
                    ws.append(param_row)


def write_to_excel(variant_runs, output_file, provider):
    wb = Workbook()
    existing_titles = set()

    for idx, run in enumerate(variant_runs):
        service_label = run["label"] or run["key"]
        sheet_title = _make_sheet_title(service_label, existing_titles)
        if idx == 0:
            ws = wb.active
            ws.title = sheet_title
        else:
            ws = wb.create_sheet(title=sheet_title)
        _populate_sheet(ws, provider, service_label, run["data"])

    wb.save(output_file)
