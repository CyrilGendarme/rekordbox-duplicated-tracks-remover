"""Cleanup workflow for duplicate track management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from file_operations import safe_delete_file
from normalizers import normalize_path_for_compare
from path_utils import find_first_dropbox_file, path_under_directory
from rekordbox_operations import delete_rekordbox_track, relocate_rekordbox_track


def select_surviving_dropbox_path(non_matching: list[dict[str, str]], dropbox_dir: str) -> str | None:
    """Select the surviving Dropbox file path from non-matching duplicates."""
    dropbox_root = Path(dropbox_dir)

    for item in non_matching:
        item_path = item.get("path", "")
        if not item_path:
            continue

        path_obj = Path(item_path)
        if path_obj.exists() and path_under_directory(path_obj, dropbox_root):
            return str(path_obj)

        candidate = find_first_dropbox_file(dropbox_dir, path_obj.name)
        if candidate:
            return candidate

    return None


def perform_cleanup(
    matched_item: dict[str, str],
    non_matching: list[dict[str, str]],
    youtube_path: str,
    dropbox_dir: str,
    db: Any,
    test_mode: bool,
    titles_only: bool,
) -> None:
    """Perform the cleanup sequence for a matched pair."""
    matched_id = str(matched_item.get("id", ""))
    surviving_dropbox_path = select_surviving_dropbox_path(non_matching, dropbox_dir)

    # Step 1: Delete from local directory (youtube_downloaded)
    if not titles_only:
        print(f"  [1/4] Delete from local directory...")
    safe_delete_file(
        youtube_path,
        reason="consolidated to Dropbox",
        log_enabled=not titles_only,
        verbose=not titles_only,
    )

    # Step 2: Delete non-matching duplicate tracks from Rekordbox collection
    if not titles_only:
        print(f"  [2/4] Delete non-matching duplicate tracks from Rekordbox collection...")
    for nm in non_matching:
        nm_id = str(nm.get("id", ""))
        if not titles_only:
            print(f"    - Removing collection entry: {nm['artist']} - {nm['title']} (id={nm_id})")
        delete_rekordbox_track(db, nm_id, verbose=not titles_only, log_enabled=not titles_only)

    # Step 3: Find and delete matching file from Dropbox
    if not titles_only:
        print(f"  [3/4] Delete matched track from Dropbox...")
    dropbox_file = find_first_dropbox_file(dropbox_dir, Path(youtube_path).name)
    if dropbox_file:
        if surviving_dropbox_path and normalize_path_for_compare(dropbox_file) == normalize_path_for_compare(surviving_dropbox_path):
            if not titles_only:
                print(f"    [SKIP] Dropbox file is selected as surviving target: {dropbox_file}")
        else:
            if not titles_only:
                print(f"    Found in Dropbox: {dropbox_file}")
            safe_delete_file(
                dropbox_file,
                reason="duplicate copy matching local download",
                log_enabled=not titles_only,
                verbose=not titles_only,
            )
    else:
        if not titles_only:
            print(f"    [SKIP] No Dropbox file found matching local filename: {Path(youtube_path).name}")

    # Step 4: Relocate remaining track to Dropbox
    if not titles_only:
        print(f"  [4/4] Relocate track to Dropbox...")
    if not surviving_dropbox_path:
        if not titles_only:
            print("    [SKIP] No surviving Dropbox file found to relocate to.")
    elif not matched_id:
        if not titles_only:
            print("    [SKIP] Matched Rekordbox content has no ID.")
    else:
        relocated = relocate_rekordbox_track(
            db,
            matched_id,
            surviving_dropbox_path,
            verbose=not titles_only,
            log_enabled=not titles_only,
        )
        if relocated:
            if not titles_only:
                print(f"    Relocated content id={matched_id} to: {surviving_dropbox_path}")
        else:
            if not titles_only:
                print(f"    [ERROR] Relocation failed for content id={matched_id}")

    if test_mode and not titles_only:
        print("  [TEST MODE] Processed first matching pair and stopped.")

    if not titles_only:
        print(f"\n  ✓ Cleanup sequence complete for: {matched_item['artist']} - {matched_item['title']}")
