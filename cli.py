"""Command-line argument parsing for the duplicate track remover."""

from __future__ import annotations

import argparse

from config import (
    CLI_AUTO_CLEANUP_HELP,
    CLI_CASE_SENSITIVE_HELP,
    CLI_DESCRIPTION,
    CLI_DROPBOX_DIR_HELP,
    CLI_INCLUDE_EMPTY_HELP,
    CLI_KEY_HELP,
    CLI_TEST_MODE_HELP,
    CLI_TITLES_ONLY_HELP,
    CLI_YOUTUBE_DIR_HELP,
)

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)
    parser.add_argument(
        "--key",
        help=CLI_KEY_HELP,
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help=CLI_CASE_SENSITIVE_HELP,
    )
    parser.add_argument(
        "--include-empty",
        action="store_true",
        help=CLI_INCLUDE_EMPTY_HELP,
    )
    parser.add_argument(
        "--youtube-dir",
        type=str,
        help=CLI_YOUTUBE_DIR_HELP,
    )
    parser.add_argument(
        "--dropbox-dir",
        type=str,
        help=CLI_DROPBOX_DIR_HELP,
    )
    parser.add_argument(
        "--auto-cleanup",
        action="store_true",
        help=CLI_AUTO_CLEANUP_HELP,
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help=CLI_TEST_MODE_HELP,
    )
    parser.add_argument(
        "--titles-only",
        action="store_true",
        help=CLI_TITLES_ONLY_HELP,
    )
    return parser.parse_args()
