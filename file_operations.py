"""File system operations for managing audio files."""

from __future__ import annotations

import sys
from pathlib import Path


def log_file_operation(operation: str, file_path: str, enabled: bool = True) -> None:
    """Log file operations to console."""
    if not enabled:
        return
    print(f"[FILE OP] {operation:20} | {file_path}", file=sys.stderr)


def safe_delete_file(
    file_path: str,
    reason: str = "",
    log_enabled: bool = True,
    verbose: bool = True,
) -> bool:
    """Safely delete a file with logging."""
    path = Path(file_path)
    if not path.exists():
        log_file_operation("DELETE (NOT FOUND)", file_path, enabled=log_enabled)
        return False

    try:
        path.unlink()
        msg = f"DELETE"
        if reason:
            msg += f" ({reason})"
        log_file_operation(msg, file_path, enabled=log_enabled)
        return True
    except Exception as e:
        log_file_operation("DELETE FAILED", file_path, enabled=log_enabled)
        if verbose:
            print(f"  Error: {e}", file=sys.stderr)
        return False

