"""Path utility functions for file location and comparison."""

from __future__ import annotations

from pathlib import Path

from normalizers import normalize_filename


def path_under_directory(candidate: Path, directory: Path) -> bool:
    """Check if a candidate path is under a directory."""
    try:
        candidate.resolve(strict=False).relative_to(directory.resolve(strict=False))
        return True
    except ValueError:
        return False


def find_first_dropbox_file(
    dropbox_dir: str | Path | None, filename: str
) -> str | None:
    """Find the first occurrence of a file in the Dropbox directory tree."""

    print(f"Searching for '{filename}' in Dropbox directory: {dropbox_dir}")

    if not dropbox_dir or not filename:
        return None

    target_name = Path(filename).name.strip()
    if not target_name:
        return None

    dropbox_root = Path(dropbox_dir)
    if not dropbox_root.exists():
        return None

    # Fast path: exact filename lookup.
    for file_path in dropbox_root.rglob(target_name):
        if file_path.is_file():
            return str(file_path)

    # Fallback 1: case-insensitive filename lookup.
    target_name_casefold = target_name.casefold()
    for file_path in dropbox_root.rglob("*"):
        if file_path.is_file() and file_path.name.casefold() == target_name_casefold:
            return str(file_path)

    # Fallback 2: compare normalized stems to tolerate punctuation differences.
    target_normalized = normalize_filename(target_name)
    if target_normalized:
        for file_path in dropbox_root.rglob("*"):
            if (
                file_path.is_file()
                and normalize_filename(file_path.name) == target_normalized
            ):
                return str(file_path)

    return None
