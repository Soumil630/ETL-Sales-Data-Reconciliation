# Submission 3: Latest Validation Execution and QA Findings

**Prepared:** 2026-11-05
**Latest execution:** 2026-11-05 08:55:55 UTC
**Assessment:** Current source-to-staging and staging-to-mart checks were executed. This is not a full pipeline sign-off; aggregate and reporting layers remain untested.

## Execution summary

The latest run used the configured 50,000-row distributor sales file, 50,000-row customer master, and read-only MySQL customer-360 mart query. The target read succeeded and returned 45,076 rows. The process exited with code 1 because the run contains failed checks; report generation completed.

| Outcome | Result rows | Distinct validation IDs |
|---|---:|---:|
| PASS | 13 | 13 |
| FAIL | 40,580 | 6 |
| BLOCKED | 1 | 1 |

Result rows include one record for each field mismatch: 40,575 customer-PAN mismatches account for most FAIL rows. The distinct-ID count describes check types, not individual records. See [QA_SUMMARY.html](./QA_SUMMARY.html) for the grouped current-run summary and [VALIDATION_EXECUTION_REPORT.csv](./VALIDATION_EXECUTION_REPORT.csv) for sanitized check-level counts.

## Current findings

1. **Required sales values:** 1,539 sales rows have a blank `customer_id`; this check fails.
2. **Customer master uniqueness:** 2,525 customer-master rows participate in duplicate `customer_id` values; this check fails. Confirm the business-key rule before deduplication.
3. **Customer reference integrity — blocked:** direct ID comparison indicates 48,461 unresolved sales rows representing 44,753 distinct IDs. The source-to-master mapping is not confirmed, so these counts are exploratory and are not reported as a verified defect. The [`WHY_STG_CUSTOMER_REF_IS_BLOCKED.md`](./WHY_STG_CUSTOMER_REF_IS_BLOCKED.md) analysis records the ETL join evidence and questions for the data owner. Confirm the approved mapping before rerunning this check as PASS/FAIL.
4. **Mart completeness:** 4,924 source transaction keys are absent from the 45,076-row target; no extra target keys were found. The row-count and missing-key checks fail.
5. **Customer PAN comparison:** 40,575 matched transaction rows differ on `customer_pan`; the mismatch details are withheld from this upload. Confirm the approved transformation, masking, and target-field rules before treating this as a defect.
6. **Other source checks:** configured schema, transaction uniqueness, numeric amounts, dates, mandatory customer fields, and policy references passed.

Defect dispositions and evidence references are in [DEFECT_LOG.csv](./DEFECT_LOG.csv). Severity and business impact remain provisional pending data-owner review.

## Scope and limitations

- The customer-ID reference check is blocked until an approved mapping is documented. The submitted result distinguishes unresolved rows from distinct unresolved IDs and does not present direct string comparison as a confirmed defect.
- The mart comparisons use the current configured source, target, key, and direct-field mappings. Confirm business scope and customer-PAN rules before disposition.
- Aggregate-model, Retail CSV, Online API, and reporting/dashboard checks were not run because their required sources/specifications or accessible environment were not available.
- The package contains sanitized summaries only. It excludes raw validation details, row-level identifiers and compared values, source datasets, credentials, and synthetic demo output.
- The validation process exit code is 1 because data checks failed or were blocked; this does not mean report generation failed.

## Upload checklist

- [x] Latest run summary, sanitized check-level results, grouped HTML summary, coverage matrix, defect log, evidence index, and correlated sanitized execution log included.
- [x] ZIP rebuilt from the current `submission3_upload` folder.
- [ ] Upload `submission3_upload.zip` (or its contents) through the submission portal and verify mentor access.
- [ ] Obtain data-owner confirmation of customer-ID mapping, duplicate-key rules, and PAN handling; rerun affected checks after confirmation.
- [ ] Obtain requirements and evidence for aggregate-model and reporting/dashboard layers, or written confirmation that they are out of scope.

This package is current execution evidence, not release approval or full multi-layer assignment completion.

## Package contents

- [VALIDATION_EXECUTION_REPORT.csv](./VALIDATION_EXECUTION_REPORT.csv) — sanitized latest-run counts by validation ID.
- [WHY_STG_CUSTOMER_REF_IS_BLOCKED.md](./WHY_STG_CUSTOMER_REF_IS_BLOCKED.md) — investigation of the customer-reference mapping block and supporting evidence.
- [QA_SUMMARY.html](./QA_SUMMARY.html) — latest generated grouped report.
- [LAYER_COVERAGE.csv](./LAYER_COVERAGE.csv) — executed and untested layers.
- [DEFECT_LOG.csv](./DEFECT_LOG.csv) — findings with current evidence and disposition.
- [EVIDENCE_INDEX.csv](./EVIDENCE_INDEX.csv) — sources, timestamps, coverage, and handling notes.
- [EXECUTION_LOG.txt](./EXECUTION_LOG.txt) and [LOGS_README.txt](./LOGS_README.txt) — correlated sanitized execution evidence.
- [SOURCE_DOCUMENT_INDEX.csv](./SOURCE_DOCUMENT_INDEX.csv), [CODE_REPOSITORY_LINK.txt](./CODE_REPOSITORY_LINK.txt), and [UPLOAD_CHECKLIST.txt](./UPLOAD_CHECKLIST.txt) — assignment/source and submission references.
