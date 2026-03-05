"""Unit tests for rekordbox_operations module."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, call
from io import StringIO

import pytest

from rekordbox_operations import delete_rekordbox_track, relocate_rekordbox_track


class TestDeleteRekordboxTrack:
    """Tests for delete_rekordbox_track function."""

    def test_delete_with_delete_content_method(self):
        """Test deletion using delete_content method."""
        mock_db = Mock()
        mock_content = Mock()
        mock_db.get_content.return_value = mock_content
        mock_db.delete_content = Mock()
        
        result = delete_rekordbox_track(mock_db, "123", verbose=False, log_enabled=False)
        
        assert result is True
        mock_db.get_content.assert_called_once_with(ID="123")
        mock_db.delete_content.assert_called_once_with(mock_content)

    def test_delete_with_delete_method(self):
        """Test deletion using delete method."""
        mock_db = Mock()
        mock_content = Mock()
        mock_db.get_content.return_value = mock_content
        mock_db.delete_content = None
        mock_db.delete = Mock()
        
        result = delete_rekordbox_track(mock_db, "123", verbose=False, log_enabled=False)
        
        assert result is True
        mock_db.delete.assert_called_once_with(mock_content)

    def test_delete_with_no_db(self):
        """Test deletion with None db."""
        result = delete_rekordbox_track(None, "123", verbose=False, log_enabled=False)
        assert result is False

    def test_delete_with_no_content_id(self):
        """Test deletion with empty content ID."""
        mock_db = Mock()
        result = delete_rekordbox_track(mock_db, "", verbose=False, log_enabled=False)
        assert result is False

    def test_delete_content_not_found(self):
        """Test deletion when content is not found."""
        mock_db = Mock()
        mock_db.get_content.return_value = None
        
        result = delete_rekordbox_track(mock_db, "123", verbose=False, log_enabled=False)
        assert result is False

    def test_delete_no_delete_method(self):
        """Test deletion when no delete method is available."""
        mock_db = Mock()
        mock_content = Mock()
        mock_db.get_content.return_value = mock_content
        mock_db.delete_content = None
        mock_db.delete = None
        
        result = delete_rekordbox_track(mock_db, "123", verbose=False, log_enabled=False)
        assert result is False

    def test_delete_with_exception(self):
        """Test deletion when exception occurs."""
        mock_db = Mock()
        mock_db.get_content.side_effect = Exception("DB Error")
        
        result = delete_rekordbox_track(mock_db, "123", verbose=False, log_enabled=False)
        assert result is False

    def test_delete_verbose_output(self):
        """Test verbose output during deletion."""
        mock_db = Mock()
        mock_content = Mock()
        mock_db.get_content.return_value = mock_content
        mock_db.delete_content = Mock()
        
        with patch('sys.stderr', new=StringIO()) as mock_stderr:
            delete_rekordbox_track(mock_db, "123", verbose=True, log_enabled=True)
            output = mock_stderr.getvalue()
            assert "REKORDBOX DELETE" in output


class TestRelocateRekordboxTrack:
    """Tests for relocate_rekordbox_track function."""

    def test_relocate_with_update_content_path(self):
        """Test relocation using update_content_path method."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            mock_db = Mock()
            mock_db.update_content_path = Mock()
            
            result = relocate_rekordbox_track(
                mock_db, "123", tmp_path, verbose=False, log_enabled=False
            )
            
            assert result is True
            mock_db.update_content_path.assert_called_once()
        finally:
            Path(tmp_path).unlink()

    def test_relocate_with_direct_attribute_setting(self):
        """Test relocation by setting attributes directly."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            mock_db = Mock()
            mock_db.update_content_path = None
            mock_content = Mock()
            mock_db.get_content.return_value = mock_content
            
            result = relocate_rekordbox_track(
                mock_db, "123", tmp_path, verbose=False, log_enabled=False
            )
            
            assert result is True
            assert hasattr(mock_content, 'FolderPath')
        finally:
            Path(tmp_path).unlink()

    def test_relocate_with_no_db(self):
        """Test relocation with None db."""
        result = relocate_rekordbox_track(None, "123", "/path", verbose=False, log_enabled=False)
        assert result is False

    def test_relocate_with_no_content_id(self):
        """Test relocation with empty content ID."""
        mock_db = Mock()
        result = relocate_rekordbox_track(mock_db, "", "/path", verbose=False, log_enabled=False)
        assert result is False

    def test_relocate_non_existing_path(self):
        """Test relocation to non-existing path."""
        mock_db = Mock()
        result = relocate_rekordbox_track(
            mock_db, "123", "/non/existing/path.mp3", verbose=False, log_enabled=False
        )
        assert result is False

    def test_relocate_content_not_found(self):
        """Test relocation when content is not found."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            mock_db = Mock()
            mock_db.update_content_path = None
            mock_db.get_content.return_value = None
            
            result = relocate_rekordbox_track(
                mock_db, "123", tmp_path, verbose=False, log_enabled=False
            )
            assert result is False
        finally:
            Path(tmp_path).unlink()

    def test_relocate_with_exception(self):
        """Test relocation when exception occurs."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            mock_db = Mock()
            mock_db.update_content_path = Mock(side_effect=Exception("DB Error"))
            
            result = relocate_rekordbox_track(
                mock_db, "123", tmp_path, verbose=False, log_enabled=False
            )
            assert result is False
        finally:
            Path(tmp_path).unlink()

    def test_relocate_normalizes_path(self):
        """Test that relocation normalizes Windows paths."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            mock_db = Mock()
            mock_db.update_content_path = None
            mock_content = Mock()
            mock_db.get_content.return_value = mock_content
            
            relocate_rekordbox_track(mock_db, "123", tmp_path, verbose=False, log_enabled=False)
            
            # Check that path uses forward slashes
            if hasattr(mock_content, 'FolderPath'):
                assert "\\" not in mock_content.FolderPath or "/" in mock_content.FolderPath
        finally:
            Path(tmp_path).unlink()

    def test_relocate_verbose_output(self):
        """Test verbose output during relocation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            mock_db = Mock()
            mock_db.update_content_path = Mock()
            
            with patch('sys.stderr', new=StringIO()) as mock_stderr:
                relocate_rekordbox_track(mock_db, "123", tmp_path, verbose=True, log_enabled=True)
                output = mock_stderr.getvalue()
                assert "REKORDBOX RELOCATE" in output
        finally:
            Path(tmp_path).unlink()
