# datasnap

> Instant data profiling for CSV and JSON files — straight from the terminal.

[![CI](https://github.com/maic93/datasnap/actions/workflows/ci.yml/badge.svg)](https://github.com/maic93/datasnap/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-0.1.0-blueviolet)

`datasnap` profiles any CSV, TSV, JSON, or JSONL file in seconds — no notebook,
no boilerplate pandas code. Point it at a file and get row/column counts,
per-column statistics, a missing-value breakdown, duplicate and outlier
detection, a 0–100 quality score, and optional terminal charts.

```
$ datasnap sales.csv --plot

 sales.csv  10,000 rows × 6 columns  missing overall: 1.2%

 #  column        type         non-null  missing%  summary
 ────────────────────────────────────────────────────────────────────────
 1  id            numeric       10000       0%      mean=5000  min=1  max=10000
 2  revenue       numeric        9876       1%      mean=4823  min=10  max=99999
 3  category      categorical   10000       0%      5 unique  top: Electronics (61.0%)
 4  joined_date   datetime      10000       0%      2019-01-01 → 2024-12-31

  Missing values: 1 column has missing data (worst: 'revenue' at 1.2%)

╭──────────────────────────────────────────╮
│ Quality score: 87/100 (B)                 │
│   Duplicate rows : 3 (0.03%)               │
│   Outliers in revenue: 12 rows (0.12%)     │
│                                            │
│   Breakdown:                              │
│     completeness    37.6/40               │
│     uniqueness       24.9/25              │
│     consistency      19.9/20              │
│     validity         15.0/15              │
╰──────────────────────────────────────────╯

[histogram and bar charts render here with --plot]
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
# Profile any supported file
datasnap data.csv
datasnap data.tsv
datasnap data.json
datasnap data.jsonl

# Show terminal charts (histograms + bar charts)
datasnap data.csv --plot

# Save a report to disk
datasnap data.csv --output report.json
datasnap data.csv --output report.md

# Skip the quality/duplicate/outlier checks
datasnap data.csv --no-quality

# Profile multiple files in one command
datasnap jan.csv feb.csv mar.csv

# Compare two files (schema + row diff)
datasnap before.csv after.csv --diff
```

## Features

**Loaders** — CSV, TSV, JSON, and JSONL with automatic encoding (utf-8, latin-1,
cp1252) and delimiter detection (comma, semicolon, tab, pipe). Handles nested
JSON structures and newline-delimited JSON transparently.

**Column type inference** — classifies every column as numeric, categorical,
boolean, or datetime, including low-cardinality integer columns that are
really categorical IDs.

**Numeric stats** — mean, std, variance, min, max, range, quartiles, IQR,
skewness, and kurtosis for every numeric column.

**Categorical stats** — unique count, mode, top-N value counts with
percentages, least-common values, and cardinality ratio.

**Missing value report** — per-column missing count and percentage with a
five-level severity scale (none → critical), sorted worst-first.

**Duplicate detection** — exact row duplicates with severity scoring, grouped
duplicate detection, and optional column-subset matching.

**Outlier detection** — IQR and Z-score methods with configurable thresholds,
returning bounds, affected row indices, and min/max outlier values.

**Quality score** — a 0–100 score broken into four weighted dimensions
(completeness, uniqueness, consistency, validity) with a letter grade (A–F).

**Terminal charts** — histograms for numeric columns and bar charts for
categorical columns, rendered directly in the terminal via `plotext`.

**Report export** — save the full profile as JSON (machine-readable) or
Markdown (for READMEs, PRs, or documentation).

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check datasnap/
```

The test suite covers loaders, type inference, numeric and categorical stats,
missing value analysis, duplicate and outlier detection, the quality score,
report export, terminal charts, the CLI itself, and a battery of edge cases
(empty data, unicode, single rows, all-missing columns, and more).

## Project structure

```
datasnap/
├── datasnap/
│   ├── cli.py            CLI entry point (argparse)
│   ├── loaders/          CSV / TSV / JSON / JSONL loading
│   ├── stats/            type inference, numeric & categorical stats, missing values
│   ├── quality/          duplicates, outliers, quality score
│   ├── charts/           terminal histograms and bar charts
│   └── reports/          rich terminal output, JSON/Markdown export
├── tests/                pytest suite + fixtures
├── .github/workflows/    CI (Python 3.9 / 3.11 / 3.12)
├── DEVLOG.md             daily build log
└── pyproject.toml
```

## Roadmap

This project was built in 14 days, one feature per day, with a daily commit.

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
| 10 | Jun 15 | Outlier detection (IQR) + quality score 0–100 | ✅ |
| 11 | Jun 16 | Terminal charts: histogram + bar chart with plotext | ✅ |
| 12 | Jun 17 | Export report to JSON and Markdown (--output flag) | ✅ |
| 13 | Jun 18 | Full pytest suite — CLI integration + edge case coverage | ✅ |
| 14 | Jun 19 | README rewrite, badges, tag v0.1.0 | ✅ |

See [DEVLOG.md](DEVLOG.md) for the day-by-day build notes.

## Contributing

Issues and pull requests are welcome. Please run `pytest` and `ruff check
datasnap/` before submitting a PR.

## License

MIT
