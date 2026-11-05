# Why `STG-CUSTOMER-REF` Is Blocked

**Checked:** 2026-11-05
**Latest validation run reviewed:** 2026-11-05 08:55:55 UTC

## Short answer

`STG-CUSTOMER-REF` is blocked because the approved rule for matching sales
customer IDs to Customer Master records has not been confirmed. The validator
does not assume that equal-looking IDs—or a plausible alternative key—are the
approved business mapping.

The current config does not set `customer_json.reference_mapping_verified` to
`true`. The validator therefore reports `BLOCKED`, not `PASS` or `FAIL`. The
option is documented in [`config/config.example.json`](config/config.example.json).

## Evidence reviewed

The available input files are:

- `dim_Distributor_sales_50k.json`, with a `customer_id` and `policy_number`.
- `dim_Customer_Master_50k.txt`, with a `customer_id`, `customer_key`, and
  `policy_number`.
- `Fact_Sales_50k_CSV.csv`, with a `customer_key` and `policy_number`.

The lab's ETL SQL script,
`C:\qa-lab\python-project-2\admin\03_load_datamart.sql`, documents an intended
join from distributor sales to Customer Master on `customer_id` and selects
the corresponding `customer_key`. The join is in the script's final
`LEFT JOIN dim_Customer_Master d2 ON d1.customer_id = d2.customer_id`.

However, a read-only comparison of the supplied input files found:

- **0 distinct nonblank sales `customer_id` values** shared with the Customer
  Master `customer_id` values.
- **50,000 distinct sales policy numbers** shared with Customer Master policy
  numbers.
- Customer Master has **50,000 rows but 48,729 distinct customer IDs**; 1,254
  IDs are associated with multiple customer keys. The SQL schema declares
  `customer_key` as the primary key and `policy_number` unique, but does not
  declare `customer_id` unique.

The latest run's direct-ID comparison consequently found **48,461 unresolved
sales rows across 44,753 distinct nonblank IDs**. Those values describe the
direct comparison only. They do not prove that the records are invalid if the
authoritative mapping is different.

## Why matching on policy is not assumed

Policy number is a possible join candidate based on the observed overlap and
the SQL schema's unique policy constraint. But the ETL script explicitly uses
`customer_id` for this relationship, and no separate approved crosswalk,
mapping specification, or instruction authorizing policy-based customer
resolution was found in the repository or lab project files. Changing the
business join to policy number without owner confirmation would be an
unsupported assumption.

## What is needed to unblock the check

Ask the data owner or assignment mentor to confirm:

1. The authoritative sales-to-customer matching rule (for example, whether
   `customer_id` should match directly, whether a crosswalk exists, or whether
   policy number is approved for the relationship).
2. Whether the reference is expected to resolve to an active customer.
3. How duplicate `customer_id` values should be handled when they map to
   multiple `customer_key` values.

Once that rule is documented, configure the approved mapping and set
`customer_json.reference_mapping_verified` to `true`; then rerun the validation.
With that flag enabled, unresolved rows are reported as `FAIL`. Do not enable it
merely to turn the blocked result into a pass.

## Implementation and evidence locations

- [`src/customer_validator.py`](src/customer_validator.py) — reference-check
  status and exploratory unresolved-row/distinct-ID counts.
- [`config/config.example.json`](config/config.example.json) — mapping
  verification defaults to false.
- [`submission3_upload/VALIDATION_EXECUTION_REPORT.csv`](submission3_upload/VALIDATION_EXECUTION_REPORT.csv) —
  sanitized latest-run check result.
- [`submission3_upload/EXECUTION_LOG.txt`](submission3_upload/EXECUTION_LOG.txt) —
  sanitized latest-run execution evidence.

The sales and customer input datasets are sensitive and are not included in the
submission package.
