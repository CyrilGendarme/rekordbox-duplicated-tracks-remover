"""Tests for duplicate cleanup workflow in find_duplicate_tracks."""

from __future__ import annotations

from unittest.mock import ANY, Mock, call, patch

from find_duplicate_tracks import _merge_protected_tags, perform_cleanup


class TestProtectedTagMerge:
    """Tests for protected tag transfer logic."""

    def test_merge_protected_tags_adds_missing_tags_from_removed_items(self):
        metadata_owner = {"tags": ["Not Tagged", "My Set"]}
        removed_items = [
            {"tags": ["record rip", "house"]},
            {"tags": ["Copyright Ok", "other"]},
        ]

        merged = _merge_protected_tags(metadata_owner, removed_items)

        assert merged == ["Not Tagged", "My Set", "record rip", "Copyright Ok"]

    def test_merge_protected_tags_keeps_existing_and_avoids_case_duplicates(self):
        metadata_owner = {"tags": ["Record Rip"]}
        removed_items = [{"tags": ["record rip", "COPYRIGHT OK"]}]

        merged = _merge_protected_tags(metadata_owner, removed_items)

        assert merged == ["Record Rip", "COPYRIGHT OK"]


class TestPerformCleanup:
    """Tests for the perform_cleanup function."""

    @patch("find_duplicate_tracks.relocate_rekordbox_track")
    @patch("find_duplicate_tracks.find_first_dropbox_file")
    @patch("find_duplicate_tracks.delete_rekordbox_track")
    @patch("find_duplicate_tracks.safe_delete_file")
    def test_same_file_and_metadata_owner_uses_early_return_branch(
        self,
        mock_delete_file,
        mock_delete_track,
        mock_find_dropbox,
        mock_relocate,
    ):
        owner = {
            "id": "1",
            "path_local_dir": "C:/local/owner.mp3",
            "path_rekordbox_dir": "/rb/owner.mp3",
        }
        duplicate = {
            "id": "2",
            "path_local_dir": "C:/local/duplicate.mp3",
            "path_rekordbox_dir": "/rb/duplicate.mp3",
        }
        mock_find_dropbox.return_value = "C:/dropbox/duplicate.mp3"

        perform_cleanup([owner, duplicate], owner, owner, Mock(), "C:/dropbox")

        mock_delete_file.assert_has_calls(
            [
                call(
                    "C:/local/duplicate.mp3",
                    reason="remove local downloaded file",
                    log_enabled=True,
                    verbose=True,
                ),
                call(
                    "C:/dropbox/duplicate.mp3",
                    reason="remove dropbox dir file",
                    log_enabled=True,
                    verbose=True,
                ),
            ]
        )
        mock_delete_track.assert_called_once_with(
            ANY, "2", verbose=True, log_enabled=True
        )
        mock_relocate.assert_not_called()

    @patch("find_duplicate_tracks.relocate_rekordbox_track")
    @patch("find_duplicate_tracks.find_first_dropbox_file")
    @patch("find_duplicate_tracks.delete_rekordbox_track")
    @patch("find_duplicate_tracks.safe_delete_file")
    def test_different_owners_delete_duplicates_and_relocate_survivor(
        self,
        mock_delete_file,
        mock_delete_track,
        mock_find_dropbox,
        mock_relocate,
    ):
        file_owner = {
            "id": "1",
            "path_local_dir": "C:/local/owner.mp3",
            "path_rekordbox_dir": "/rb/owner.mp3",
        }
        metadata_owner = {
            "id": "2",
            "path_local_dir": "C:/local/meta.mp3",
            "path_rekordbox_dir": "/rb/meta.mp3",
        }
        mock_db = Mock()
        mock_find_dropbox.side_effect = [
            "C:/dropbox/meta.mp3",
            "C:/dropbox/owner.mp3",
        ]

        perform_cleanup(
            [file_owner, metadata_owner],
            file_owner,
            metadata_owner,
            mock_db,
            "C:/dropbox",
        )

        mock_delete_file.assert_has_calls(
            [
                call(
                    "C:/local/meta.mp3",
                    reason="remove local downloaded file",
                    log_enabled=True,
                    verbose=True,
                ),
                call(
                    "C:/dropbox/meta.mp3",
                    reason="remove dropbox dir file",
                    log_enabled=True,
                    verbose=True,
                ),
            ]
        )
        mock_delete_track.assert_called_once_with(
            mock_db, "1", verbose=True, log_enabled=True
        )
        mock_relocate.assert_called_once_with(
            mock_db,
            "2",
            "C:/dropbox/owner.mp3",
            verbose=True,
            log_enabled=True,
        )

    @patch("find_duplicate_tracks.relocate_rekordbox_track")
    @patch("find_duplicate_tracks.find_first_dropbox_file")
    @patch("find_duplicate_tracks.delete_rekordbox_track")
    @patch("find_duplicate_tracks.safe_delete_file")
    def test_skips_dropbox_delete_and_relocate_when_lookup_returns_none(
        self,
        mock_delete_file,
        mock_delete_track,
        mock_find_dropbox,
        mock_relocate,
    ):
        file_owner = {
            "id": "1",
            "path_local_dir": "C:/local/owner.mp3",
            "path_rekordbox_dir": "/rb/owner.mp3",
        }
        metadata_owner = {
            "id": "2",
            "path_local_dir": "C:/local/meta.mp3",
            "path_rekordbox_dir": "/rb/meta.mp3",
        }
        mock_find_dropbox.side_effect = [None, None]

        perform_cleanup(
            [file_owner, metadata_owner],
            file_owner,
            metadata_owner,
            Mock(),
            "C:/dropbox",
        )

        assert mock_delete_file.call_count == 1
        mock_delete_track.assert_called_once()
        mock_relocate.assert_not_called()

    @patch("find_duplicate_tracks.relocate_rekordbox_track")
    @patch("find_duplicate_tracks.find_first_dropbox_file")
    @patch("find_duplicate_tracks.delete_rekordbox_track")
    @patch("find_duplicate_tracks.safe_delete_file")
    def test_dry_run_logs_only_and_skips_mutations(
        self,
        mock_delete_file,
        mock_delete_track,
        mock_find_dropbox,
        mock_relocate,
    ):
        file_owner = {
            "id": "1",
            "path_local_dir": "C:/local/owner.mp3",
            "path_rekordbox_dir": "/rb/owner.mp3",
        }
        metadata_owner = {
            "id": "2",
            "path_local_dir": "C:/local/meta.mp3",
            "path_rekordbox_dir": "/rb/meta.mp3",
        }
        mock_find_dropbox.side_effect = ["C:/dropbox/meta.mp3", "C:/dropbox/owner.mp3"]

        perform_cleanup(
            [file_owner, metadata_owner],
            file_owner,
            metadata_owner,
            Mock(),
            "C:/dropbox",
            dry_run=True,
        )

        mock_delete_file.assert_not_called()
        mock_delete_track.assert_not_called()
        mock_relocate.assert_not_called()

    @patch("find_duplicate_tracks.relocate_rekordbox_track")
    @patch("find_duplicate_tracks.find_first_dropbox_file")
    @patch("find_duplicate_tracks.delete_rekordbox_track")
    @patch("find_duplicate_tracks.safe_delete_file")
    @patch("find_duplicate_tracks._set_rekordbox_track_tags")
    def test_propagates_protected_tags_to_kept_metadata_track(
        self,
        mock_set_tags,
        mock_delete_file,
        mock_delete_track,
        mock_find_dropbox,
        mock_relocate,
    ):
        file_owner = {
            "id": "1",
            "path_local_dir": "C:/local/owner.mp3",
            "path_rekordbox_dir": "/rb/owner.mp3",
            "tags": ["record rip"],
        }
        metadata_owner = {
            "id": "2",
            "path_local_dir": "C:/local/meta.mp3",
            "path_rekordbox_dir": "/rb/meta.mp3",
            "tags": ["Not Tagged"],
        }
        mock_db = Mock()
        mock_find_dropbox.side_effect = ["C:/dropbox/meta.mp3", "C:/dropbox/owner.mp3"]

        perform_cleanup(
            [file_owner, metadata_owner],
            file_owner,
            metadata_owner,
            mock_db,
            "C:/dropbox",
        )

        mock_set_tags.assert_called_once_with(
            mock_db,
            "2",
            ["Not Tagged", "record rip"],
        )
