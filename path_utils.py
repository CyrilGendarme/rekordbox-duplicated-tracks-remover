"""Path utility functions for file location and comparison."""

from __future__ import annotations

from pathlib import Path


def path_under_directory(candidate: Path, directory: Path) -> bool:
    """Check if a candidate path is under a directory."""
    try:
        candidate.resolve(strict=False).relative_to(directory.resolve(strict=False))
        return True
    except ValueError:
        return False


def find_first_dropbox_file(dropbox_dir: str, filename: str) -> str | None:
    """Find the first occurrence of a file in the Dropbox directory tree."""
    dropbox_root = Path(dropbox_dir)
    if not dropbox_root.exists() or not filename:
        return None

    for file_path in dropbox_root.rglob(filename):
        if file_path.is_file():
            return str(file_path)
    return None
