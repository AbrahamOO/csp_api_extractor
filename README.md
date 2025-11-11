## CSP API Extractor

CSP API Extractor inspects AWS, GCP, and Azure services and exports a tree of operations/methods plus request parameters into a structured Excel workbook. The tool automates service discovery, prompts for the cloud/service you want to inspect, and produces provider-specific spreadsheet layouts that make it easy to audit available APIs.

---

### Key Features

- **Live service catalogs** – pulls the latest AWS service list via Botocore, the public GCP Discovery directory, and the Azure REST spec repo. Results are cached in `service_catalog_cache.json` for offline reuse.
- **Provider-specific extractors**
  - *AWS*: loads the Botocore `service-2` models to enumerate every API action and its request shape.
  - *GCP*: walks the Discovery document for the chosen service, covering top-level and nested REST resources.
  - *Azure*: pulls the live OpenAPI (Swagger) specs from the Azure REST API repo, parses the real request schemas, and outputs production-ready parameter trees.
- **Excel writer tailored per CSP**
  - AWS sheets show `<service> API Action` followed by hierarchical parameter levels.
  - GCP sheets show `<service> REST Resource`, `API Method`, and parameter levels.
  - Azure sheets show `<service> Resource Operation`, `API Method`, and parameter levels.
  - Required fields are annotated with `(required)` and the header row is frozen for easier scanning.
- **Guided CLI workflow** – prompts for provider/service (with an `L` shortcut to list services in a padded table), pre-fills a default filename (`<csp>-<service>-api-extract.xlsx`), and offers to save into the local `OUTPUT_FILES` directory.
- **Version-aware selection** – the CLI detects related AWS service variants (for example, every SageMaker runtime, even if you start from `sagemaker-runtime`) and the available GCP API versions. Each variant/version gets its own worksheet inside the generated workbook so their actions and parameters are never mixed.

---

### Project Layout

| Path | Description |
| --- | --- |
| `fetch_api_params.py` | Entry point CLI that orchestrates provider selection, catalog refresh, prompting, and Excel generation. |
| `extractors/` | One module per CSP (`aws_extractor.py`, `gcp_extractor.py`, `azure_extractor.py`). Each returns a list of `{resource, method, tree}` dictionaries. |
| `writer/excel_writer.py` | Normalizes the extracted data into provider-aware Excel workbooks using `openpyxl`. |
| `utils/schema_parser.py` | Recursively converts JSON schemas into `(level, label)` rows, marking required parameters. |
| `utils/cache_manager.py` | Reads/writes the JSON service catalog cache. |
| `OUTPUT_FILES/` | Default destination for generated workbooks (retained via `.gitkeep`). |
| `requirements.txt` | Python dependencies (Botocore/Boto3, Requests, Google client, OpenPyXL). |

---

### Get the Code

If you have not pulled the project yet, clone it and switch into the folder:

```bash
git clone <csp_api_extractor repo>
cd csp_api_extractor
```

(You can also unzip a downloaded archive—the remaining steps simply assume your terminal is already inside the project directory.)

---

### What You Need

- Python 3.8+ installed (run `python --version` to double-check).
- Internet access the first time you list services for a provider (catalogs are cached afterward).
- No cloud credentials are required. The tool only reads the public API descriptions that ship with Google/AWS SDKs or the Azure REST spec repo.

---

### How to Run

1. Open a terminal (macOS Terminal, Windows Terminal, etc.) and `cd` into this project.
2. Run the extractor:
   ```bash
   python run_extractor.py
   ```
3. Respond to the prompts:
   - Enter the provider (`aws`, `gcp`, or `azure`).
   - Enter the service you want (press `L` or `l` to print the full service list). When prompted, include any AWS service variants (all SageMaker runtimes, Lex v2, etc.) or pick the precise GCP API versions (`v1`, `beta`, etc.). Every variant/version becomes its own worksheet inside the same Excel file.
   - Press Enter to accept the suggested Excel file name and the default `OUTPUT_FILES/` folder, or type your own choices. If you select multiple variants/versions, the workbook automatically gains one sheet per selection.
