"""Tests for track_role_mgmt module."""

from __future__ import annotations

from track_role_mgmt import find_matching_files


class TestFindMatchingFiles:
    """Tests for duplicate ownership selection."""

    def test_returns_first_item_for_both_owners_by_default(self):
        duplicate = [
            {
                "id": "1",
                "title": "Track",
                "artist": "Artist",
                "tags": [],
                "cues": {"hot_cues_cnt": 0},
            },
            {
                "id": "2",
                "title": "Track",
                "artist": "Artist",
                "tags": [],
                "cues": {"hot_cues_cnt": 0},
            },
        ]

        result = find_matching_files(duplicate)

        assert result["file_owner"] is duplicate[0]
        assert result["metadata_owner"] is duplicate[0]

    def test_prefers_copyright_ok_for_file_owner(self):
        duplicate = [
            {
                "id": "1",
                "tags": ["Other Tag"],
                "cues": {"hot_cues_cnt": 0},
            },
            {
                "id": "2",
                "tags": ["Copyright Ok"],
                "cues": {"hot_cues_cnt": 0},
            },
        ]

        result = find_matching_files(duplicate)

        assert result["file_owner"] is duplicate[1]
        assert result["metadata_owner"] is duplicate[1]

    def test_accepts_single_string_tag_values(self):
        duplicate = [
            {
                "id": "1",
                "tags": "copyright ok",
                "cues": {"hot_cues_cnt": 0},
            },
            {
                "id": "2",
                "tags": [],
                "cues": {"hot_cues_cnt": 0},
            },
        ]

        result = find_matching_files(duplicate)

        assert result["file_owner"] is duplicate[0]

    def test_prefers_most_hot_cues_for_metadata_owner(self):
        duplicate = [
            {
                "id": "1",
                "tags": [],
                "cues": {"hot_cues_cnt": 1},
            },
            {
                "id": "2",
                "tags": [],
                "cues": {"hot_cues_cnt": 3},
            },
            {
                "id": "3",
                "tags": [],
                "cues": {"hot_cues_cnt": 2},
            },
        ]

        result = find_matching_files(duplicate)

        assert result["metadata_owner"] is duplicate[1]

    def test_prefers_not_tagged_absence_when_no_hot_cues(self):
        duplicate = [
            {
                "id": "1",
                "tags": ["Not Tagged"],
                "cues": {"hot_cues_cnt": 0},
            },
            {
                "id": "2",
                "tags": ["House"],
                "cues": {"hot_cues_cnt": 0},
            },
        ]

        result = find_matching_files(duplicate)

        assert result["metadata_owner"] is duplicate[1]

    def test_falls_back_to_file_owner_when_all_are_not_tagged(self):
        duplicate = [
            {
                "id": "1",
                "tags": ["Copyright Ok", "Not Tagged"],
                "cues": {"hot_cues_cnt": 0},
            },
            {
                "id": "2",
                "tags": ["Not Tagged"],
                "cues": {"hot_cues_cnt": 0},
            },
        ]

        result = find_matching_files(duplicate)

        assert result["file_owner"] is duplicate[0]
        assert result["metadata_owner"] is duplicate[0]