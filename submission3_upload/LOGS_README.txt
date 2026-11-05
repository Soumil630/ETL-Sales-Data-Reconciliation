Execution log provenance
========================

EXECUTION_LOG.txt is a sanitized transcription of the latest workspace run.
It is correlated with the reports generated at 2026-11-05 08:55:55 UTC by the
matching run start, report-write entry, validation IDs/statuses, and final exit code.

The configured source files loaded successfully (50000 sales rows and 50000
customer-master records). The configured read-only target query succeeded and
returned 45076 rows. The runner generated the detailed CSV, reconciliation CSV,
and HTML summary. It exited with code 1 because validation checks failed and one
check was blocked; report generation itself succeeded.

The shared log omits credentials, record keys, compared source/target values, and
absolute configuration/input paths. The detailed local reports may contain
business identifiers and compared values; do not upload those raw files.
output/demo/execution.log contains synthetic records and is not included.
