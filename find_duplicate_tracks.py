"""Find duplicate tracks in a Rekordbox 6 collection using pyrekordbox.

Duplicate criteria: same title and artist.
"""

from __future__ import annotations

from pathlib import Path
import sys
from collections import defaultdict
from typing import Any

from cli import parse_args
from config import (
    COPYRIGHT_OK_TAG,
    DB_COMMIT_SUCCESS_MESSAGE,
    DEFAULT_LOG_ENABLED,
    DEFAULT_VERBOSE,
    DRY_RUN_PREFIX,
    DROPBOX_FILE_DELETE_REASON,
    EMPTY_STRING,
    EXIT_CODE_DB_OPEN_ERROR,
    EXIT_CODE_IMPORT_ERROR,
    EXIT_CODE_SUCCESS,
    LOCAL_FILE_DELETE_REASON,
    NO_DUPLICATES_FOUND_MESSAGE,
    PYREKORDBOX_IMPORT_ERROR_MESSAGE,
    RECORD_RIP_TAG,
    REKORDBOX_CLOSE_METHOD,
    REKORDBOX_COMMIT_METHOD,
    REKORDBOX_GET_CONTENT_METHOD,
    REKORDBOX_OPEN_ERROR_TEMPLATE,
    ROOT_PATH_PREFIX,
    UNKNOWN_CONTENT_ID,
)

from normalizers import normalize, safe_string
from rekordbox_helpers import get_artist_name
from file_operations import safe_delete_file
from path_utils import find_first_dropbox_file
from rekordbox_operations import delete_rekordbox_track, relocate_rekordbox_track
from track_info_extraction import extract_track_tags, extract_track_cues
from track_role_mgmt import find_matching_files


def _merge_protected_tags(
    metadata_owner_item: dict[str, Any],
    removed_items: list[dict[str, Any]],
) -> list[str]:
    """Merge protected tags from removed duplicates into metadata owner tags."""
    protected = {RECORD_RIP_TAG, COPYRIGHT_OK_TAG}

    merged: list[str] = []
    seen_lower: set[str] = set()

    for tag in metadata_owner_item.get("tags", []) or []:
        tag_text = safe_string(tag).strip()
        if not tag_text:
            continue
        tag_lower = tag_text.lower()
        if tag_lower in seen_lower:
            continue
        merged.append(tag_text)
        seen_lower.add(tag_lower)

    for item in removed_items:
        for tag in item.get("tags", []) or []:
            tag_text = safe_string(tag).strip()
            if not tag_text:
                continue
            tag_lower = tag_text.lower()
            if tag_lower not in protected or tag_lower in seen_lower:
                continue
            merged.append(tag_text)
            seen_lower.add(tag_lower)

    return merged


def _set_rekordbox_track_tags(
    db: Any,
    content_id: str,
    tags: list[str],
) -> bool:
    """Best-effort update of tag names on a Rekordbox content row."""
    if db is None or not content_id:
        return False

    get_content_fn = getattr(db, REKORDBOX_GET_CONTENT_METHOD, None)
    if not callable(get_content_fn):
        return False

    content = get_content_fn(ID=str(content_id))
    if content is None:
        return False

    # Prefer MyTagNames because extraction already supports it as plain names.
    for attr_name in ("MyTagNames", "MyTags", "Tags"):
        if not hasattr(content, attr_name):
            continue
        try:
            setattr(content, attr_name, tags)
            return True
        except Exception:
            continue

    return False


