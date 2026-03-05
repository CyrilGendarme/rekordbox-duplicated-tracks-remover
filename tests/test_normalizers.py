"""Tests for normalizers module."""

from __future__ import annotations

import pytest

from normalizers import (
    normalize,
    normalize_filename,
    normalize_path_for_compare,
    safe_string,
)


class TestNormalize:
    """Tests for the normalize function."""

    def test_normalize_case_insensitive(self):
        """Test case-insensitive normalization."""
        result = normalize("Test String", case_sensitive=False)
        assert result == "test string"

    def test_normalize_case_sensitive(self):
        """Test case-sensitive normalization."""
        result = normalize("Test String", case_sensitive=True)
        assert result == "Test String"

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        result = normalize("  Multiple   Spaces  ", case_sensitive=False)
        assert result == "multiple spaces"

    def test_normalize_empty_string(self):
        """Test normalization of empty string."""
        result = normalize("", case_sensitive=False)
        assert result == ""


class TestSafeString:
    """Tests for the safe_string function."""

    def test_safe_string_with_string(self):
        """Test safe_string with a regular string."""
        result = safe_string("test")
        assert result == "test"

    def test_safe_string_with_none(self):
        """Test safe_string with None."""
        result = safe_string(None)
        assert result == ""

    def test_safe_string_with_number(self):
        """Test safe_string with a number."""
        result = safe_string(123)
        assert result == "123"

    def test_safe_string_with_whitespace(self):
        """Test safe_string strips whitespace."""
        result = safe_string("  test  ")
        assert result == "test"


class TestNormalizeFilename:
    """Tests for the normalize_filename function."""

    def test_normalize_filename_removes_extension(self):
        """Test that file extension is removed."""
        result = normalize_filename("track.mp3")
        assert result == "track"

    def test_normalize_filename_lowercase(self):
        """Test that filename is converted to lowercase."""
        result = normalize_filename("TRACK.MP3")
        assert result == "track"

    def test_normalize_filename_removes_special_chars(self):
        """Test that special characters are removed."""
        result = normalize_filename("track-name_v2.0!.mp3")
        assert result == "tracknamev20"

    def test_normalize_filename_normalizes_whitespace(self):
        """Test that whitespace is normalized."""
        result = normalize_filename("track  name   with spaces.mp3")
        assert result == "track name with spaces"

    def test_normalize_filename_complex(self):
        """Test normalization of complex filename."""
        result = normalize_filename("Artist - Track (Original Mix) [Label].mp3")
        assert result == "artist track original mix label"


class TestNormalizePathForCompare:
    """Tests for the normalize_path_for_compare function."""

    def test_normalize_path_forward_slashes(self):
        """Test that backslashes are converted to forward slashes."""
        result = normalize_path_for_compare(r"C:\Users\Test\file.mp3")
        assert result == "c:/users/test/file.mp3"

    def test_normalize_path_lowercase(self):
        """Test that path is converted to lowercase."""
        result = normalize_path_for_compare("/Path/To/File.MP3")
        assert result == "/path/to/file.mp3"

    def test_normalize_path_trailing_slash(self):
        """Test that trailing slashes are removed."""
        result = normalize_path_for_compare("/path/to/dir/")
        assert result == "/path/to/dir"

    def test_normalize_path_with_pathlib(self):
        """Test normalization with Path object."""
        from pathlib import Path
        result = normalize_path_for_compare(Path("C:\\Users\\Test"))
        assert "/" in result  # Should contain forward slashes
        assert result == result.casefold()  # Should be lowercase
