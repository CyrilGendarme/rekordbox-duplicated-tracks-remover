"""Rekordbox database operations for track management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from file_operations import log_file_operation


def delete_rekordbox_track(
    db: Any,
    content_id: str,
    *,
    verbose: bool = True,
    log_enabled: bool = True,
) -> bool:
    """Delete a track from the Rekordbox collection."""
    if db is None or not content_id:
        if verbose:
            print(f"  [SKIP] Cannot delete Rekordbox content id={content_id}")
        return False

    try:
        content = db.get_content(ID=content_id)
        if content is None:
            if verbose:
                print(f"  [SKIP] Rekordbox content not found for id={content_id}")
            return False

        delete_content_fn = getattr(db, "delete_content", None)
        if callable(delete_content_fn):
            delete_content_fn(content)
        else:
            delete_fn = getattr(db, "delete", None)
            if not callable(delete_fn):
                if verbose:
                    print("  [SKIP] No delete method available on Rekordbox DB instance")
                return False
            delete_fn(content)

        log_file_operation("REKORDBOX DELETE", f"content_id={content_id}", enabled=log_enabled)
        return True
    except Exception as exc:
        if verbose:
            print(f"  [ERROR] Failed deleting Rekordbox content id={content_id}: {exc}")
        return False


def relocate_rekordbox_track(
    db: Any,
    content_id: str,
    new_path: str,
    *,
    verbose: bool = True,
    log_enabled: bool = True,
) -> bool:
    """Relocate a track to a new path in the Rekordbox collection."""
    if db is None or not content_id:
        if verbose:
            print(f"  [SKIP] Cannot relocate Rekordbox content id={content_id}")
        return False

    path_obj = Path(new_path)
    if not path_obj.exists():
        if verbose:
            print(f"  [SKIP] Relocation target does not exist: {new_path}")
        return False

    try:
        update_path_fn = getattr(db, "update_content_path", None)
        if callable(update_path_fn):
            update_path_fn(content_id, str(path_obj), save=True, check_path=True, commit=False)
            log_file_operation(
                "REKORDBOX RELOCATE",
                f"content_id={content_id} -> {path_obj}",
                enabled=log_enabled,
            )
            return True

        content = db.get_content(ID=content_id)
        if content is None:
            if verbose:
                print(f"  [SKIP] Rekordbox content not found for id={content_id}")
            return False

        normalized = str(path_obj).replace("\\", "/")
        if hasattr(content, "FolderPath"):
            content.FolderPath = normalized
        if hasattr(content, "OrgFolderPath") and getattr(content, "OrgFolderPath", ""):
            content.OrgFolderPath = normalized
        if hasattr(content, "FileNameL"):
            content.FileNameL = path_obj.name
        log_file_operation(
            "REKORDBOX RELOCATE",
            f"content_id={content_id} -> {normalized}",
            enabled=log_enabled,
        )
        return True
    except Exception as exc:
        if verbose:
            print(f"  [ERROR] Failed relocating Rekordbox content id={content_id}: {exc}")
        return False
