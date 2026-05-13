from __future__ import annotations

from typing import Any


def _item_tags_lower(item: dict[str, Any]) -> set[str]:
    raw_tags = item.get("tags") or []
    if isinstance(raw_tags, str):
        raw_tags = [raw_tags]
    if not isinstance(raw_tags, (list, tuple, set)):
        return set()
    return {str(tag).strip().lower() for tag in raw_tags if str(tag).strip()}


def _select_file_owner_item(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Choose which duplicate should keep the physical file.

    Rule: if one track has tag "Copyright Ok", prefer that one.
    """
    if not items:
        return None

    copyright_candidates = [
        item for item in items if "copyright ok" in _item_tags_lower(item)
    ]
    if copyright_candidates:
        # print("---- found copyright ok candidate")
        return copyright_candidates[0]

    return items[0]


def _select_metadata_owner_item(
    items: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Choose which duplicate should keep the Rekordbox metadata entry.

    Priority:
    1) Track with the most hot cues
    2) Track without "Not Tagged"
    3) Fallback to file owner
    """

    def hot_cues_count(item: dict[str, Any]) -> int:
        return (item.get("cues") or {}).get("hot_cues_cnt", 0)

    def is_not_tagged(item: dict[str, Any]) -> bool:
        return "not tagged" in _item_tags_lower(item)

    # --- Rule 1: Prefer items with hot cues ---
    max_hot = max(hot_cues_count(item) for item in items)
    if max_hot > 0:
        candidates = [item for item in items if hot_cues_count(item) == max_hot]
        return candidates[0]  # deterministic enough, or add tie-breaker if needed

    # --- Rule 2: Prefer items NOT tagged as "Not Tagged" ---
    not_tagged_flags = [is_not_tagged(item) for item in items]
    if any(not_tagged_flags) and not all(not_tagged_flags):
        for item in items:
            if not is_not_tagged(item):
                return item

    # --- Rule 3: fallback ---
    return _select_file_owner_item(items)


def find_matching_files(
    duplicate: list[dict[str, str]],
) -> dict[str, dict[str, Any]] | None:
    """Find matching files and optionally cleanup/relocate."""

    # print(f"\n\n\n\n=== original duplicate ===")
    # for item in duplicate:
    #     print(
    #         f"-\nRekordbox: id={item['id']} title='{item['title']}' artist='{item['artist']}' path_rekordbox_dir='{item['path_rekordbox_dir']}' path_local_dir='{item['path_local_dir']}' tags='{item['tags']}' cues='{item['cues']}'"
    #     )

    file_owner_item = _select_file_owner_item(duplicate)
    metadata_owner_item = _select_metadata_owner_item(duplicate)

    # print(f"\n=== MATCHED GROUP ===")
    # print(
    #     f"Metadata owner: {metadata_owner_item['artist']} - {metadata_owner_item['title']} (id={metadata_owner_item['id']})"
    # )
    # print(
    #     f"File owner: {file_owner_item['artist']} - {file_owner_item['title']} (id={file_owner_item['id']})"
    # )

    return {"file_owner": file_owner_item, "metadata_owner": metadata_owner_item}
