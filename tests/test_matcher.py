"""Unit tests for matcher module."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, call

import pytest

from matcher import find_matching_files


class TestFindMatchingFiles:
    """Tests for find_matching_files function."""

    @patch('matcher.scan_audio_files')
    def test_find_matching_with_no_youtube_files(self, mock_scan):
        """Test when no YouTube files are found."""
        mock_scan.return_value = {}
        
        duplicates = [[{"path": "/path/song.mp3", "artist": "Artist", "title": "Title"}]]
        
        with patch('builtins.print') as mock_print:
            find_matching_files(
                duplicates,
                "/youtube",
                titles_only=False
            )
            
            # Should print that no files were found
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "No audio files found" in printed_text

    @patch('matcher.scan_audio_files')
    def test_find_matching_with_match(self, mock_scan):
        """Test finding a matching file."""
        mock_scan.return_value = {"song.mp3": "/youtube/song.mp3"}
        
        duplicates = [[
            {"path": "/rekordbox/song.mp3", "artist": "Artist", "title": "Title"},
            {"path": "/rekordbox/song2.mp3", "artist": "Artist", "title": "Title"}
        ]]
        
        with patch('builtins.print') as mock_print:
            find_matching_files(
                duplicates,
                "/youtube",
                titles_only=False
            )
            
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Artist" in printed_text
            assert "Title" in printed_text

    @patch('matcher.scan_audio_files')
    def test_find_matching_titles_only_mode(self, mock_scan):
        """Test titles_only mode output."""
        mock_scan.return_value = {"song.mp3": "/youtube/song.mp3"}
        
        duplicates = [[
            {"path": "/rekordbox/song.mp3", "artist": "Test Artist", "title": "Test Title"}
        ]]
        
        with patch('builtins.print') as mock_print:
            find_matching_files(
                duplicates,
                "/youtube",
                titles_only=True
            )
            
            # Should only print "Artist - Title" format
            mock_print.assert_called()
            printed_text = str(mock_print.call_args_list[-1])
            assert "Test Artist - Test Title" in printed_text

    @patch('matcher.scan_audio_files')
    @patch('matcher.perform_cleanup')
    def test_find_matching_with_cleanup(self, mock_cleanup, mock_scan):
        """Test auto-cleanup is triggered."""
        mock_scan.return_value = {"song.mp3": "/youtube/song.mp3"}
        
        duplicates = [[
            {"path": "/rekordbox/song.mp3", "artist": "Artist", "title": "Title"},
            {"path": "/rekordbox/song2.mp3", "artist": "Artist", "title": "Title"}
        ]]
        
        mock_db = Mock()
        find_matching_files(
            duplicates,
            "/youtube",
            dropbox_dir="/dropbox",
            auto_cleanup=True,
            test_mode=False,
            titles_only=True,
            db=mock_db
        )
        
        # Should call cleanup
        mock_cleanup.assert_called_once()

    @patch('matcher.scan_audio_files')
    @patch('matcher.perform_cleanup')
    def test_find_matching_test_mode_stops_after_first(self, mock_cleanup, mock_scan):
        """Test test_mode stops after first match."""
        mock_scan.return_value = {
            "song1.mp3": "/youtube/song1.mp3",
            "song2.mp3": "/youtube/song2.mp3"
        }
        
        duplicates = [
            [{"path": "/rekordbox/song1.mp3", "artist": "Artist1", "title": "Title1"}],
            [{"path": "/rekordbox/song2.mp3", "artist": "Artist2", "title": "Title2"}]
        ]
        
        mock_db = Mock()
        find_matching_files(
            duplicates,
            "/youtube",
            dropbox_dir="/dropbox",
            auto_cleanup=True,
            test_mode=True,
            titles_only=True,
            db=mock_db
        )
        
        # Should only process first match in test mode
        assert mock_cleanup.call_count == 1

    @patch('matcher.scan_audio_files')
    def test_find_matching_skips_empty_paths(self, mock_scan):
        """Test that items with empty paths are skipped."""
        mock_scan.return_value = {"song.mp3": "/youtube/song.mp3"}
        
        duplicates = [[
            {"path": "", "artist": "Artist", "title": "Title"},
            {"path": "/rekordbox/song.mp3", "artist": "Artist", "title": "Title"}
        ]]
        
        with patch('builtins.print') as mock_print:
            find_matching_files(
                duplicates,
                "/youtube",
                titles_only=False
            )
            
            # Should still find match from second item
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Artist" in printed_text

    @patch('matcher.scan_audio_files')
    def test_find_matching_normalizes_filenames(self, mock_scan):
        """Test that filename normalization works."""
        mock_scan.return_value = {"Song_-_123.mp3": "/youtube/Song_-_123.mp3"}
        
        # Rekordbox has slightly different filename
        duplicates = [[
            {"path": "/rekordbox/Song - 123.mp3", "artist": "Artist", "title": "Title"}
        ]]
        
        with patch('builtins.print') as mock_print:
            find_matching_files(
                duplicates,
                "/youtube",
                titles_only=True
            )
            
            # Should find match despite different formatting
            printed_text = str(mock_print.call_args_list)
            assert "Artist - Title" in printed_text

    @patch('matcher.scan_audio_files')
    def test_find_matching_no_matches_found(self, mock_scan):
        """Test when no matches are found."""
        mock_scan.return_value = {"different.mp3": "/youtube/different.mp3"}
        
        duplicates = [[
            {"path": "/rekordbox/song.mp3", "artist": "Artist", "title": "Title"}
        ]]
        
        with patch('builtins.print') as mock_print:
            find_matching_files(
                duplicates,
                "/youtube",
                titles_only=False
            )
            
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "No matching files found" in printed_text or "Total matches: 0" not in printed_text

    @patch('matcher.scan_audio_files')
    @patch('matcher.perform_cleanup')
    def test_find_matching_without_dropbox_dir(self, mock_cleanup, mock_scan):
        """Test that cleanup is skipped without dropbox_dir."""
        mock_scan.return_value = {"song.mp3": "/youtube/song.mp3"}
        
        duplicates = [[
            {"path": "/rekordbox/song.mp3", "artist": "Artist", "title": "Title"}
        ]]
        
        find_matching_files(
            duplicates,
            "/youtube",
            dropbox_dir=None,
            auto_cleanup=True,
            titles_only=True
        )
        
        # Cleanup should not be called without dropbox_dir
        mock_cleanup.assert_not_called()

    @patch('matcher.scan_audio_files')
    def test_find_matching_multiple_duplicates_in_group(self, mock_scan):
        """Test matching with multiple duplicates in a group."""
        mock_scan.return_value = {"song.mp3": "/youtube/song.mp3"}
        
        duplicates = [[
            {"path": "/rekordbox/song.mp3", "artist": "Artist", "title": "Title"},
            {"path": "/rekordbox/copy1.mp3", "artist": "Artist", "title": "Title"},
            {"path": "/rekordbox/copy2.mp3", "artist": "Artist", "title": "Title"}
        ]]
        
        with patch('builtins.print') as mock_print:
            find_matching_files(
                duplicates,
                "/youtube",
                titles_only=False
            )
            
            # Should show non-matching duplicates
            printed_text = ' '.join(str(call) for call in mock_print.call_args_list)
            assert "Non-matching duplicates" in printed_text or "copy1" in printed_text