4. Wait for the confirmation line that shows the exact path to the generated workbook.

`run_extractor.py` sets up an isolated `.venv`, installs/updates the dependencies when `requirements.txt` changes, and launches the CLI. You do not need to manage Python packages manually.

---

### Direct CLI (Advanced / Existing Environments)

`fetch_api_params.py` remains fully supported. If you already manage dependencies yourself (for example, inside an existing virtual environment or CI job), run:

```bash
pip install -r requirements.txt
python fetch_api_params.py
```

This bypasses the helper `.venv` that `run_extractor.py` creates while keeping identical functionality.

---

Interactive flow recap:

1. **Provider** – `aws`, `gcp`, or `azure`.
2. **Service** – type the identifier; use `L` to list available services. When prompted, include related AWS service variants or pick specific GCP versions as needed (each selection generates its own worksheet).
3. **Output file** – accept `<csp>-<service>-api-extract.xlsx` or provide a custom name (the `.xlsx` extension is added if missing).
4. **Destination** – press Enter to save inside `OUTPUT_FILES/`, or choose “no” to enter a custom directory or full path.
5. The script prints the absolute path to your Excel file once extraction finishes. Re-running automatically refreshes the cached service catalog whenever a newer list is available.

---

### Troubleshooting

- **“Unable to create default output directory”** – verify you have write permission to the project folder. Running the terminal as an administrator (Windows) or saving to another directory usually fixes it.
- **“Unable to write to `<file>.xlsx`”** – Excel (or another app) might have the file open. Close it and rerun.
- **Network errors when refreshing services** – the tool falls back to the cached/bundled list and prints a warning. Re-run when you’re back online to refresh.
- **“Service '<name>' not found”** – make sure you used the provider’s canonical service name. Use the `L` shortcut to copy-paste an exact identifier.
- **Unexpected crash/stack trace** – rerun via `python run_extractor.py` so dependencies are installed in a clean `.venv`. If the problem persists, re-run with `L` to confirm the service exists, then share the console output when reporting the issue.

---

### Excel Output Details

| Provider | Columns | Notes |
| --- | --- | --- |
| AWS | `<service> API Action`, `Level 1..N` | Each worksheet covers a single AWS service or variant (for example, `sagemaker-runtime`), and every action’s request tree is indented beneath it. |
| GCP | `<service> REST Resource`, `API Method`, `Level 1..N` | Each worksheet corresponds to one GCP API version (v1, beta, etc.); resources group their methods and parameter trees. |
| Azure | `<service> Resource Operation`, `API Method`, `Level 1..N` | Same layout as GCP but tailored for Azure terminology. |

- `Level` columns expand dynamically beyond Level 5 to accommodate deeply nested schemas.
- Required parameters include `(required)` in their label.
- Map/dictionary parameters expand into nested Key/Value rows so even complex SageMaker bodies remain readable.
- Each worksheet is named after the chosen service/variant (sanitized to Excel’s length limits) and row 1 is frozen for easy scrolling.

---

### Service Catalog Refresh Logic

1. The CLI loads `service_catalog_cache.json` if present.
2. It attempts a live refresh for the chosen provider. When successful, it:
   - Prints how many services were added or removed.
   - Writes the updated list back to the cache.
3. If live refresh fails (e.g., offline), the cached or bundled list is used, and the script warns you accordingly.

---

### Extending

- **Azure OpenAPI tweaks** – update `extractors/azure_extractor.py` if you want to choose different tags/input files or cache the downloaded Swagger documents locally.
- **GCP rate limits** – if you hit API quotas, consider caching Discovery documents locally.
- **Excel formatting** – adjust `writer/excel_writer.py` to add styling, filters, or alternate sheet layouts.
- **Additional logging** – wrap extractor calls in try/except blocks (in `fetch_api_params.py`) and add logging if you need finer-grained diagnostics.

---

### License

Add your preferred license here (MIT, Apache 2.0, proprietary, etc.).