def perform_cleanup(
    duplicates,
    file_owner_item,
    metadata_owner_item,
    db: Any,
    dropbox_dir: str,
    *,
    dry_run: bool = False,
) -> None:

    metadata_owner_id = str(metadata_owner_item.get("id", EMPTY_STRING))
    removed_items = [
        item
        for item in duplicates
        if str(item.get("id", EMPTY_STRING)) != metadata_owner_id
    ]
    merged_tags = _merge_protected_tags(metadata_owner_item, removed_items)
    existing_tags = metadata_owner_item.get("tags", []) or []
    has_new_tags = len(merged_tags) > len(existing_tags)

    if has_new_tags:
        if dry_run:
            print(
                f"{DRY_RUN_PREFIX} Would merge protected tags into "
                f"Rekordbox content id={metadata_owner_id}: "
                f"{', '.join(merged_tags)}",
                file=sys.stderr,
            )
        else:
            _set_rekordbox_track_tags(db, metadata_owner_id, merged_tags)
        metadata_owner_item["tags"] = merged_tags

    if file_owner_item is metadata_owner_item:
        for item in duplicates:
            if item is file_owner_item:
                continue

            if dry_run:
                print(
                    f"{DRY_RUN_PREFIX} Would delete local file: "
                    f"{item.get('path_local_dir')}",
                    file=sys.stderr,
                )
                print(
                    f"{DRY_RUN_PREFIX} Would delete Rekordbox content "
                    f"id={item.get('id', EMPTY_STRING)}",
                    file=sys.stderr,
                )
            else:
                safe_delete_file(
                    item.get("path_local_dir"),
                    reason=LOCAL_FILE_DELETE_REASON,
                    log_enabled=DEFAULT_LOG_ENABLED,
                    verbose=DEFAULT_VERBOSE,
                )

                delete_rekordbox_track(
                    db,
                    str(item.get("id", EMPTY_STRING)),
                    verbose=DEFAULT_VERBOSE,
                    log_enabled=DEFAULT_LOG_ENABLED,
                )

            dropbox_file_path = find_first_dropbox_file(
                dropbox_dir, Path(item.get("path_rekordbox_dir", "")).name
            )

            if dry_run:
                print(
                    f"{DRY_RUN_PREFIX} Would delete Dropbox file: "
                    f"{dropbox_file_path}",
                    file=sys.stderr,
                )
            else:
                safe_delete_file(
                    dropbox_file_path,
                    reason=DROPBOX_FILE_DELETE_REASON,
                    log_enabled=DEFAULT_LOG_ENABLED,
                    verbose=DEFAULT_VERBOSE,
                )

            return

    # Step 1: Delete all items from local directory, except the selected file owner item
    for item in duplicates:
        if item is file_owner_item:
            continue

        if dry_run:
            print(
                f"{DRY_RUN_PREFIX} Would delete local file: "
                f"{item.get('path_local_dir')}",
                file=sys.stderr,
            )
        else:
            safe_delete_file(
                item.get("path_local_dir"),
                reason=LOCAL_FILE_DELETE_REASON,
                log_enabled=DEFAULT_LOG_ENABLED,
                verbose=DEFAULT_VERBOSE,
            )

    # Step 2: Delete non-matching duplicate tracks from Rekordbox collection
    for item in duplicates:
        if str(item.get("id", EMPTY_STRING)) == str(metadata_owner_id):
            continue

        if dry_run:
            print(
                f"{DRY_RUN_PREFIX} Would delete Rekordbox content "
                f"id={item.get('id', EMPTY_STRING)}",
                file=sys.stderr,
            )
        else:
            delete_rekordbox_track(
                db,
                str(item.get("id", EMPTY_STRING)),
                verbose=DEFAULT_VERBOSE,
                log_enabled=DEFAULT_LOG_ENABLED,
            )

    # Step 3: Find and delete duplicate files from Dropbox
    for item in duplicates:
        if item is file_owner_item:
            continue

        dropbox_file_path = find_first_dropbox_file(
            dropbox_dir, Path(item.get("path_rekordbox_dir", "")).name
        )

        if dropbox_file_path is not None:
            if dry_run:
                print(
                    f"{DRY_RUN_PREFIX} Would delete Dropbox file: "
                    f"{dropbox_file_path}",
                    file=sys.stderr,
                )
            else:
                safe_delete_file(
                    dropbox_file_path,
                    reason=DROPBOX_FILE_DELETE_REASON,
                    log_enabled=DEFAULT_LOG_ENABLED,
                    verbose=DEFAULT_VERBOSE,
                )

    # Step 4: Relocate remaining track to Dropbox
    dropbox_owner_path = find_first_dropbox_file(
        dropbox_dir, Path(file_owner_item.get("path_rekordbox_dir", "")).name
    )
    if dropbox_owner_path is not None:
        if dry_run:
            print(
                f"{DRY_RUN_PREFIX} Would relocate Rekordbox content "
                f"id={metadata_owner_item.get('id', UNKNOWN_CONTENT_ID)} -> "
                f"{dropbox_owner_path}",
                file=sys.stderr,
            )
        else:
            relocate_rekordbox_track(
                db,
                metadata_owner_item.get("id", UNKNOWN_CONTENT_ID),
                dropbox_owner_path,
                verbose=DEFAULT_VERBOSE,
                log_enabled=DEFAULT_LOG_ENABLED,
            )


def main() -> int:
    args = parse_args()

    try:
        from pyrekordbox import Rekordbox6Database
    except ImportError:
        print(PYREKORDBOX_IMPORT_ERROR_MESSAGE, file=sys.stderr)
        return EXIT_CODE_IMPORT_ERROR

    db_kwargs: dict[str, Any] = {}
    if args.key:
        db_kwargs["key"] = args.key

    try:
        db = Rekordbox6Database(**db_kwargs)
    except Exception as exc:
        print(REKORDBOX_OPEN_ERROR_TEMPLATE.format(exc=exc), file=sys.stderr)
        return EXIT_CODE_DB_OPEN_ERROR

    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    try:
        tracks = db.get_content()

        dropbox_base = Path(args.dropbox_dir) if args.dropbox_dir else None

        for content in tracks:
            title = safe_string(getattr(content, "Title", ""))
            artist = get_artist_name(content)

            if not args.include_empty and (not title or not artist):
                continue

            key = (
                normalize(title, args.case_sensitive),
                normalize(artist, args.case_sensitive),
            )

            should_include_track = True
            if dropbox_base is not None:
                folder = Path(content.FolderPath)
                folder = Path(folder.as_posix().lstrip(ROOT_PATH_PREFIX))
                rekordbox_file_path = dropbox_base / folder
                should_include_track = rekordbox_file_path.exists()

            if should_include_track:
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
            print(NO_DUPLICATES_FOUND_MESSAGE)
            return EXIT_CODE_SUCCESS

        if args.test_mode:
            duplicates = [duplicates[0]]

        for duplicate in duplicates:
            matching_files = find_matching_files(duplicate)

            perform_cleanup(
                duplicate,
                matching_files["file_owner"],
                matching_files["metadata_owner"],
                db,
                args.dropbox_dir,
                dry_run=args.dry_run,
            )

        if args.auto_cleanup and not args.dry_run:
            commit_fn = getattr(db, REKORDBOX_COMMIT_METHOD, None)
            if callable(commit_fn):
                commit_fn()
                if not args.titles_only:
                    print(DB_COMMIT_SUCCESS_MESSAGE)
        elif args.auto_cleanup and args.dry_run and not args.titles_only:
            print(f"{DRY_RUN_PREFIX} Rekordbox commit skipped.")

        return EXIT_CODE_SUCCESS

    finally:
        close_fn = getattr(db, REKORDBOX_CLOSE_METHOD, None)
        if callable(close_fn):
            close_fn()


if __name__ == "__main__":
    raise SystemExit(main())
