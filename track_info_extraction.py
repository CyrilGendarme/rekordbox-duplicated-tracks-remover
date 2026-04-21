from __future__ import annotations

from typing import Any

from normalizers import  safe_string


def extract_track_tags(content: Any) -> list[str]:
    """Best-effort extraction of tag names from a Rekordbox content object."""
    tag_values = []
    for attr_name in ("MyTagNames", "MyTags", "Tags"):
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
                name = safe_string(getattr(item, "Name", "")).strip()
                if not name:
                    name = safe_string(getattr(item, "TagName", "")).strip()
                if not name:
                    my_tag = getattr(item, "MyTag", None)
                    name = safe_string(getattr(my_tag, "Name", "")).strip()
                if name:
                    tags.append(name)
            continue

        name = safe_string(getattr(value, "Name", "")).strip()
        if not name:
            name = safe_string(getattr(value, "TagName", "")).strip()
        if not name:
            my_tag = getattr(value, "MyTag", None)
            name = safe_string(getattr(my_tag, "Name", "")).strip()
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
        "hot_cues_cnt": collect(hot_cues=True),
        "memory_cues_cnt": collect(hot_cues=False),
    }

