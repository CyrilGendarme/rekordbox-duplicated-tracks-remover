from __future__ import annotations

from typing import Any

from config import (
    EMPTY_STRING,
    HOT_CUES_COUNT_KEY,
    MEMORY_CUES_COUNT_KEY,
    MY_TAG_ATTRIBUTE,
    TAG_NAME_ATTRIBUTES,
    TRACK_TAG_ATTRIBUTES,
)
from normalizers import safe_string


def _extract_tag_name(value: Any) -> str:
    """Extract a tag name from the supported Rekordbox tag shapes."""
    for attr_name in TAG_NAME_ATTRIBUTES:
        name = safe_string(getattr(value, attr_name, EMPTY_STRING)).strip()
        if name:
            return name

    my_tag = getattr(value, MY_TAG_ATTRIBUTE, None)
    return safe_string(getattr(my_tag, TAG_NAME_ATTRIBUTES[0], EMPTY_STRING)).strip()


def extract_track_tags(content: Any) -> list[str]:
    """Best-effort extraction of tag names from a Rekordbox content object."""
    tag_values: list[Any] = []
    for attr_name in TRACK_TAG_ATTRIBUTES:
        value = getattr(content, attr_name, None)
        if value:
            tag_values.append(value)

    tags: list[str] = []
    for value in tag_values:
        if isinstance(value, str):
            tag = value.strip()
            if tag:
                tags.append(tag)
            continue

        if isinstance(value, (list, tuple, set)):
            for item in value:
                name = _extract_tag_name(item)
                if name:
                    tags.append(name)
            continue

        name = _extract_tag_name(value)
        if name:
            tags.append(name)

    deduped: list[str] = []
    for tag in tags:
        if tag not in deduped:
            deduped.append(tag)
    return deduped


def extract_track_cues(content: Any) -> dict[str, list[str]]:
    """Best-effort extraction of hot cues and memory cues for debug output."""

    def collect(hot_cues: bool) -> int:
        cues_cnt = 0
        for cue in content.Cues:
            if (hot_cues and cue.is_hot_cue) or (not hot_cues and cue.is_memory_cue):
                cues_cnt += 1
        return cues_cnt

    return {
        HOT_CUES_COUNT_KEY: collect(hot_cues=True),
        MEMORY_CUES_COUNT_KEY: collect(hot_cues=False),
    }
