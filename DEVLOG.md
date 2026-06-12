# devlog

Daily progress journal for `datasnap`.

---

## Week 1

### Day 1 — Jun 6
- Initialised repo and full project structure
- Added `pyproject.toml` with all dependencies
- Created folder skeleton: loaders, stats, quality, charts, reports
- Added sample CSV and JSON fixtures

### Day 2 — Jun 7
- Verified CLI entry point works (`datasnap --help`)
- `datasnap tests/fixtures/sample.csv` runs cleanly
- Installed package with `pip install -e .`

### Day 3 — Jun 8
- Rewrote CSV loader with encoding auto-detection (utf-8, latin-1, cp1252)
- Added delimiter auto-detection (comma, semicolon, tab, pipe)
- Added file validation: empty file and no-column guards
- Fixed `rich` lazy imports to stop CI failures
- Fixed GitHub Actions CI workflow to install deps explicitly
- All tests passing

---

_Add one entry every day before committing._

### Day 4 — Jun 9
- Rewrote JSON loader with multi-strategy parsing (array, nested, flat dict)
- Added JSONL support (newline-delimited JSON)
- Added TSV support to detect.py (tab-separated files)
- Added FileNotFoundError to detect.py
- Added nested.json, sample.jsonl, sample.tsv fixtures
- Expanded test suite: 14 tests across CSV, TSV, JSON, JSONL

### Day 5 — Jun 10
- Created `datasnap/stats/inference.py` — column type inference engine
- Detects: numeric, categorical, boolean, datetime, unknown
- Handles string/object dtype difference in newer pandas versions
- Low-cardinality integer columns correctly typed as categorical
- Boolean detection: True/False, yes/no, 1/0, y/n
- Datetime detection via regex patterns + pandas fallback parser
- Added `infer_all_columns()` and `columns_by_type()` helpers
- Wired inference into `summary.py` replacing old `_infer_type()`
- Added 14 new tests in `tests/test_inference.py`

### Day 6 — Jun 11
- Created `datasnap/stats/numeric.py` — dedicated numeric stats module
- Stats: count, mean, std, variance, min, max, range, q1, median, q3, iqr, skewness, kurtosis
- Added `numeric_stats_all()` to compute stats for all numeric cols in a DataFrame
- Added `summarise_numeric()` for one-line human-readable summary
- Updated `summary.py` to use new numeric module + added summary string per column
- Added datetime summary formatting (date range)
- 15 new tests in `tests/test_numeric.py`

### Day 7 — Jun 12
- Created `datasnap/stats/categorical.py` — dedicated categorical stats module
- Stats: count, unique, mode, mode_count, mode_pct, top_values, least_common, cardinality_ratio
- Added `categorical_stats_all()` for all categorical/boolean columns in a DataFrame
- Added `summarise_categorical()` for one-line human-readable summary
- Added `value_counts_table()` for sorted frequency table with percentages
- Updated `summary.py` to use new categorical module
- 19 new tests in `tests/test_categorical.py`
- Fixed README Day 4 checkbox (was missing ✅)
