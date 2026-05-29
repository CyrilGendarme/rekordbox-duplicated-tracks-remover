"""File system operations for managing audio files."""

from __future__ import annotations

import sys
from pathlib import Path

from config import (
    DEFAULT_LOG_ENABLED,
    DEFAULT_VERBOSE,
    FILE_DELETE_FAILED_OPERATION,
    FILE_DELETE_NOT_FOUND_OPERATION,
    FILE_DELETE_OPERATION,
    FILE_OPERATION_PREFIX,
    FILE_OPERATION_WIDTH,
)


def log_file_operation(
    operation: str, file_path: str, enabled: bool = DEFAULT_LOG_ENABLED
) -> None:
    """Log file operations to console."""
    if not enabled:
        return
    print(
        f"{FILE_OPERATION_PREFIX} {operation:{FILE_OPERATION_WIDTH}} | {file_path}",
        file=sys.stderr,
    )


def safe_delete_file(
    file_path: str,
    reason: str = "",
    log_enabled: bool = DEFAULT_LOG_ENABLED,
    verbose: bool = DEFAULT_VERBOSE,
) -> bool:
    """Safely delete a file with logging."""
    path = Path(file_path)
    if not path.exists():
        log_file_operation(
            FILE_DELETE_NOT_FOUND_OPERATION, file_path, enabled=log_enabled
        )
        return False

    try:
        path.unlink()
        msg = FILE_DELETE_OPERATION
        if reason:
            msg += f" ({reason})"
        log_file_operation(msg, file_path, enabled=log_enabled)
        return True
    except Exception as e:
        log_file_operation(FILE_DELETE_FAILED_OPERATION, file_path, enabled=log_enabled)
        if verbose:
            print(f"  Error: {e}", file=sys.stderr)
        return False
