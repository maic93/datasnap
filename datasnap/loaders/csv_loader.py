"""CSV file loader with validation and encoding detection."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


ENCODINGS = ["utf-8", "latin-1", "cp1252"]


def load_csv(path: Path, delimiter: Optional[str] = None) -> pd.DataFrame:
    """Load a CSV file into a DataFrame.

    Tries multiple encodings automatically.
    Auto-detects delimiter if not provided (comma, semicolon, tab, pipe).

    Args:
        path: Path to the CSV file.
        delimiter: Column separator. Auto-detected if None.

    Returns:
        Loaded DataFrame.

    Raises:
        RuntimeError: If the file cannot be read.
        ValueError: If the file is empty or has no columns.
    """
    last_exc: Optional[Exception] = None

    for encoding in ENCODINGS:
        try:
            sep = delimiter or _detect_delimiter(path, encoding)
            df = pd.read_csv(path, sep=sep, encoding=encoding)
            _validate(df, path)
            return df
        except (UnicodeDecodeError, LookupError):
            continue
        except (ValueError, RuntimeError):
            raise
        except Exception as exc:
            last_exc = exc

    raise RuntimeError(
        f"Could not read '{path}' with encodings {ENCODINGS}. "
        f"Last error: {last_exc}"
    )


def _detect_delimiter(path: Path, encoding: str) -> str:
    """Sniff the delimiter from the first line of the file."""
    try:
        first_line = path.read_text(encoding=encoding).splitlines()[0]
    except Exception:
        return ","

    counts = {
        ",": first_line.count(","),
        ";": first_line.count(";"),
        "\t": first_line.count("\t"),
        "|": first_line.count("|"),
    }
    best = max(counts, key=lambda k: counts[k])
    return best if counts[best] > 0 else ","


def _validate(df: pd.DataFrame, path: Path) -> None:
    """Raise ValueError for clearly bad files."""
    if df.empty:
        raise ValueError(f"'{path}' loaded as empty — no rows found.")
    if len(df.columns) == 0:
        raise ValueError(f"'{path}' has no columns.")
