# CSP API Extractor

> Ever needed to audit cloud APIs across AWS, GCP, and Azure? This tool does exactly that—pulls service definitions, maps out their parameters, and exports everything to Excel workbooks you can actually use.

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

I built this because manually digging through SDK documentation to understand API parameters is tedious. This extractor grabs live service definitions from AWS, GCP, and Azure, organizes all the operations and request parameters into a clean hierarchy, and spits out Excel files you can share with your team. The CLI walks you through picking a provider and service, then handles the rest.

## Features

- **Live service catalogs** – Pulls the latest service lists from AWS Botocore, GCP Discovery, and Azure REST specs. Everything caches locally in `service_catalog_cache.json` so you're not stuck online.
- **Provider-specific extraction** – Each cloud has its quirks. I wrote dedicated extractors for Botocore `service-2` models, GCP Discovery resources, and Azure OpenAPI specs that actually understand their structure.
- **Smart Excel output** – Generates worksheets with provider-specific headers, hierarchical parameter trees, required-field indicators, and frozen top rows so you can scroll comfortably through massive APIs.
- **Interactive CLI** – Just run it and answer a few prompts. Press `L` to list available services, and it'll suggest sensible file names like `<csp>-<service>-api-extract.xlsx`.
- **Version handling** – AWS has weird service variants (looking at you, SageMaker Runtime). GCP has multiple API versions. This tool detects them and creates separate worksheets so nothing gets lost.

## Project Layout

| Path | Description |
| --- | --- |
| `fetch_api_params.py` | Main CLI that handles provider selection, catalog refresh, prompting, and Excel generation. |
| `extractors/` | Provider-specific modules (`aws_extractor.py`, `gcp_extractor.py`, `azure_extractor.py`) that extract `{resource, method, tree}` data. |
| `writer/excel_writer.py` | Takes extracted data and builds provider-aware Excel workbooks using `openpyxl`. |
| `utils/schema_parser.py` | Recursively transforms JSON schemas into `(level, label)` rows and marks required parameters. |
| `utils/cache_manager.py` | Manages reading and writing the service catalog cache. |
| `OUTPUT_FILES/` | Where your generated workbooks go by default. |
| `requirements.txt` | Python dependencies (Botocore/Boto3, Requests, Google client, OpenPyXL). |

## Prerequisites

- Python 3.8 or newer (check with `python --version`).
- Internet connection for the first run when fetching provider catalogs. After that, it uses the cache.
- No cloud credentials needed—this just reads public API descriptions from the providers' SDKs and REST specs.

## Quick Start

1. Clone this repo and navigate into it:
   ```bash
   git clone <csp_api_extractor repo>
   cd csp_api_extractor
   ```
2. Run the extractor:
   ```bash
   python run_extractor.py
   ```
3. Answer the prompts:
   - Pick your provider: `aws`, `gcp`, or `azure`
   - Enter the service name (hit `L` to see available services). For AWS, you can include variants; for GCP, pick the specific version—each creates its own worksheet.
   - Use the suggested workbook name or type your own (defaults to `OUTPUT_FILES/`).
4. The script sets up a local `.venv`, installs what it needs, and prints the path to your finished Excel file when done.

## Advanced Usage

If you're managing your own Python environment, skip the helper script and run the CLI directly:

```bash
pip install -r requirements.txt
python fetch_api_params.py
```

Same functionality—you just control the environment yourself.

## Workflow Reference

1. **Provider** – Choose `aws`, `gcp`, or `azure`.
2. **Service** – Type the identifier or press `L` to list options. Include AWS variants or pick specific GCP versions if you need them.
3. **Output file** – Defaults to `<csp>-<service>-api-extract.xlsx` (adds `.xlsx` automatically if you forget).
4. **Destination** – Hit Enter to save in `OUTPUT_FILES/`, or specify your own path.
5. The tool prints the full path to your workbook and refreshes the service catalog cache when newer lists are available.

## Troubleshooting

- **"Unable to create default output directory"** – Check you have write permissions in the project folder, or use a different destination.
- **"Unable to write to `<file>.xlsx`"** – Close Excel (or whatever has the file open) and try again.
- **Network errors while refreshing services** – Falls back to the cached list. Run again when you're online to refresh.
- **"Service '<name>' not found"** – Double-check the service name. Press `L` to see the exact spelling.
- **Unexpected crash** – Try `python run_extractor.py` to rebuild the virtual environment. Still broken? Run with `L` to confirm the service exists and send me the console output.

## Excel Output Details

| Provider | Columns | Notes |
| --- | --- | --- |
| AWS | `<service> API Action`, `Level 1..N` | One worksheet per service or variant (like `sagemaker-runtime`). Each action's request parameters show up as an indented tree. |
| GCP | `<service> REST Resource`, `API Method`, `Level 1..N` | One worksheet per API version. Resources are organized with their REST methods and parameter hierarchies. |
| Azure | `<service> Resource Operation`, `API Method`, `Level 1..N` | Same layout as GCP, just using Azure's terminology. |

- `Level` columns expand automatically if schemas go deeper than Level 5.
- Required parameters show `(required)` in their label.
- Map/dictionary structures get nested Key/Value rows so nothing gets hidden.
- Top row is frozen so you can scroll through huge APIs without losing context.

## Service Catalog Refresh

1. Loads `service_catalog_cache.json` if it exists.
2. Tries to fetch the latest service list for your provider.
   - Shows you how many services were added or removed.
   - Saves the updated catalog back to the cache.
3. If the refresh fails (you're offline, got throttled, etc.), it uses the cached list and warns you.

## Extending

Want to customize this? Here are some starting points:

- **Azure OpenAPI tweaks** – Edit [extractors/azure_extractor.py](extractors/azure_extractor.py) to select different tags/spec files or cache Swagger docs locally.
- **GCP rate limits** – Cache Discovery documents if you're running this in automated workflows and hitting rate limits.
- **Excel formatting** – Modify [writer/excel_writer.py](writer/excel_writer.py) to add filters, conditional formatting, or custom layouts.
- **Logging** – Wrap extractor calls in [fetch_api_params.py](fetch_api_params.py) with structured logging for better diagnostics.

## License

MIT. Use it however you want.
