# datasnap

> Instant data profiling for CSV and JSON files — from the terminal.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-in%20development-orange)

```
$ datasnap sales.csv

 sales.csv  10,000 rows × 6 columns  missing overall: 1.2%

 column        type         non-null  missing%  summary
 ─────────────────────────────────────────────────────────────
 id            numeric       10000       0.0%   mean=5000 min=1 max=10000
 revenue       numeric        9876       1.2%   mean=4823 min=10 max=99999
 category      categorical   10000       0.0%   5 unique — Electronics, Tools ...
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
- Terminal charts — histograms and bar charts *(coming Day 11)*

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check datasnap/
```

## 14-day Roadmap

| Day | Date   | Task | Status |
|-----|--------|------|--------|
| 1  | Jun 6  | Project scaffold — pyproject.toml, folder structure | ✅ |
| 2  | Jun 7  | CLI entry point with argparse, --help output | ✅ |
| 3  | Jun 8  | CSV loader — encoding detection, delimiter sniffing | ✅ |
| 4  | Jun 9  | JSON + JSONL loader, unified file-type detection | ✅ |
| 5  | Jun 10 | Column type inference (numeric / categorical / datetime) | ✅ |
| 6  | Jun 11 | Numeric stats: mean, std, min, max, quartiles | ✅ |
| 7  | Jun 12 | Categorical stats: value counts, top-N, unique count | ✅ |
| 8  | Jun 13 | Missing value report with % per column + rich table | ✅ |
| 9  | Jun 14 | Duplicate row detection and report | ✅ |
| 10 | Jun 15 | Outlier detection (IQR) + quality score 0–100 | ⬜ |
| 11 | Jun 16 | Terminal charts: histogram + bar chart with plotext | ⬜ |
| 12 | Jun 17 | Export report to JSON and Markdown (--output flag) | ⬜ |
| 13 | Jun 18 | Full pytest suite — coverage for all modules | ⬜ |
| 14 | Jun 19 | README rewrite, badges, tag v0.1.0 | ⬜ |

## License

MIT
