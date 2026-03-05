"""Normalization utilities for text and filenames."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def normalize(value: str, case_sensitive: bool) -> str:
    """Normalize a string value for comparison."""
    cleaned = " ".join(value.strip().split())
    return cleaned if case_sensitive else cleaned.casefold()


def safe_string(value: Any) -> str:
    """Convert any value to a safe string."""
    if value is None:
        return ""
    return str(value).strip()


def normalize_filename(filename: str) -> str:
    """Normalize filename for comparison by removing special characters and extensions."""
    # Remove extension, convert to lowercase, remove special chars
    name_without_ext = Path(filename).stem
    normalized = re.sub(r"[^a-z0-9\s]", "", name_without_ext.lower())
    # Normalize whitespace
    normalized = " ".join(normalized.split())
    return normalized


def normalize_path_for_compare(path: str | Path) -> str:
    """Normalize a path for comparison (case-insensitive, forward slashes)."""
    return str(path).replace("\\", "/").rstrip("/").casefold()
