"""Matching logic for finding duplicate tracks across collections."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cleanup import perform_cleanup
from file_operations import scan_audio_files
from normalizers import normalize_filename


def find_matching_files(
    duplicates: list[list[dict[str, str]]],
    youtube_dir: str,
    dropbox_dir: str | None = None,
    auto_cleanup: bool = False,
    test_mode: bool = False,
    titles_only: bool = False,
    db: Any = None,
) -> None:
    """Find matching files and optionally cleanup/relocate."""
    if not titles_only:
        print(f"\nScanning {youtube_dir} for audio files...")
    youtube_files = scan_audio_files(youtube_dir)

    if not youtube_files:
        if not titles_only:
            print("No audio files found in the specified directory.")
        return

    if not titles_only:
        print(f"Found {len(youtube_files)} audio files in {youtube_dir}")

    # Build normalized filename maps
    youtube_normalized = {normalize_filename(name): name for name in youtube_files.keys()}

    found_matches = 0
    if not titles_only:
        print("\n=== FILENAME MATCHING ===")

    for dup_group in duplicates:
        for item_idx, item in enumerate(dup_group):
            file_path = item["path"]
            if not file_path:
                continue

            # Extract filename from path
            filename = Path(file_path).name
            normalized = normalize_filename(filename)

            if normalized in youtube_normalized:
                youtube_filename = youtube_normalized[normalized]
                youtube_path = youtube_files[youtube_filename]
                found_matches += 1

                if titles_only:
                    print(f"{item['artist']} - {item['title']}")
                else:
                    print(f"\n[Match {found_matches}]")
                    print(f"  Rekordbox: {item['artist']} - {item['title']}")
                    print(f"    Rekordbox Path (matched): {item['path']}")
                    print(f"  YouTube Download:")
                    print(f"    Path: {youtube_path}")

                # Show non-matching duplicates
                non_matching = [it for idx, it in enumerate(dup_group) if idx != item_idx]
                if non_matching and not titles_only:
                    print(f"  Non-matching duplicates in group:")
                    for nm in non_matching:
                        print(f"    - {nm['artist']} - {nm['title']} (path: {nm['path']})")

                # Perform cleanup if requested
                if auto_cleanup and dropbox_dir:
                    if not titles_only:
                        print(f"\n  [CLEANUP PROCEDURE]")
                    perform_cleanup(
                        item,
                        non_matching,
                        youtube_path,
                        dropbox_dir,
                        db,
                        test_mode,
                        titles_only,
                    )

                if test_mode:
                    if not titles_only:
                        print("\n[TEST MODE] Exiting after first match.")
                    return

    if not titles_only:
        if found_matches == 0:
            print("No matching files found between Rekordbox duplicates and YouTube downloads.")
        else:
            print(f"\nTotal matches: {found_matches}")
