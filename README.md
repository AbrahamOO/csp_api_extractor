## CSP API Extractor

Collects API shapes from AWS, GCP, and Azure services and exports a tree of operations/methods and request parameters into a structured Excel workbook. The tool automates service discovery, prompts for the cloud/service you want to inspect, and produces provider-specific spreadsheet layouts that make it easy to audit available APIs.

---

### Key Features

- **Live service catalogs** – pulls the latest AWS service list via Botocore, the public GCP Discovery directory, and the Azure REST spec repo. Results are cached in `service_catalog_cache.json` for offline reuse.
- **Provider-specific extractors**
  - *AWS*: loads the Botocore `service-2` models to enumerate every API action and its request shape.
  - *GCP*: walks the Discovery document for the chosen service, covering top-level and nested REST resources.
  - *Azure*: placeholder sample tree (can be swapped with a real OpenAPI parser later).
- **Excel writer tailored per CSP**
  - AWS sheets show `<service> API Action` followed by hierarchical parameter levels.
  - GCP sheets show `<service> REST Resource`, `API Method`, and parameter levels.
  - Azure sheets show `<service> Resource Operation`, `API Method`, and parameter levels.
  - Required fields are annotated with `(required)` and the header row is frozen for easier scanning.
- **Guided CLI workflow** – prompts for provider/service (with an `L` shortcut to list services in a padded table), pre-fills a default filename (`<csp>-<service>-api-extract.xlsx`), and offers to save into the local `OUTPUT_FILES` directory.

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

### Prerequisites

1. Python 3.8+ (project developed/tested with 3.8).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. AWS extractor needs access to Botocore models (bundled with the installed package). No AWS credentials are required because it only inspects the local service descriptions.

---

### Usage

```bash
python fetch_api_params.py
```

Interactive flow:

1. **Provider** – enter `aws`, `gcp`, or `azure`.
2. **Service** – type the service identifier (use `L`/`l` to print the available services in a table).
3. **Output file** – accept the suggested `<csp>-<service>-api-extract.xlsx` by pressing Enter/yes or supply a custom name.
4. **Destination** – press Enter/yes to save into `OUTPUT_FILES/`, or choose “no” to provide a full path.
5. Wait for extraction; the script prints the resolved file path once complete.

Tip: reruns automatically merge any newly discovered services into `service_catalog_cache.json`.

---

### Excel Output Details

| Provider | Columns | Notes |
| --- | --- | --- |
| AWS | `<service> API Action`, `Level 1..N` | Each action appears once; its parameter tree fills the Level columns with blank action cells on child rows. |
| GCP | `<service> REST Resource`, `API Method`, `Level 1..N` | Resources group their methods, and method rows expand with parameter trees. |
| Azure | `<service> Resource Operation`, `API Method`, `Level 1..N` | Same layout as GCP but tailored for Azure terminology. |

- `Level` columns expand dynamically beyond Level 5 to accommodate deeply nested schemas.
- Required parameters include `(required)` in their label.
- The workbook tab is named “API Methods” and row 1 is frozen.

---

### Service Catalog Refresh Logic

1. The CLI loads `service_catalog_cache.json` if present.
2. It attempts a live refresh for the chosen provider. When successful, it:
   - Prints how many services were added or removed.
   - Writes the updated list back to the cache.
3. If live refresh fails (e.g., offline), the cached or bundled list is used, and the script warns you accordingly.

---

### Extending or Troubleshooting

- **Azure extractor** is currently a stub. Replace `extractors/azure_extractor.py` with logic that downloads and parses the official OpenAPI specs for production use.
- **GCP rate limits** – if you hit API quotas, consider caching Discovery documents locally.
- **Excel formatting tweaks** – adjust `writer/excel_writer.py` to add styling, filters, or alternate sheet layouts.
- **Debug logs** – wrap extractor calls in try/except blocks (in `fetch_api_params.py`) and add logging if you need finer-grained error reporting.

---

### License

Add your preferred license here (MIT, Apache 2.0, proprietary, etc.).
