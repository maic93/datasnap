"""Detect file type and dispatch to the correct loader."""

from pathlib import Path

import pandas as pd

from datasnap.loaders.csv_loader import load_csv
from datasnap.loaders.json_loader import load_json

SUPPORTED = {".csv", ".json", ".jsonl"}


def load_file(path: Path) -> pd.DataFrame:
    """Load a CSV or JSON/JSONL file into a DataFrame."""
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Supported: {', '.join(sorted(SUPPORTED))}"
        )
    if suffix == ".csv":
        return load_csv(path)
    return load_json(path)
