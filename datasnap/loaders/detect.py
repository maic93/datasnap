"""Detect file type and dispatch to the correct loader."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from datasnap.loaders.csv_loader import load_csv
from datasnap.loaders.json_loader import load_json

SUPPORTED_EXTENSIONS = {
    ".csv": "CSV",
    ".json": "JSON",
    ".jsonl": "JSONL",
    ".tsv": "TSV",
}


def load_file(path: Path) -> pd.DataFrame:
    """Load a data file into a DataFrame based on its extension.

    Supported formats: .csv, .tsv, .json, .jsonl

    Args:
        path: Path to the file.

    Returns:
        Loaded DataFrame.

    Raises:
        ValueError: If the file extension is not supported.
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: '{path}'")

    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS.keys()))
        raise ValueError(
            f"Unsupported file type '{suffix}'. Supported: {supported}"
        )

    if suffix == ".csv":
        return load_csv(path)

    if suffix == ".tsv":
        return load_csv(path, delimiter="\t")

    # .json or .jsonl
    return load_json(path)


def supported_formats() -> list[str]:
    """Return list of supported file extensions."""
    return sorted(SUPPORTED_EXTENSIONS.keys())
