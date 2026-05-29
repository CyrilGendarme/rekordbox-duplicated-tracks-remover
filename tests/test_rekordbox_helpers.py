"""Tests for rekordbox_helpers module."""

from __future__ import annotations

from unittest.mock import Mock

from rekordbox_helpers import get_artist_name

class TestGetArtistName:
    """Tests for the get_artist_name function."""

    def test_get_artist_name_from_artist_object(self):
        """Test getting artist name from Artist object."""
        content = Mock()
        artist = Mock()
        artist.Name = "Test Artist"
        content.Artist = artist

        result = get_artist_name(content)
        assert result == "Test Artist"

    def test_get_artist_name_from_artist_name_field(self):
        """Test getting artist name from ArtistName field."""
        content = Mock()
        content.Artist = None
        content.ArtistName = "Direct Artist"

        result = get_artist_name(content)
        assert result == "Direct Artist"

    def test_get_artist_name_with_whitespace(self):
        """Test that whitespace is stripped."""
        content = Mock()
        artist = Mock()
        artist.Name = "  Test Artist  "
        content.Artist = artist

        result = get_artist_name(content)
        assert result == "Test Artist"

    def test_get_artist_name_empty(self):
        """Test getting artist name when empty."""
        content = Mock()
        content.Artist = None
        content.ArtistName = ""

        result = get_artist_name(content)
        assert result == ""

    def test_get_artist_name_missing_name_on_artist_object(self):
        """Test empty result when the Artist object has no usable name."""
        content = Mock()
        artist = Mock()
        artist.Name = None
        content.Artist = artist
        content.ArtistName = "Ignored ArtistName"

        result = get_artist_name(content)
        assert result == ""
