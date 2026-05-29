"""Tests for track_info_extraction module."""

from __future__ import annotations

from types import SimpleNamespace

from track_info_extraction import extract_track_cues, extract_track_tags


class TestExtractTrackTags:
    """Tests for tag extraction from Rekordbox content objects."""

    def test_extracts_tags_from_multiple_supported_shapes(self):
        content = SimpleNamespace(
            MyTagNames=" Direct Tag ",
            MyTags=[
                SimpleNamespace(Name="House"),
                SimpleNamespace(TagName="Peak Time"),
            ],
            Tags=SimpleNamespace(MyTag=SimpleNamespace(Name="Closing")),
        )

        result = extract_track_tags(content)

        assert result == ["Direct Tag", "House", "Peak Time", "Closing"]

    def test_deduplicates_tags_while_preserving_order(self):
        content = SimpleNamespace(
            MyTagNames=None,
            MyTags=[
                SimpleNamespace(Name="House"),
                SimpleNamespace(Name="House"),
            ],
            Tags="House",
        )

        result = extract_track_tags(content)

        assert result == ["House"]

    def test_ignores_empty_tag_values(self):
        content = SimpleNamespace(
            MyTagNames="   ",
            MyTags=[SimpleNamespace(Name=""), SimpleNamespace(TagName=None)],
            Tags=SimpleNamespace(MyTag=SimpleNamespace(Name="")),
        )

        result = extract_track_tags(content)

        assert result == []


class TestExtractTrackCues:
    """Tests for cue extraction counts."""

    def test_counts_hot_and_memory_cues(self):
        content = SimpleNamespace(
            Cues=[
                SimpleNamespace(is_hot_cue=True, is_memory_cue=False),
                SimpleNamespace(is_hot_cue=True, is_memory_cue=False),
                SimpleNamespace(is_hot_cue=False, is_memory_cue=True),
                SimpleNamespace(is_hot_cue=False, is_memory_cue=False),
            ]
        )

        result = extract_track_cues(content)

        assert result == {"hot_cues_cnt": 2, "memory_cues_cnt": 1}

    def test_returns_zero_counts_for_empty_cues(self):
        content = SimpleNamespace(Cues=[])

        result = extract_track_cues(content)

        assert result == {"hot_cues_cnt": 0, "memory_cues_cnt": 0}