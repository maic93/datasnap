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
