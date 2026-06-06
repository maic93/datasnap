# datasnap

> Instant data profiling for CSV and JSON files — from the terminal.

```
$ datasnap sales.csv

╭─ sales.csv  10,000 rows × 8 columns ─╮
│                                       │
│  column       type   missing%  stats  │
│  ──────────────────────────────────── │
│  id           numeric    0%    ...    │
│  revenue      numeric    1.2%  ...    │
│  category     cat        0%    ...    │
│  ...                                  │
╰───────────────────────────────────────╯

Quality score: 87/100
  Duplicate rows: 3 (0.03%)
  Outliers in revenue: 12 rows (0.12%)
```

## Install

```bash
pip install datasnap
```

Or from source:

```bash
git clone https://github.com/yourname/datasnap
cd datasnap
pip install -e ".[dev]"
```

## Usage

```bash
# Profile a CSV
datasnap data.csv

# Show terminal charts
datasnap data.csv --plot

# Save report
datasnap data.csv --output report.json
datasnap data.csv --output report.md

# Compare two files (coming week 6)
datasnap before.csv after.csv --diff

# Skip quality checks
datasnap data.csv --no-quality
```

## Features

- **Summary stats** — mean, std, min/max, quartiles, value counts
- **Missing value report** — per-column counts and percentages
- **Data quality score** — 0–100 composite metric
- **Outlier detection** — IQR-based flagging
- **Duplicate detection** — exact row duplicates
- **Export reports** — JSON, Markdown (HTML coming week 5)
- **Terminal charts** — histograms and bar charts via plotext

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check datasnap/
```

## Roadmap

- [x] Week 1: Project skeleton & CLI
- [x] Week 2: Summary statistics
- [x] Week 3: Data quality checks
- [ ] Week 4: Terminal charts
- [ ] Week 5: HTML/Markdown export
- [ ] Week 6: File diff / comparison
- [ ] Week 7: Test coverage + CI
- [ ] Week 8: PyPI release

## License

MIT
