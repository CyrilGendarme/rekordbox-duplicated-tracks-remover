"""Tests for path_utils module."""

from __future__ import annotations

from pathlib import Path

import pytest

from path_utils import find_first_dropbox_file, path_under_directory


class TestPathUnderDirectory:
    """Tests for the path_under_directory function."""

    def test_path_under_directory_true(self, temp_dir):
        """Test when path is under directory."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        test_file = subdir / "file.txt"
        
        result = path_under_directory(test_file, temp_dir)
        assert result is True

    def test_path_under_directory_false(self, temp_dir):
        """Test when path is not under directory."""
        other_dir = Path(temp_dir).parent / "other_dir"
        
        result = path_under_directory(other_dir, temp_dir)
        assert result is False

    def test_path_under_directory_same(self, temp_dir):
        """Test when path is the same as directory."""
        result = path_under_directory(temp_dir, temp_dir)
        assert result is True

    def test_path_under_directory_nested(self, temp_dir):
        """Test with deeply nested path."""
        nested = temp_dir / "a" / "b" / "c" / "file.txt"
        
        result = path_under_directory(nested, temp_dir)
        assert result is True


class TestFindFirstDropboxFile:
    """Tests for the find_first_dropbox_file function."""

    def test_find_first_dropbox_file_exists(self, temp_dir):
        """Test finding an existing file."""
        test_file = temp_dir / "track.mp3"
        test_file.write_text("audio content")
        
        result = find_first_dropbox_file(str(temp_dir), "track.mp3")
        
        assert result is not None
        assert "track.mp3" in result

    def test_find_first_dropbox_file_not_exists(self, temp_dir):
        """Test when file doesn't exist."""
        result = find_first_dropbox_file(str(temp_dir), "nonexistent.mp3")
        assert result is None

    def test_find_first_dropbox_file_nested(self, temp_dir):
        """Test finding file in nested directory."""
        subdir = temp_dir / "subdir" / "nested"
        subdir.mkdir(parents=True)
        test_file = subdir / "track.mp3"
        test_file.write_text("audio content")
        
        result = find_first_dropbox_file(str(temp_dir), "track.mp3")
        
        assert result is not None
        assert "track.mp3" in result

    def test_find_first_dropbox_file_empty_filename(self, temp_dir):
        """Test with empty filename."""
        result = find_first_dropbox_file(str(temp_dir), "")
        assert result is None

    def test_find_first_dropbox_file_nonexistent_dir(self):
        """Test with non-existent directory."""
        result = find_first_dropbox_file("/nonexistent/dir", "file.mp3")
        assert result is None

    def test_find_first_dropbox_file_multiple_matches(self, temp_dir):
        """Test when multiple files match (returns first)."""
        (temp_dir / "track.mp3").write_text("audio1")
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "track.mp3").write_text("audio2")
        
        result = find_first_dropbox_file(str(temp_dir), "track.mp3")
        
        assert result is not None
        assert "track.mp3" in result

    def test_find_first_dropbox_file_ignores_directories(self, temp_dir):
        """Test that it ignores directories with matching names."""
        # Create a directory with the target name
        (temp_dir / "track.mp3").mkdir()
        
        result = find_first_dropbox_file(str(temp_dir), "track.mp3")
        assert result is None
