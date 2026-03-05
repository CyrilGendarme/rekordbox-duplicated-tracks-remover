"""Command-line argument parsing for the duplicate track remover."""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Read a Rekordbox collection and print duplicate tracks "
            "(same title + artist)."
        )
    )
    parser.add_argument(
        "--key",
        help=(
            "Optional SQLCipher key for Rekordbox database decryption. "
            "Useful for some Rekordbox >= 6.6.5 installs."
        ),
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Use case-sensitive duplicate matching (default is case-insensitive).",
    )
    parser.add_argument(
        "--include-empty",
        action="store_true",
        help="Include tracks even if title or artist is empty.",
    )
    parser.add_argument(
        "--youtube-dir",
        type=str,
        help="Scan directory for audio files and match against duplicate paths using filename.",
    )
    parser.add_argument(
        "--dropbox-dir",
        type=str,
        help="Dropbox rekordbox folder path for file consolidation.",
    )
    parser.add_argument(
        "--auto-cleanup",
        action="store_true",
        help="Automatically cleanup and relocate files (requires --dropbox-dir).",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Test mode: process only first match then exit.",
    )
    parser.add_argument(
        "--titles-only",
        action="store_true",
        help="Only print 'artist - title' lines to console.",
    )
    return parser.parse_args()
