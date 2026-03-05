"""Unit tests for cleanup module."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, call

import pytest

from cleanup import perform_cleanup, select_surviving_dropbox_path


class TestSelectSurvivingDropboxPath:
    """Tests for select_surviving_dropbox_path function."""

    def test_select_existing_file_in_dropbox(self):
        """Test selecting existing file in Dropbox directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            test_file = tmp_path / "song.mp3"
            test_file.touch()
            
            non_matching = [{"path": str(test_file)}]
            result = select_surviving_dropbox_path(non_matching, tmp_dir)
            
            assert result == str(test_file)

    def test_select_with_no_path(self):
        """Test when non-matching items have no path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            non_matching = [{"path": ""}]
            result = select_surviving_dropbox_path(non_matching, tmp_dir)
            assert result is None

    def test_select_from_multiple_candidates(self):
        """Test selecting from multiple non-matching items."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            file1 = tmp_path / "song1.mp3"
            file1.touch()
            file2 = tmp_path / "song2.mp3"
            file2.touch()
            
            non_matching = [
                {"path": str(file1)},
                {"path": str(file2)}
            ]
            result = select_surviving_dropbox_path(non_matching, tmp_dir)
            
            # Should return the first valid one
            assert result == str(file1)

    def test_select_finds_file_by_name(self):
        """Test finding file by name when path doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            actual_file = tmp_path / "song.mp3"
            actual_file.touch()
            
            # Non-matching has wrong path but correct filename
            non_matching = [{"path": "/wrong/path/song.mp3"}]
            result = select_surviving_dropbox_path(non_matching, tmp_dir)
            
            assert result == str(actual_file)

    def test_select_with_non_existing_files(self):
        """Test when no files exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            non_matching = [{"path": "/non/existing/file.mp3"}]
            result = select_surviving_dropbox_path(non_matching, tmp_dir)
            assert result is None


