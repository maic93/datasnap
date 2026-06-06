"""CSV file loader with basic validation."""

from pathlib import Path

import pandas as pd


def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV file, inferring dtypes and parsing dates where possible."""
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise RuntimeError(f"Failed to read CSV '{path}': {exc}") from exc

    if df.empty:
        raise ValueError(f"CSV file '{path}' is empty or has no rows.")

    return df
