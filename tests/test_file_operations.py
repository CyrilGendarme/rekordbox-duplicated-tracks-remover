"""Tests for file_operations module."""

from __future__ import annotations

import io
from pathlib import Path
from unittest.mock import patch

from file_operations import log_file_operation, safe_delete_file

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
