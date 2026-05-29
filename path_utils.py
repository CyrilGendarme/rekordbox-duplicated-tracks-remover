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

    if not dropbox_dir or not filename:
        return None

    target_name = Path(filename).name.strip()
    if not target_name:
        return None

    dropbox_root = Path(dropbox_dir)
    if not dropbox_root.exists():
        return None

    target_name_casefold = target_name.casefold()
    target_normalized = normalize_filename(target_name)

    first_case_insensitive_match: str | None = None
    first_normalized_match: str | None = None
    for file_path in dropbox_root.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.name == target_name:
            return str(file_path)

        if (
            first_case_insensitive_match is None
            and file_path.name.casefold() == target_name_casefold
        ):
            first_case_insensitive_match = str(file_path)

        if (
            target_normalized
            and first_normalized_match is None
            and normalize_filename(file_path.name) == target_normalized
        ):
            first_normalized_match = str(file_path)

    if first_case_insensitive_match is not None:
        return first_case_insensitive_match

    if first_normalized_match is not None:
        return first_normalized_match

    return None
