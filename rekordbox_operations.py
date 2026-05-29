"""Rekordbox database operations for track management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config import (
    DEFAULT_LOG_ENABLED,
    DEFAULT_VERBOSE,
    EMPTY_STRING,
    POSIX_PATH_SEPARATOR,
    REKORDBOX_DELETE_CONTENT_METHOD,
    REKORDBOX_DELETE_ERROR_TEMPLATE,
    REKORDBOX_DELETE_METHOD,
    REKORDBOX_DELETE_METHOD_MISSING_MESSAGE,
    REKORDBOX_DELETE_OPERATION,
    REKORDBOX_GET_CONTENT_METHOD,
    REKORDBOX_NOT_FOUND_TEMPLATE,
    REKORDBOX_RELOCATE_ERROR_TEMPLATE,
    REKORDBOX_RELOCATE_OPERATION,
    REKORDBOX_SKIP_DELETE_TEMPLATE,
    REKORDBOX_SKIP_RELOCATE_TEMPLATE,
    REKORDBOX_UPDATE_CONTENT_PATH_METHOD,
    RELOCATION_TARGET_MISSING_TEMPLATE,
    WINDOWS_PATH_SEPARATOR,
)
from file_operations import log_file_operation


def delete_rekordbox_track(
    db: Any,
    content_id: str,
    *,
    verbose: bool = DEFAULT_VERBOSE,
    log_enabled: bool = DEFAULT_LOG_ENABLED,
) -> bool:
    """Delete a track from the Rekordbox collection."""
    if db is None or not content_id:
        if verbose:
            print(REKORDBOX_SKIP_DELETE_TEMPLATE.format(content_id=content_id))
        return False

    try:
        content = getattr(db, REKORDBOX_GET_CONTENT_METHOD)(ID=content_id)
        if content is None:
            if verbose:
                print(REKORDBOX_NOT_FOUND_TEMPLATE.format(content_id=content_id))
            return False

        delete_content_fn = getattr(db, REKORDBOX_DELETE_CONTENT_METHOD, None)
        if callable(delete_content_fn):
            delete_content_fn(content)
        else:
            delete_fn = getattr(db, REKORDBOX_DELETE_METHOD, None)
            if not callable(delete_fn):
                if verbose:
                    print(REKORDBOX_DELETE_METHOD_MISSING_MESSAGE)
                return False
            delete_fn(content)

        log_file_operation(
            REKORDBOX_DELETE_OPERATION,
            f"content_id={content_id}",
            enabled=log_enabled,
        )
        return True
    except Exception as exc:
        if verbose:
            print(
                REKORDBOX_DELETE_ERROR_TEMPLATE.format(content_id=content_id, exc=exc)
            )
        return False


def relocate_rekordbox_track(
    db: Any,
    content_id: str,
    new_path: str,
    *,
    verbose: bool = DEFAULT_VERBOSE,
    log_enabled: bool = DEFAULT_LOG_ENABLED,
) -> bool:
    """Relocate a track to a new path in the Rekordbox collection."""
    if db is None or not content_id:
        if verbose:
            print(REKORDBOX_SKIP_RELOCATE_TEMPLATE.format(content_id=content_id))
        return False

    path_obj = Path(new_path)
    if not path_obj.exists():
        if verbose:
            print(RELOCATION_TARGET_MISSING_TEMPLATE.format(new_path=new_path))
        return False

    try:
        update_path_fn = getattr(db, REKORDBOX_UPDATE_CONTENT_PATH_METHOD, None)
        if callable(update_path_fn):
            update_path_fn(content_id, str(path_obj), save=True, check_path=True, commit=False)
            log_file_operation(
                REKORDBOX_RELOCATE_OPERATION,
                f"content_id={content_id} -> {path_obj}",
                enabled=log_enabled,
            )
            return True

        content = getattr(db, REKORDBOX_GET_CONTENT_METHOD)(ID=content_id)
        if content is None:
            if verbose:
                print(REKORDBOX_NOT_FOUND_TEMPLATE.format(content_id=content_id))
            return False

        normalized = str(path_obj).replace(WINDOWS_PATH_SEPARATOR, POSIX_PATH_SEPARATOR)
        if hasattr(content, "FolderPath"):
            content.FolderPath = normalized
        if hasattr(content, "OrgFolderPath") and getattr(
            content, "OrgFolderPath", EMPTY_STRING
        ):
            content.OrgFolderPath = normalized
        if hasattr(content, "FileNameL"):
            content.FileNameL = path_obj.name
        log_file_operation(
            REKORDBOX_RELOCATE_OPERATION,
            f"content_id={content_id} -> {normalized}",
            enabled=log_enabled,
        )
        return True
    except Exception as exc:
        if verbose:
            print(
                REKORDBOX_RELOCATE_ERROR_TEMPLATE.format(content_id=content_id, exc=exc)
            )
        return False
