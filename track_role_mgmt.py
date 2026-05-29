from __future__ import annotations

from typing import Any

from config import COPYRIGHT_OK_TAG, HOT_CUES_COUNT_KEY, NOT_TAGGED_TAG

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
        item for item in items if COPYRIGHT_OK_TAG in _item_tags_lower(item)
    ]
    if copyright_candidates:
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

    scored_items = [
        {
            "item": item,
            "hot_cues_count": (item.get("cues") or {}).get(HOT_CUES_COUNT_KEY, 0),
            "is_not_tagged": NOT_TAGGED_TAG in _item_tags_lower(item),
        }
        for item in items
    ]

    # --- Rule 1: Prefer items with hot cues ---
    max_hot = max(candidate["hot_cues_count"] for candidate in scored_items)
    if max_hot > 0:
        candidates = [
            candidate["item"]
            for candidate in scored_items
            if candidate["hot_cues_count"] == max_hot
        ]
        return candidates[0]

    # --- Rule 2: Prefer items NOT tagged as "Not Tagged" ---
    not_tagged_flags = [candidate["is_not_tagged"] for candidate in scored_items]
    if any(not_tagged_flags) and not all(not_tagged_flags):
        for candidate in scored_items:
            if not candidate["is_not_tagged"]:
                return candidate["item"]

    # --- Rule 3: fallback ---
    return _select_file_owner_item(items)


def find_matching_files(
    duplicate: list[dict[str, str]],
) -> dict[str, dict[str, Any]] | None:
    """Find matching files and optionally cleanup/relocate."""

    file_owner_item = _select_file_owner_item(duplicate)
    metadata_owner_item = _select_metadata_owner_item(duplicate)

    return {"file_owner": file_owner_item, "metadata_owner": metadata_owner_item}
