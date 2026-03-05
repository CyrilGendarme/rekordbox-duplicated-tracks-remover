"""Tests for file_operations module."""

from __future__ import annotations

import io
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from file_operations import log_file_operation, safe_delete_file, scan_audio_files


class TestLogFileOperation:
    """Tests for the log_file_operation function."""

    def test_log_file_operation_enabled(self):
        """Test logging when enabled."""
        captured_output = io.StringIO()
        with patch("sys.stderr", captured_output):
            log_file_operation("TEST_OP", "/path/to/file.mp3", enabled=True)
        
        output = captured_output.getvalue()
        assert "TEST_OP" in output
        assert "/path/to/file.mp3" in output

    def test_log_file_operation_disabled(self):
        """Test logging when disabled."""
        captured_output = io.StringIO()
        with patch("sys.stderr", captured_output):
            log_file_operation("TEST_OP", "/path/to/file.mp3", enabled=False)
        
        output = captured_output.getvalue()
        assert output == ""


class TestSafeDeleteFile:
    """Tests for the safe_delete_file function."""

    def test_safe_delete_file_success(self, temp_dir):
        """Test successful file deletion."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        
        result = safe_delete_file(str(test_file), log_enabled=False, verbose=False)
        
        assert result is True
        assert not test_file.exists()

    def test_safe_delete_file_not_found(self):
        """Test deletion of non-existent file."""
        result = safe_delete_file("/nonexistent/file.txt", log_enabled=False, verbose=False)
        assert result is False

    def test_safe_delete_file_with_reason(self, temp_dir):
        """Test deletion with reason logged."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        captured_output = io.StringIO()
        with patch("sys.stderr", captured_output):
            safe_delete_file(str(test_file), reason="test cleanup", log_enabled=True, verbose=False)
        
        output = captured_output.getvalue()
        assert "DELETE" in output
        assert "test cleanup" in output

    def test_safe_delete_file_permission_error(self, temp_dir):
        """Test deletion with permission error."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Mock unlink to raise permission error
        with patch.object(Path, "unlink", side_effect=PermissionError("Access denied")):
            result = safe_delete_file(str(test_file), log_enabled=False, verbose=False)
        
        assert result is False


class TestScanAudioFiles:
    """Tests for the scan_audio_files function."""

    def test_scan_audio_files_success(self, temp_dir):
        """Test scanning directory with audio files."""
        # Create test audio files
        (temp_dir / "track1.mp3").write_text("audio1")
        (temp_dir / "track2.m4a").write_text("audio2")
        (temp_dir / "track3.flac").write_text("audio3")
        (temp_dir / "readme.txt").write_text("not audio")
        
        result = scan_audio_files(temp_dir)
        
        assert len(result) == 3
        assert "track1.mp3" in result
        assert "track2.m4a" in result
        assert "track3.flac" in result
        assert "readme.txt" not in result

    def test_scan_audio_files_nested(self, temp_dir):
        """Test scanning nested directories."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        (temp_dir / "track1.mp3").write_text("audio1")
        (subdir / "track2.mp3").write_text("audio2")
        
        result = scan_audio_files(temp_dir)
        
        assert len(result) == 2
        assert "track1.mp3" in result
        assert "track2.mp3" in result

    def test_scan_audio_files_empty_directory(self, temp_dir):
        """Test scanning empty directory."""
        result = scan_audio_files(temp_dir)
        assert len(result) == 0

    def test_scan_audio_files_nonexistent_directory(self):
        """Test scanning non-existent directory."""
        result = scan_audio_files("/nonexistent/directory")
        assert len(result) == 0

    def test_scan_audio_files_various_extensions(self, temp_dir):
        """Test scanning with various audio extensions."""
        extensions = [".mp3", ".m4a", ".aac", ".flac", ".wav", ".ogg", ".wma"]
        for ext in extensions:
            (temp_dir / f"track{ext}").write_text("audio")
        
        result = scan_audio_files(temp_dir)
        assert len(result) == len(extensions)

    def test_scan_audio_files_case_insensitive(self, temp_dir):
        """Test that extension matching is case-insensitive."""
        (temp_dir / "track.MP3").write_text("audio")
        (temp_dir / "track2.M4A").write_text("audio")
        
        result = scan_audio_files(temp_dir)
        assert len(result) == 2
