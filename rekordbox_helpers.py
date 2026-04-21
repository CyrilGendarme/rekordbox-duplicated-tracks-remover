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
