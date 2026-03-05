"""Find duplicate tracks in a Rekordbox 6 collection using pyrekordbox.

Duplicate criteria: same title and artist.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from typing import Any

from cli import parse_args
from matcher import find_matching_files
from normalizers import normalize, safe_string
from rekordbox_helpers import get_artist_name, get_track_id, get_track_path



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

    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)

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
            groups[key].append(
                {
                    "title": title,
                    "artist": artist,
                    "id": get_track_id(content),
                    "path": get_track_path(content),
                }
            )

        duplicates = [items for items in groups.values() if len(items) > 1]
        duplicates.sort(key=lambda items: (items[0]["artist"].casefold(), items[0]["title"].casefold()))

        if not duplicates:
            if not args.titles_only:
                print("No duplicates found.")
            return 0

        if not args.titles_only:
            total_tracks = sum(len(items) for items in duplicates)
            print(f"Found {len(duplicates)} duplicate groups ({total_tracks} tracks).")

            for index, items in enumerate(duplicates, start=1):
                title = items[0]["title"] or "<empty title>"
                artist = items[0]["artist"] or "<empty artist>"
                print(f"\n[{index}] {artist} - {title} ({len(items)} tracks)")
                for item in items:
                    line = f"  - id={item['id']}"
                    if item["path"]:
                        line += f" | src_storage_path={item['path']}"
                    print(line)

        if args.youtube_dir:
            find_matching_files(
                duplicates,
                args.youtube_dir,
                dropbox_dir=args.dropbox_dir,
                auto_cleanup=args.auto_cleanup,
                test_mode=args.test_mode,
                titles_only=args.titles_only,
                db=db,
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
