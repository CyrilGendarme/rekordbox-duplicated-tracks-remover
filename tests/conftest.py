"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_rekordbox_content():
    """Create a mock Rekordbox content object."""
    content = Mock()
    content.Title = "Test Track"
    content.ID = "12345"
    content.FolderPath = "/test/path/track.mp3"
    content.FileNameL = "track.mp3"
    
    # Mock Artist object
    artist = Mock()
    artist.Name = "Test Artist"
    content.Artist = artist
    
    return content


@pytest.fixture
def mock_rekordbox_db():
    """Create a mock Rekordbox database."""
    db = Mock()
    db.get_content = Mock(return_value=None)
    db.delete = Mock()
    db.commit = Mock()
    db.close = Mock()
    return db


@pytest.fixture
def sample_duplicates():
    """Create sample duplicate groups for testing."""
    return [
        [
            {
                "title": "Track One",
                "artist": "Artist A",
                "id": "1",
                "path": "/path/to/track1.mp3",
            },
            {
                "title": "Track One",
                "artist": "Artist A",
                "id": "2",
                "path": "/path/to/track1_duplicate.mp3",
            },
        ],
        [
            {
                "title": "Track Two",
                "artist": "Artist B",
                "id": "3",
                "path": "/path/to/track2.mp3",
            },
            {
                "title": "Track Two",
                "artist": "Artist B",
                "id": "4",
                "path": "/path/to/track2_copy.mp3",
            },
        ],
    ]


@pytest.fixture
def audio_files(temp_dir):
    """Create temporary audio files for testing."""
    files = []
    for ext in [".mp3", ".m4a", ".flac"]:
        file_path = temp_dir / f"test_audio{ext}"
        file_path.write_text("dummy audio content")
        files.append(file_path)
    return files
