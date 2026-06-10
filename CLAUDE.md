# datasnap — Claude Code instructions

## What this project is
`datasnap` is a Python CLI tool for instant data profiling of CSV and JSON files.
Users run `datasnap myfile.csv` and get stats, quality checks, and charts in the terminal.

## How to find today's task
1. Read `DEVLOG.md` to see the last completed day
2. Find the next unchecked `[ ]` task in the roadmap below
3. Implement it, write/update tests, update DEVLOG.md, mark `[x]`, then commit

## 14-day roadmap (Jun 6 – Jun 19)

### Week 1 — Foundation & core stats
- [x] Day 1  Jun 6  Fri — Init repo, pyproject.toml, full folder structure
- [x] Day 2  Jun 7  Sat — CLI entry point with argparse, --help output
- [x] Day 3  Jun 8  Sun — CSV loader with pandas, basic validation
- [x] Day 4  Jun 9  Mon — JSON + JSONL loader, unified file-type detection
- [x] Day 5  Jun 10 Tue — Column type inference (numeric / categorical / datetime)
- [ ] Day 6  Jun 11 Wed — Numeric stats: mean, std, min, max, quartiles
- [ ] Day 7  Jun 12 Thu — Categorical stats: value counts, top-N, unique count

### Week 2 — Quality, charts & export
- [ ] Day 8  Jun 13 Fri — Missing value report with % per column + rich table output
- [ ] Day 9  Jun 14 Sat — Duplicate row detection and report
- [ ] Day 10 Jun 15 Sun — Outlier detection via IQR + quality score (0–100)
- [ ] Day 11 Jun 16 Mon — Terminal charts: histogram + bar chart with plotext
- [ ] Day 12 Jun 17 Tue — Export report to JSON and Markdown with --output flag
- [ ] Day 13 Jun 18 Wed — pytest suite: full test coverage for all modules
- [ ] Day 14 Jun 19 Thu — README rewrite, badges, usage GIF placeholder, tag v0.1.0

## How to implement each task
1. Read existing code in `datasnap/` before writing anything
2. Write the code for today's task
3. Add or update tests in `tests/`
4. Run `pytest` — fix failures before committing
5. Update `DEVLOG.md` with today's date and a one-line description
6. Mark the task `[x]` in this file
7. Commit and push:
   ```bash
   git add .
   git commit -m "feat: <short description>"
   git push
   ```

## Code style
- Python 3.9+ compatible, type hints on all functions
- Docstrings on all public functions
- Max line length: 88 (ruff default)
- Use `rich` Console for all output — no bare `print()`
- All new modules need an `__init__.py` export

## Project structure
```
datasnap/
├── datasnap/
│   ├── cli.py            ← argparse entry point
│   ├── loaders/          ← CSV + JSON loading
│   ├── stats/            ← summary statistics
│   ├── quality/          ← data quality checks
│   ├── charts/           ← terminal charts (Day 11)
│   └── reports/          ← terminal output + export
├── tests/
│   └── fixtures/         ← sample.csv, sample.json
├── DEVLOG.md
├── CLAUDE.md
└── pyproject.toml
```

## Running locally
```bash
pip install -e ".[dev]"
datasnap tests/fixtures/sample.csv
pytest
```

## Commit message format
```
feat: add IQR outlier detection
fix: handle empty CSV files gracefully
test: add missing value edge case fixtures
docs: update README with --plot example
refactor: split summary into numeric and categorical modules
```

## Rules for Claude Code
- Always run `pytest` before committing — never commit broken tests
- Keep each day's change small and focused — one feature at a time
- If code for a task already exists, extend it rather than rewrite
- Write more tests rather than more code when in doubt
