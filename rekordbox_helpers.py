"""Helper functions to extract data from Rekordbox content objects."""

from __future__ import annotations

from typing import Any

from normalizers import safe_string


def get_artist_name(content: Any) -> str:
    """Extract artist name from a Rekordbox content object."""
    artist = getattr(content, "Artist", None)
    if artist is not None:
        return safe_string(getattr(artist, "Name", ""))
    return safe_string(getattr(content, "ArtistName", ""))


def get_track_id(content: Any) -> str:
    """Extract track ID from a Rekordbox content object."""
    for attr in ("ID", "TrackID", "ContentID"):
        value = getattr(content, attr, None)
        if value is not None:
            return str(value)
    return "?"


def get_track_path(content: Any) -> str:
    """Extract file path from a Rekordbox content object."""
    # Prefer source/original path fields when available, then fallback.
    for attr in ("SrcPath", "SourcePath", "OriginalPath", "FolderPath", "Path", "FileNameL"):
        value = getattr(content, attr, None)
        if value:
            return str(value)
    return ""
