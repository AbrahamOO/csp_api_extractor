# CSP API Extractor

> Audit every AWS, GCP, and Azure service definition from a single CLI and export parameter trees to polished Excel workbooks.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Layout](#project-layout)
4. [Prerequisites](#prerequisites)
5. [Quick Start](#quick-start)
6. [Advanced Usage](#advanced-usage)
7. [Workflow Reference](#workflow-reference)
8. [Troubleshooting](#troubleshooting)
9. [Excel Output Details](#excel-output-details)
10. [Service Catalog Refresh](#service-catalog-refresh)
11. [Extending](#extending)
12. [License](#license)

## Overview

CSP API Extractor inspects live service definitions across the three major cloud providers, builds a full hierarchy of operations plus request parameters, and exports the results to Excel. The CLI guides you through provider selection, service discovery, and output handling so auditors and builders can analyze APIs without sifting through SDK models manually.

## Features

- **Live service catalogs** – pull the latest AWS Botocore service list, GCP Discovery directory, and Azure REST spec repository with optional offline caching in `service_catalog_cache.json`.
- **Provider-specific extraction** – dedicated extractors parse real Botocore `service-2` models, GCP Discovery resources, and Azure OpenAPI specs to capture every operation plus request schema.
- **Excel writer tuned per CSP** – auto-builds worksheets with provider-aware headers, hierarchical parameter columns, required-field badges, and frozen header rows for comfortable review.
- **Guided CLI workflow** – interactive prompts for provider, service, and output path with shortcuts (`L`) to list services and smart defaults like `<csp>-<service>-api-extract.xlsx`.
- **Version-aware selection** – detect related AWS variants (multiple SageMaker runtimes, Lex v2, etc.) and enumerate GCP API versions so each variant/version becomes its own worksheet.

## Project Layout

| Path | Description |
| --- | --- |
| `fetch_api_params.py` | Primary CLI responsible for provider selection, catalog refresh, prompting, and Excel generation. |
| `extractors/` | Provider modules (`aws_extractor.py`, `gcp_extractor.py`, `azure_extractor.py`) that emit `{resource, method, tree}` dictionaries. |
| `writer/excel_writer.py` | Normalizes the extracted data and renders provider-aware Excel workbooks via `openpyxl`. |
| `utils/schema_parser.py` | Recursively transforms JSON schemas into `(level, label)` rows and flags required parameters. |
| `utils/cache_manager.py` | Handles reading/writing of the JSON service catalog cache. |
| `OUTPUT_FILES/` | Default destination for generated workbooks (tracked via `.gitkeep`). |
| `requirements.txt` | Python dependencies (Botocore/Boto3, Requests, Google client, OpenPyXL). |

## Prerequisites

- Python 3.8 or newer (`python --version` to confirm).
- Internet access the first time you refresh a provider catalog (subsequent runs can reuse the cache).
- No cloud credentials are required; the extractor consumes only the public API descriptions distributed with the providers’ SDKs and REST specs.

## Quick Start

1. Clone the repository and move into it:
   ```bash
   git clone <csp_api_extractor repo>
   cd csp_api_extractor
   ```
2. Run the guided extractor:
   ```bash
   python run_extractor.py
   ```
3. Follow the prompts:
   - Choose the provider (`aws`, `gcp`, or `azure`).
   - Enter the service identifier (press `L` to print the available services). Include AWS variants or pick the exact GCP version when prompted—each selection generates its own worksheet.
   - Accept or override the suggested workbook name and output directory (defaults to `OUTPUT_FILES/`).
4. The script provisions/updates the local `.venv`, installs dependencies as needed, and prints the full path to your Excel workbook when extraction finishes.

## Advanced Usage

Already managing dependencies yourself? Skip the helper virtual environment and run the CLI directly:

```bash
pip install -r requirements.txt
python fetch_api_params.py
```

Functionality is identical—the only difference is that you control the Python environment.

## Workflow Reference

1. **Provider** – `aws`, `gcp`, or `azure`.
2. **Service** – type the identifier or press `L` to list options. Include AWS variants or choose specific GCP versions if needed.
3. **Output file** – defaults to `<csp>-<service>-api-extract.xlsx` (the `.xlsx` extension is added automatically when omitted).
4. **Destination** – press Enter to save inside `OUTPUT_FILES/`, or specify any absolute/relative path.
5. The CLI prints the absolute path to the generated workbook and refreshes cached service catalogs whenever newer lists are available.

## Troubleshooting

- **“Unable to create default output directory”** – ensure you have write permissions to the project folder or pick another destination.
- **“Unable to write to `<file>.xlsx`”** – close any application holding the workbook open and rerun the export.
- **Network errors while refreshing services** – the extractor falls back to the cached list and warns you; rerun when online to refresh.
- **“Service '<name>' not found”** – confirm the provider’s canonical identifier (use the `L` shortcut to copy a known-good name).
- **Unexpected crash/stack trace** – rerun via `python run_extractor.py` so dependencies are installed in a clean `.venv`. If it persists, re-run with `L` to verify the service exists and capture the console output for debugging.

## Excel Output Details

| Provider | Columns | Notes |
| --- | --- | --- |
| AWS | `<service> API Action`, `Level 1..N` | Each worksheet covers one AWS service or variant (for example, `sagemaker-runtime`) with every action’s request tree indented beneath it. |
| GCP | `<service> REST Resource`, `API Method`, `Level 1..N` | Each worksheet maps to a specific GCP API version; resources organize their REST methods and parameter hierarchies. |
| Azure | `<service> Resource Operation`, `API Method`, `Level 1..N` | Mirrors the GCP layout but uses Azure terminology for operations/resources. |

- `Level` columns expand dynamically beyond Level 5 for deep schemas.
- Required parameters include `(required)` in their labels.
- Map/dictionary nodes expand into nested Key/Value rows so even complex bodies remain readable.
- Row 1 on every worksheet is frozen for effortless scrolling.

## Service Catalog Refresh

1. Load `service_catalog_cache.json` when present.
2. Attempt a live refresh for the selected provider.
   - Print how many services were added or removed.
   - Persist the updated catalog to the cache.
3. If the refresh fails (offline, throttled, etc.), continue with the cached or bundled list and display a warning.

## Extending

- **Azure OpenAPI tweaks** – adjust `extractors/azure_extractor.py` to select different tags/spec files or to cache downloaded Swagger documents.
- **GCP rate limits** – cache Discovery documents locally if you expect heavy usage in automated workflows.
- **Excel formatting** – enhance `writer/excel_writer.py` with styling, filters, conditional formatting, or custom layouts.
- **Additional logging/telemetry** – wrap extractor calls in `fetch_api_params.py` with structured logging if you need richer diagnostics.

## License

Add your preferred license here (MIT, Apache 2.0, proprietary, etc.).
