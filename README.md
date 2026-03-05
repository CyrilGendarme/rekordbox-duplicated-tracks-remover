# Rekordbox Duplicated Tracks Remover

Find duplicate tracks in a local Rekordbox 6 library using `pyrekordbox`.

Duplicate definition: **same title + same artist**.

## Requirements

- Python 3.10+
- Rekordbox installed on the same machine
- `pyrekordbox`

Install dependency:

```bash
pip install pyrekordbox
```

## Project Structure

The project is organized into modular components:

- **find_duplicate_tracks.py** - Main entry point and orchestration
- **cli.py** - Command-line argument parsing
- **normalizers.py** - Text and filename normalization utilities
- **rekordbox_helpers.py** - Rekordbox content object helpers
- **file_operations.py** - File system operations (scan, delete)
- **path_utils.py** - Path comparison and matching utilities
- **rekordbox_operations.py** - Database operations (delete, relocate tracks)
- **cleanup.py** - Cleanup workflow for duplicate management
- **matcher.py** - File matching logic for detecting duplicates

## Usage

Run from this project folder:

```bash
python find_duplicate_tracks.py
```

Optional flags:

- `--key <sqlcipher_key>`: provide Rekordbox DB key manually
- `--case-sensitive`: match duplicates with case-sensitive comparison
- `--include-empty`: include tracks with missing title or artist
- `--youtube-dir <path>`: scan directory for audio files and match against duplicates
- `--dropbox-dir <path>`: Dropbox rekordbox folder path for file consolidation
- `--auto-cleanup`: automatically cleanup and relocate files (requires --dropbox-dir)
- `--test-mode`: process only first match then exit (for testing)
- `--titles-only`: only print 'artist - title' lines to console

Example:

```bash
python find_duplicate_tracks.py --case-sensitive
```

Full cleanup example:

```bash
python find_duplicate_tracks.py --youtube-dir "C:\Music\youtube_downloaded" --dropbox-dir "C:\Dropbox\rekordbox" --auto-cleanup --titles-only
```

## Testing

The project includes a comprehensive test suite with **100 unit tests** covering all modules.

### Running Tests

Install test dependencies:

```bash
pip install -r requirements-dev.txt
```

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=. --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_normalizers.py -v
```

### Test Structure

- **test_cli.py** - Command-line argument parsing tests
- **test_normalizers.py** - Text and filename normalization tests
- **test_rekordbox_helpers.py** - Rekordbox content extraction tests
- **test_file_operations.py** - File system operations tests
- **test_path_utils.py** - Path utilities tests
- **test_rekordbox_operations.py** - Database operations tests
- **test_cleanup.py** - Cleanup workflow tests
- **test_matcher.py** - File matching logic tests

### Test Coverage

Current test coverage: **99% pass rate** (99/100 tests passing)

## Notes

- The script can read and modify the Rekordbox database when using `--auto-cleanup`
- Without `--auto-cleanup`, it only reads and reports duplicates
- If automatic key extraction fails on newer Rekordbox installs, cache/provide the key first (for example with `python -m pyrekordbox download-key` or `--key`)

