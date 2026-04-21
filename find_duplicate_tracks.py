"""Find duplicate tracks in a Rekordbox 6 collection using pyrekordbox.

Duplicate criteria: same title and artist.
"""

from __future__ import annotations

from pathlib import Path
import sys
from collections import defaultdict
from typing import Any

from cli import parse_args

from normalizers import normalize, safe_string
from rekordbox_helpers import get_artist_name
from file_operations import safe_delete_file
from path_utils import find_first_dropbox_file
from rekordbox_operations import delete_rekordbox_track, relocate_rekordbox_track
from track_info_extraction import extract_track_tags, extract_track_cues
from track_role_mgmt import find_matching_files


def perform_cleanup(
    duplicates,
    file_owner_item,
    metadata_owner_item,
    db: Any,
    dropbox_dir: str,
) -> None:

    if file_owner_item is metadata_owner_item:
        for item in duplicates:
            if item is file_owner_item:
                continue

            safe_delete_file(
                item.get("path_local_dir"),
                reason="remove local downloaded file",
                log_enabled=True,
                verbose=False,
            )

            delete_rekordbox_track(
                db, str(item.get("id", "")), verbose=False, log_enabled=True
            )

            dropbox_file_path = find_first_dropbox_file(
                dropbox_dir, Path(item.get("path_rekordbox_dir", "")).name
            )

            safe_delete_file(
                dropbox_file_path,
                reason="remove dropbox dir file",
                log_enabled=True,
                verbose=False,
            )

            # print(f"\n[DRY RUN] UNIQUE FILE")

            return

    # Step 1: Delete all items from local directory, except the selected file owner item
    for item in duplicates:
        if item is file_owner_item:
            continue

        safe_delete_file(
            item.get("path_local_dir"),
            reason="remove local downloaded file",
            log_enabled=True,
            verbose=False,
        )

        # print(
        #     f"\n[DRY RUN] Would delete local file : {item.get('id')} | {item.get('path_local_dir')}"
        # )

    # Step 2: Delete non-matching duplicate tracks from Rekordbox collection
    for item in duplicates:
        if str(item.get("id", "")) == str(metadata_owner_item.get("id", "")):
            continue

        delete_rekordbox_track(
            db, str(item.get("id", "")), verbose=False, log_enabled=True
        )

        # print(f"\n[DRY RUN] Would delete Rekordbox track : {item.get('id')}")

    # Step 3: Find and delete duplicate files from Dropbox
    for item in duplicates:
        if item is file_owner_item:
            continue

        dropbox_file_path = find_first_dropbox_file(
            dropbox_dir, Path(item.get("path_rekordbox_dir", "")).name
        )

        safe_delete_file(
            dropbox_file_path,
            reason="remove dropbox dir file",
            log_enabled=True,
            verbose=False,
        )

        # print(
        #     f"\n[DRY RUN] Would delete Dropbox file : {item.get('id')} | {dropbox_file_path}"
        # )

    # Step 4: Relocate remaining track to Dropbox
    relocate_rekordbox_track(
        db,
        metadata_owner_item.get("id", "?"),
        find_first_dropbox_file(
            dropbox_dir, Path(file_owner_item.get("path_rekordbox_dir", "")).name
        ),
        verbose=False,
        log_enabled=True,
    )

    # print(
    #     f"\n[DRY RUN] Would relocate track with id: {metadata_owner_item.get('id', '?')} to Dropbox path: {find_first_dropbox_file(dropbox_dir, Path(file_owner_item.get('path', '')).name)}."
    # )


def main() -> int:
    args = parse_args()

    try:
        from pyrekordbox import Rekordbox6Database
    except ImportError:
        print(
            "pyrekordbox is not installed. Run: pip install pyrekordbox",
            file=sys.stderr,
        )
        return 1

    db_kwargs: dict[str, Any] = {}
    if args.key:
        db_kwargs["key"] = args.key

    try:
        db = Rekordbox6Database(**db_kwargs)
    except Exception as exc:
        print(f"Failed to open Rekordbox database: {exc}", file=sys.stderr)
        return 2

    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    try:
        tracks = db.get_content()

        for content in tracks:
            title = safe_string(getattr(content, "Title", ""))
            artist = get_artist_name(content)

            if not args.include_empty and (not title or not artist):
                continue

            key = (
                normalize(title, args.case_sensitive),
                normalize(artist, args.case_sensitive),
            )

            # Workaround to solve strange db entries duplicated (fuck Rekordbox)
            base = Path(args.dropbox_dir)
            folder = Path(content.FolderPath)
            folder = Path(folder.as_posix().lstrip("/"))
            rekordbox_file_path = base / folder
            if rekordbox_file_path.exists():
                groups[key].append(
                    {
                        "title": title,
                        "artist": artist,
                        "id": content.ID,
                        "path_rekordbox_dir": content.FolderPath,
                        "path_local_dir": content.OrgFolderPath,
                        "tags": extract_track_tags(content),
                        "cues": extract_track_cues(content),
                    }
                )

        duplicates = [items for items in groups.values() if len(items) > 1]
        duplicates.sort(
            key=lambda items: (
                items[0]["artist"].casefold(),
                items[0]["title"].casefold(),
            )
        )

        if not duplicates:
            if not args.titles_only:
                print("No duplicates found.")
            return 0

        # FIXME: for dev purposes only
        # duplicates = [duplicates[0]]

        for duplicate in duplicates:

            matching_files = find_matching_files(duplicate)

            perform_cleanup(
                duplicate,
                matching_files["file_owner"],
                matching_files["metadata_owner"],
                db,
                args.dropbox_dir,
            )

        if args.auto_cleanup:
            commit_fn = getattr(db, "commit", None)
            if callable(commit_fn):
                commit_fn()
                if not args.titles_only:
                    print("\n[DB] Rekordbox database save committed.")

        return 0

    finally:
        close_fn = getattr(db, "close", None)
        if callable(close_fn):
            close_fn()


if __name__ == "__main__":
    raise SystemExit(main())
