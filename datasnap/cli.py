"""datasnap CLI — instant data profiling from the terminal."""

import argparse
import sys
from pathlib import Path

from datasnap import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="datasnap",
        description="Instant data profiling for CSV and JSON files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  datasnap data.csv
  datasnap data.json --plot
  datasnap data.csv --output report.json
  datasnap data.csv --output report.md
  datasnap file_a.csv file_b.csv --diff
        """,
    )
    parser.add_argument(
        "files", nargs="+", metavar="FILE", help="CSV or JSON file(s) to profile"
    )
    parser.add_argument("--plot", action="store_true", help="show terminal charts")
    parser.add_argument(
        "--output", metavar="PATH", help="save report (.json or .md)"
    )
    parser.add_argument(
        "--diff", action="store_true", help="compare two files (requires 2 FILE args)"
    )
    parser.add_argument(
        "--no-quality", action="store_true", help="skip data quality checks"
    )
    parser.add_argument(
        "--version", action="version", version=f"datasnap {__version__}"
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Lazy imports so CLI --help is instant
    from datasnap.loaders.detect import load_file
    from datasnap.stats.summary import compute_summary
    from datasnap.quality.checks import run_quality_checks
    from datasnap.reports.terminal import print_report

    if args.diff:
        if len(args.files) != 2:
            parser.error("--diff requires exactly 2 files")
        from datasnap.reports.terminal import print_diff_placeholder
        print_diff_placeholder()
        sys.exit(0)

    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"[error] File not found: {file_path}", file=sys.stderr)
            sys.exit(1)

        df = load_file(path)
        summary = compute_summary(df)
        quality = None if args.no_quality else run_quality_checks(df)
        print_report(path.name, df, summary, quality, plot=args.plot)

        if args.output:
            from datasnap.reports.export import save_report
            save_report(args.output, summary, quality)
            from rich.console import Console
            Console().print(f"\n[green]✓[/green] Report saved to {args.output}")


if __name__ == "__main__":
    main()
