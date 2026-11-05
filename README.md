# Assignment 2: Sales Data QA Automation

The submission requirements extracted from the local PDFs are summarized in [assignment2_reference.md](assignment2_reference.md). The detailed test inventory is [test_cases.csv](test_cases.csv).

The implementation follows the requested modular layout: `src/` contains the file reader, sales/customer validators, database connector, reconciliation, business rules, report generator, and pipeline entry point. The six focused test modules are in `tests/`.

## Environment

Python 3.10+. From PowerShell at this repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run against the discovered lab files

Copy `config/config.example.json` to the ignored runtime file `config/config.json`. It points to read-only lab inputs under `C:\qa-lab\python-project-2\input` and the verified `dm_distributor_sales_customer_360` MySQL table:

- `dim_Distributor_sales_50k.json`
- `dim_Customer_Master_50k.txt` (comma-delimited despite its extension)
- `Fact_Sales_50k_CSV.csv`

Do not copy the input datasets into the repository; `data/README.md` explains the data-handling rule. To use the runner without entering credentials each time, put your lab username and password in the `database.user` and `database.password` fields in your local `config/config.json`. The runner prefers the configured environment variables (`P2_DB_USER` and `P2_DB_PASSWORD`) when set, then falls back to those config fields. The example config has empty values; never replace them with real credentials in the tracked example file.

```powershell
if (-not (Test-Path .\config\config.json)) {
    Copy-Item .\config\config.example.json .\config\config.json
}
notepad .\config\config.json
```

Save your lab username and password in the `user` and `password` fields. The runtime config is excluded by `.gitignore`, but a password in it is still stored as plaintext on disk: use this only on a private, access-controlled machine, never commit/share/upload the file, and prefer the environment-variable prompt below when possible.

Run the validation directly with the default config:

```powershell
python run_validation.py
```

Alternatively, enter credentials through a non-echoing SecureString prompt for one run and clear the environment variables afterward:

```powershell
$securePassword = Read-Host 'Database password' -AsSecureString
$passwordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
try {
	$env:P2_DB_USER = Read-Host 'Database user'
	$env:P2_DB_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
	python run_validation.py --config config/config.json
}
finally {
	Remove-Item Env:P2_DB_USER, Env:P2_DB_PASSWORD -ErrorAction SilentlyContinue
	[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
	$securePassword.Dispose()
}
```

Each run writes `reports/validation_results.csv`, `reports/reconciliation_report.csv`, `reports/qa_summary.html`, and appends to `logs/execution.log`. The execution log includes run boundaries, a grouped result line for each validation ID/status, totals, report paths, and the process exit code. It intentionally excludes row keys and compared field values. The CSV reports can contain row-level identifiers and values; keep them private and review/sanitize before sharing. The process exits `0` when no checks fail or block, `1` when checks fail or block, and `2` when the run cannot start. A nonzero exit code does not mean report generation failed: inspect the reports and log. The runner issues a configured read-only `SELECT`; it does not modify the database. Do not put passwords in config or reports. `sample_execution.txt` contains a historical sanitized summary, not evidence from a new run.

Customer-reference validation defaults to `BLOCKED` unless `customer_json.reference_mapping_verified` is explicitly set to `true` after the approved sales-to-master ID mapping is documented. When blocked, the report shows direct-equality unresolved row and distinct-ID counts as exploratory evidence, not as a confirmed defect. The HTML report distinguishes result rows (which can include many row-level field mismatches) from distinct validation IDs.

## Run tests and demo

```powershell
python -m pytest -q
python demo_run.py
```

The demo uses fabricated records and deliberately includes defects. Its output is explicitly labeled synthetic; do not submit it as lab execution evidence. The latest local MySQL execution evidence is in `reports/` and the sanitized `submission3_upload/` package. `sample_execution.txt` is a historical summary only.

## PDF text extraction

```powershell
python extract_pdf_text.py . --output-dir extracted_pdf_text
```

The Quick Start PDF contains credentials. Keep extracted files private; do not commit or share them.

## Current findings and limits

The latest verified run (2026-11-05 08:55:55 UTC) loaded 50,000 sales rows and 50,000 customer-master records; the live mart returned 45,076 rows. Reconciliation found 4,924 source transactions missing, no extra mart keys, and 40,575 customer-PAN mismatches among matched records. The other configured direct-field comparisons matched.

The current run finds 1,539 blank distributor `customer_id` values and 2,525 Customer Master rows participating in duplicate IDs. Policy references resolve. Direct customer-ID comparison suggests 48,461 unresolved sales rows across 44,753 unique IDs, but the approved identifier mapping is unconfirmed; that check is BLOCKED, not a confirmed failure. Confirm the mapping and key semantics with the data owner before disposition.

See [WHY_STG_CUSTOMER_REF_IS_BLOCKED.md](WHY_STG_CUSTOMER_REF_IS_BLOCKED.md) for the investigated ETL join, observed identifier overlap, and what is needed to unblock the customer-reference check.

The input folder does not include product/distributor/region dimension tables or the dashboard specification. Derived measures, aggregate rules, and dashboard tests remain blocked until mappings and reporting extracts are provided. `test_cases.csv` records these limits. The PDFs differ from the actual input formats; this config follows the verified lab files and live mart schema.
