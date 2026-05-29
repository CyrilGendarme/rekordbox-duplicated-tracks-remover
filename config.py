"""Centralized configuration constants for the duplicate track remover."""

from __future__ import annotations

CLI_DESCRIPTION = (
    "Read a Rekordbox collection and print duplicate tracks "
    "(same title + artist)."
)
CLI_KEY_HELP = (
    "Optional SQLCipher key for Rekordbox database decryption. "
    "Useful for some Rekordbox >= 6.6.5 installs."
)
CLI_CASE_SENSITIVE_HELP = (
    "Use case-sensitive duplicate matching (default is case-insensitive)."
)
CLI_INCLUDE_EMPTY_HELP = "Include tracks even if title or artist is empty."
CLI_YOUTUBE_DIR_HELP = (
    "Scan directory for audio files and match against duplicate paths using filename."
)
CLI_DROPBOX_DIR_HELP = "Dropbox rekordbox folder path for file consolidation."
CLI_AUTO_CLEANUP_HELP = (
    "Automatically cleanup and relocate files (requires --dropbox-dir)."
)
CLI_TEST_MODE_HELP = "Test mode: process only first match then exit."
CLI_TITLES_ONLY_HELP = "Only print 'artist - title' lines to console."

DEFAULT_LOG_ENABLED = True
DEFAULT_VERBOSE = True

EMPTY_STRING = ""
UNKNOWN_CONTENT_ID = "?"
ROOT_PATH_PREFIX = "/"
WINDOWS_PATH_SEPARATOR = "\\"
POSIX_PATH_SEPARATOR = "/"
DROPBOX_FILE_GLOB = "*"

EXIT_CODE_SUCCESS = 0
EXIT_CODE_IMPORT_ERROR = 1
EXIT_CODE_DB_OPEN_ERROR = 2

PYREKORDBOX_IMPORT_ERROR_MESSAGE = (
    "pyrekordbox is not installed. Run: pip install pyrekordbox"
)
REKORDBOX_OPEN_ERROR_TEMPLATE = "Failed to open Rekordbox database: {exc}"
NO_DUPLICATES_FOUND_MESSAGE = "No duplicates found."
DB_COMMIT_SUCCESS_MESSAGE = "\n[DB] Rekordbox database save committed."

FILE_OPERATION_PREFIX = "[FILE OP]"
FILE_OPERATION_WIDTH = 20
FILE_DELETE_OPERATION = "DELETE"
FILE_DELETE_NOT_FOUND_OPERATION = "DELETE (NOT FOUND)"
FILE_DELETE_FAILED_OPERATION = "DELETE FAILED"
LOCAL_FILE_DELETE_REASON = "remove local downloaded file"
DROPBOX_FILE_DELETE_REASON = "remove dropbox dir file"

REKORDBOX_DELETE_OPERATION = "REKORDBOX DELETE"
REKORDBOX_RELOCATE_OPERATION = "REKORDBOX RELOCATE"
REKORDBOX_SKIP_DELETE_TEMPLATE = "  [SKIP] Cannot delete Rekordbox content id={content_id}"
REKORDBOX_NOT_FOUND_TEMPLATE = "  [SKIP] Rekordbox content not found for id={content_id}"
REKORDBOX_DELETE_METHOD_MISSING_MESSAGE = (
    "  [SKIP] No delete method available on Rekordbox DB instance"
)
REKORDBOX_DELETE_ERROR_TEMPLATE = (
    "  [ERROR] Failed deleting Rekordbox content id={content_id}: {exc}"
)
REKORDBOX_SKIP_RELOCATE_TEMPLATE = (
    "  [SKIP] Cannot relocate Rekordbox content id={content_id}"
)
RELOCATION_TARGET_MISSING_TEMPLATE = "  [SKIP] Relocation target does not exist: {new_path}"
REKORDBOX_RELOCATE_ERROR_TEMPLATE = (
    "  [ERROR] Failed relocating Rekordbox content id={content_id}: {exc}"
)

REKORDBOX_GET_CONTENT_METHOD = "get_content"
REKORDBOX_DELETE_CONTENT_METHOD = "delete_content"
REKORDBOX_DELETE_METHOD = "delete"
REKORDBOX_UPDATE_CONTENT_PATH_METHOD = "update_content_path"
REKORDBOX_COMMIT_METHOD = "commit"
REKORDBOX_CLOSE_METHOD = "close"

COPYRIGHT_OK_TAG = "copyright ok"
RECORD_RIP_TAG = "record rip"
NOT_TAGGED_TAG = "not tagged"

TRACK_TAG_ATTRIBUTES = ("MyTagNames", "MyTags", "Tags")
TAG_NAME_ATTRIBUTES = ("Name", "TagName")
MY_TAG_ATTRIBUTE = "MyTag"
HOT_CUES_COUNT_KEY = "hot_cues_cnt"
MEMORY_CUES_COUNT_KEY = "memory_cues_cnt"

FILENAME_NORMALIZE_PATTERN = r"[^a-z0-9\s]"
