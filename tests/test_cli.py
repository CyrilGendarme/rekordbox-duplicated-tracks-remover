"""Tests for cli module."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from cli import parse_args


class TestParseArgs:
    """Tests for the parse_args function."""

    def test_parse_args_defaults(self):
        """Test default argument values."""
        with patch("sys.argv", ["prog"]):
            args = parse_args()
        
        assert args.key is None
        assert args.case_sensitive is False
        assert args.include_empty is False
        assert args.youtube_dir is None
        assert args.dropbox_dir is None
        assert args.auto_cleanup is False
        assert args.test_mode is False
        assert args.titles_only is False

    def test_parse_args_with_key(self):
        """Test parsing with --key argument."""
        with patch("sys.argv", ["prog", "--key", "test_key_123"]):
            args = parse_args()
        
        assert args.key == "test_key_123"

    def test_parse_args_case_sensitive(self):
        """Test parsing with --case-sensitive flag."""
        with patch("sys.argv", ["prog", "--case-sensitive"]):
            args = parse_args()
        
        assert args.case_sensitive is True

    def test_parse_args_include_empty(self):
        """Test parsing with --include-empty flag."""
        with patch("sys.argv", ["prog", "--include-empty"]):
            args = parse_args()
        
        assert args.include_empty is True

    def test_parse_args_youtube_dir(self):
        """Test parsing with --youtube-dir argument."""
        with patch("sys.argv", ["prog", "--youtube-dir", "/path/to/youtube"]):
            args = parse_args()
        
        assert args.youtube_dir == "/path/to/youtube"

    def test_parse_args_dropbox_dir(self):
        """Test parsing with --dropbox-dir argument."""
        with patch("sys.argv", ["prog", "--dropbox-dir", "/path/to/dropbox"]):
            args = parse_args()
        
        assert args.dropbox_dir == "/path/to/dropbox"

    def test_parse_args_auto_cleanup(self):
        """Test parsing with --auto-cleanup flag."""
        with patch("sys.argv", ["prog", "--auto-cleanup"]):
            args = parse_args()
        
        assert args.auto_cleanup is True

    def test_parse_args_test_mode(self):
        """Test parsing with --test-mode flag."""
        with patch("sys.argv", ["prog", "--test-mode"]):
            args = parse_args()
        
        assert args.test_mode is True

    def test_parse_args_titles_only(self):
        """Test parsing with --titles-only flag."""
        with patch("sys.argv", ["prog", "--titles-only"]):
            args = parse_args()
        
        assert args.titles_only is True

    def test_parse_args_multiple_flags(self):
        """Test parsing with multiple arguments."""
        with patch(
            "sys.argv",
            [
                "prog",
                "--case-sensitive",
                "--youtube-dir",
                "/youtube",
                "--dropbox-dir",
                "/dropbox",
                "--auto-cleanup",
                "--titles-only",
            ],
        ):
            args = parse_args()
        
        assert args.case_sensitive is True
        assert args.youtube_dir == "/youtube"
        assert args.dropbox_dir == "/dropbox"
        assert args.auto_cleanup is True
        assert args.titles_only is True