class TestPerformCleanup:
    """Tests for perform_cleanup function."""

    @patch('cleanup.safe_delete_file')
    @patch('cleanup.delete_rekordbox_track')
    @patch('cleanup.relocate_rekordbox_track')
    @patch('cleanup.find_first_dropbox_file')
    def test_cleanup_all_steps(
        self,
        mock_find_dropbox,
        mock_relocate,
        mock_delete_track,
        mock_delete_file
    ):
        """Test complete cleanup workflow."""
        with tempfile.TemporaryDirectory() as dropbox_dir:
            dropbox_path = Path(dropbox_dir)
            surviving_file = dropbox_path / "surviving.mp3"
            surviving_file.touch()
            
            matched_item = {"id": "123", "artist": "Artist", "title": "Title"}
            non_matching = [{"id": "456", "artist": "Artist", "title": "Title", "path": str(surviving_file)}]
            youtube_path = "/youtube/song.mp3"
            
            mock_find_dropbox.return_value = None
            mock_delete_file.return_value = True
            mock_delete_track.return_value = True
            mock_relocate.return_value = True
            
            perform_cleanup(
                matched_item,
                non_matching,
                youtube_path,
                dropbox_dir,
                Mock(),
                test_mode=False,
                titles_only=True
            )
            
            # Verify all steps called
            mock_delete_file.assert_called()
            mock_delete_track.assert_called()
            mock_relocate.assert_called()

    @patch('cleanup.safe_delete_file')
    @patch('cleanup.delete_rekordbox_track')
    @patch('cleanup.find_first_dropbox_file')
    def test_cleanup_deletes_youtube_file(
        self,
        mock_find_dropbox,
        mock_delete_track,
        mock_delete_file
    ):
        """Test that YouTube file is deleted."""
        with tempfile.TemporaryDirectory() as dropbox_dir:
            matched_item = {"id": "123", "artist": "Artist", "title": "Title"}
            non_matching = []
            youtube_path = "/youtube/song.mp3"
            
            mock_find_dropbox.return_value = None
            mock_delete_file.return_value = True
            
            perform_cleanup(
                matched_item,
                non_matching,
                youtube_path,
                dropbox_dir,
                Mock(),
                test_mode=False,
                titles_only=True
            )
            
            # Check that YouTube file deletion was called
            calls = mock_delete_file.call_args_list
            assert any(youtube_path in str(call) for call in calls)

    @patch('cleanup.safe_delete_file')
    @patch('cleanup.delete_rekordbox_track')
    @patch('cleanup.find_first_dropbox_file')
    def test_cleanup_deletes_non_matching_tracks(
        self,
        mock_find_dropbox,
        mock_delete_track,
        mock_delete_file
    ):
        """Test that non-matching tracks are deleted from DB."""
        with tempfile.TemporaryDirectory() as dropbox_dir:
            matched_item = {"id": "123", "artist": "Artist", "title": "Title"}
            non_matching = [
                {"id": "456", "artist": "Artist", "title": "Title", "path": ""},
                {"id": "789", "artist": "Artist", "title": "Title", "path": ""}
            ]
            youtube_path = "/youtube/song.mp3"
            
            mock_find_dropbox.return_value = None
            mock_delete_track.return_value = True
            
            mock_db = Mock()
            perform_cleanup(
                matched_item,
                non_matching,
                youtube_path,
                dropbox_dir,
                mock_db,
                test_mode=False,
                titles_only=True
            )
            
            # Should delete each non-matching track
            assert mock_delete_track.call_count == 2

    @patch('cleanup.safe_delete_file')
    @patch('cleanup.delete_rekordbox_track')
    @patch('cleanup.relocate_rekordbox_track')
    @patch('cleanup.find_first_dropbox_file')
    def test_cleanup_relocates_kept_track(
        self,
        mock_find_dropbox,
        mock_relocate,
        mock_delete_track,
        mock_delete_file
    ):
        """Test that kept track is relocated."""
        with tempfile.TemporaryDirectory() as dropbox_dir:
            dropbox_path = Path(dropbox_dir)
            surviving_file = dropbox_path / "surviving.mp3"
            surviving_file.touch()
            
            matched_item = {"id": "123", "artist": "Artist", "title": "Title"}
            non_matching = [{"id": "456", "artist": "Artist", "title": "Title", "path": str(surviving_file)}]
            youtube_path = "/youtube/song.mp3"
            
            mock_find_dropbox.return_value = None
            mock_relocate.return_value = True
            
            mock_db = Mock()
            perform_cleanup(
                matched_item,
                non_matching,
                youtube_path,
                dropbox_dir,
                mock_db,
                test_mode=False,
                titles_only=True
            )
            
            # Should relocate the matched track
            mock_relocate.assert_called_once()
            args = mock_relocate.call_args
            assert args[0][1] == "123"  # content_id
            assert str(surviving_file) in str(args[0][2])  # new_path

    @patch('cleanup.safe_delete_file')
    @patch('cleanup.delete_rekordbox_track')
    @patch('cleanup.find_first_dropbox_file')
    def test_cleanup_skips_surviving_file(
        self,
        mock_find_dropbox,
        mock_delete_track,
        mock_delete_file
    ):
        """Test that surviving Dropbox file is not deleted."""
        with tempfile.TemporaryDirectory() as dropbox_dir:
            dropbox_path = Path(dropbox_dir)
            surviving_file = dropbox_path / "surviving.mp3"
            surviving_file.touch()
            
            matched_item = {"id": "123", "artist": "Artist", "title": "Title"}
            non_matching = [{"id": "456", "artist": "Artist", "title": "Title", "path": str(surviving_file)}]
            youtube_path = "/youtube/surviving.mp3"
            
            # find_first_dropbox_file returns the surviving file
            mock_find_dropbox.return_value = str(surviving_file)
            
            perform_cleanup(
                matched_item,
                non_matching,
                youtube_path,
                dropbox_dir,
                Mock(),
                test_mode=False,
                titles_only=True
            )
            
            # Check that surviving file was not deleted
            delete_calls = [str(call) for call in mock_delete_file.call_args_list]
            # The surviving file shouldn't be in the delete calls for Dropbox cleanup
            # (only YouTube file should be deleted)

    @patch('cleanup.safe_delete_file')
    @patch('cleanup.delete_rekordbox_track')
    def test_cleanup_titles_only_mode(
        self,
        mock_delete_track,
        mock_delete_file
    ):
        """Test cleanup with titles_only mode (no console output)."""
        with tempfile.TemporaryDirectory() as dropbox_dir:
            matched_item = {"id": "123", "artist": "Artist", "title": "Title"}
            non_matching = []
            youtube_path = "/youtube/song.mp3"
            
            with patch('builtins.print') as mock_print:
                perform_cleanup(
                    matched_item,
                    non_matching,
                    youtube_path,
                    dropbox_dir,
                    Mock(),
                    test_mode=False,
                    titles_only=True
                )
                
                # Should not print progress messages in titles_only mode
                assert mock_print.call_count == 0
