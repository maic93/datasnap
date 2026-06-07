"""CSV file loader."""

from pathlib import Path

import pandas as pd


def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise RuntimeError(f"Failed to read CSV '{path}': {exc}") from exc
    if df.empty:
        raise ValueError(f"CSV '{path}' is empty.")
    return df
