"""Tests for rekordbox_helpers module."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from rekordbox_helpers import get_artist_name, get_track_id, get_track_path


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


class TestGetTrackId:
    """Tests for the get_track_id function."""

    def test_get_track_id_from_id(self):
        """Test getting track ID from ID attribute."""
        content = Mock()
        content.ID = 12345
        
        result = get_track_id(content)
        assert result == "12345"

    def test_get_track_id_from_track_id(self):
        """Test getting track ID from TrackID attribute."""
        content = Mock()
        content.ID = None
        content.TrackID = 67890
        
        result = get_track_id(content)
        assert result == "67890"

    def test_get_track_id_from_content_id(self):
        """Test getting track ID from ContentID attribute."""
        content = Mock()
        content.ID = None
        content.TrackID = None
        content.ContentID = "abc123"
        
        result = get_track_id(content)
        assert result == "abc123"

    def test_get_track_id_fallback(self):
        """Test fallback when no ID found."""
        content = Mock()
        content.ID = None
        content.TrackID = None
        content.ContentID = None
        
        result = get_track_id(content)
        assert result == "?"


class TestGetTrackPath:
    """Tests for the get_track_path function."""

    def test_get_track_path_from_src_path(self):
        """Test getting path from SrcPath."""
        content = Mock()
        content.SrcPath = "/path/to/track.mp3"
        
        result = get_track_path(content)
        assert result == "/path/to/track.mp3"

    def test_get_track_path_from_folder_path(self):
        """Test getting path from FolderPath."""
        content = Mock()
        content.SrcPath = None
        content.SourcePath = None
        content.OriginalPath = None
        content.FolderPath = "/folder/track.mp3"
        
        result = get_track_path(content)
        assert result == "/folder/track.mp3"

    def test_get_track_path_priority_order(self):
        """Test that SrcPath has priority over other fields."""
        content = Mock()
        content.SrcPath = "/src/track.mp3"
        content.FolderPath = "/folder/track.mp3"
        
        result = get_track_path(content)
        assert result == "/src/track.mp3"

    def test_get_track_path_empty(self):
        """Test getting path when no path fields exist."""
        content = Mock()
        content.SrcPath = None
        content.SourcePath = None
        content.OriginalPath = None
        content.FolderPath = None
        content.Path = None
        content.FileNameL = None
        
        result = get_track_path(content)
        assert result == ""
