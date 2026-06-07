# datasnap

> Instant data profiling for CSV and JSON files — from the terminal.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-in%20development-orange)

```
$ datasnap sales.csv

 sales.csv  10,000 rows × 6 columns  missing overall: 1.2%

 column        type         non-null  missing%  summary
 ──────────────────────────────────────────────────────────────
 id            numeric       10000       0.0%   mean=5000 min=1 max=10000
 revenue       numeric        9876       1.2%   mean=4823 min=10 max=99999
 category      categorical   10000       0.0%   5 unique — Electronics, Tools, ...
 joined_date   categorical   10000       0.0%   ...

 Quality score: 87/100
   Duplicate rows : 3 (0.03%)
   Outliers in revenue: 12 rows (0.12%)
```

## Install

```bash
pip install datasnap
```

Or from source:

```bash
git clone https://github.com/maic93/datasnap
cd datasnap
pip install -e ".[dev]"
```

## Usage

```bash
# Profile a CSV
datasnap data.csv

# Profile a JSON file
datasnap data.json

# Show terminal charts
datasnap data.csv --plot

# Save report
datasnap data.csv --output report.json
datasnap data.csv --output report.md

# Skip quality checks
datasnap data.csv --no-quality
```

## Features

- Summary stats — mean, std, min/max, quartiles, value counts
- Missing value report — per-column counts and percentages
- Data quality score — 0–100 composite metric
- Outlier detection — IQR-based flagging
- Duplicate detection — exact row duplicates
- Export reports — JSON and Markdown
- Terminal charts — histograms and bar charts (coming Day 11)

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check datasnap/
```

## Roadmap

- [x] Day 1: Project scaffold
- [x] Day 2: CLI entry point
- [ ] Day 3–14: See CLAUDE.md

## License

MIT
