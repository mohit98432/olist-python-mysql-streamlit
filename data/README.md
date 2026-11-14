# Data policy

The dashboard reads current rows directly from MySQL. Raw extracts are deliberately not committed. `.gitignore` excludes local CSV and Parquet files so database data stays on the user's machine unless they intentionally choose to publish it.
