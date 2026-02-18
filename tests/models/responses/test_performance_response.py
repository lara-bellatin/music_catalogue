from datetime import date

import pytest

from music_catalogue.models.responses.performances import Performance
from music_catalogue.models.responses.references import (
    PerformanceArtistRef,
    PerformanceRef,
    PerformanceWorkRef,
)


class TestPerformanceRef:
    """Tests for PerformanceRef.from_dict."""

    def test_from_dict_full_payload(self):
        data = {
            "performance_id": "perf-1",
            "name": "Wembley",
            "performance_date": "2026-01-01",
            "venue": "Wembley Stadium",
            "city": "London",
        }

        ref = PerformanceRef.from_dict(data)

        assert ref.id == "perf-1"
        assert ref.name == "Wembley"
        assert ref.performance_date == date(2026, 1, 1)
        assert ref.venue == "Wembley Stadium"
        assert ref.city == "London"

    def test_from_dict_minimal_payload(self):
        data = {
            "performance_id": "perf-2",
            "name": "Concert",
            "performance_date": None,
            "venue": None,
            "city": None,
        }

        ref = PerformanceRef.from_dict(data)

        assert ref.id == "perf-2"
        assert ref.name == "Concert"
        assert ref.performance_date is None
        assert ref.venue is None
        assert ref.city is None

    def test_from_dict_missing_required_field(self):
        with pytest.raises(KeyError):
            PerformanceRef.from_dict({"name": "No ID"})


class TestPerformanceArtistRef:
    """Tests for PerformanceArtistRef.from_dict."""

    def test_from_dict_with_artist(self):
        data = {
            "performance_artist_id": "pa-1",
            "role": "headliner",
            "billing_order": 1,
            "notes": "Main act",
            "artist": {
                "artist_id": "artist-1",
                "display_name": "The Band",
                "artist_type": "group",
            },
            "person": None,
        }

        ref = PerformanceArtistRef.from_dict(data)

        assert ref.role == "headliner"
        assert ref.billing_order == 1
        assert ref.notes == "Main act"
        assert ref.artist is not None and ref.artist.id == "artist-1"
        assert ref.person is None

    def test_from_dict_with_person(self):
        data = {
            "performance_artist_id": "pa-2",
            "role": "conductor",
            "billing_order": None,
            "notes": None,
            "artist": None,
            "person": {
                "person_id": "person-1",
                "legal_name": "John Smith",
            },
        }

        ref = PerformanceArtistRef.from_dict(data)

        assert ref.role == "conductor"
        assert ref.person is not None and ref.person.id == "person-1"
        assert ref.artist is None


class TestPerformanceWorkRef:
    """Tests for PerformanceWorkRef.from_dict."""

    def test_from_dict_with_work(self):
        data = {
            "performance_work_id": "pw-1",
            "set_order": 1,
            "set_name": "First Half",
            "notes": None,
            "work": {"work_id": "work-1", "title": "Saul og David", "language": "da"},
            "version": None,
        }

        ref = PerformanceWorkRef.from_dict(data)

        assert ref.set_order == 1
        assert ref.set_name == "First Half"
        assert ref.work is not None and ref.work.id == "work-1"
        assert ref.version is None

    def test_from_dict_with_version(self):
        data = {
            "performance_work_id": "pw-2",
            "set_order": 3,
            "set_name": "Encore",
            "notes": "Crowd favourite",
            "work": None,
            "version": {
                "version_id": "ver-1",
                "title": "Bohemian Rhapsody (Live)",
                "version_type": "live",
                "primary_artist": None,
                "release_year": None,
                "completeness_level": "complete",
            },
        }

        ref = PerformanceWorkRef.from_dict(data)

        assert ref.set_order == 3
        assert ref.set_name == "Encore"
        assert ref.notes == "Crowd favourite"
        assert ref.version is not None and ref.version.id == "ver-1"
        assert ref.work is None


class TestPerformance:
    """Tests for Performance.from_dict."""

    def test_from_dict_full_payload(self):
        payload = {
            "performance_id": "perf-1",
            "name": "Performance of Prelude to Act 2",
            "performance_date": "2026-01-01",
            "venue": "Koncertpalæet",
            "city": "Copenhagen",
            "country": "Denmark",
            "notes": "Opening night",
            "performance_artists": [
                {
                    "performance_artist_id": "pa-1",
                    "role": "orchestra",
                    "billing_order": 1,
                    "notes": None,
                    "artist": {
                        "artist_id": "artist-1",
                        "display_name": "The Royal Danish Orchestra",
                        "artist_type": "group",
                    },
                    "person": None,
                },
            ],
            "performance_works": [
                {
                    "performance_work_id": "pw-1",
                    "set_order": 1,
                    "set_name": "Act 2",
                    "notes": None,
                    "work": {"work_id": "work-1", "title": "Saul og David", "language": "da"},
                    "version": None,
                },
            ],
        }

        perf = Performance.from_dict(payload)

        assert perf.id == "perf-1"
        assert perf.name == "Performance of Prelude to Act 2"
        assert perf.performance_date == date(2026, 1, 1)
        assert perf.venue == "Koncertpalæet"
        assert perf.city == "Copenhagen"
        assert perf.country == "Denmark"
        assert perf.notes == "Opening night"
        assert len(perf.artists) == 1
        assert perf.artists[0].role == "orchestra"
        assert len(perf.works) == 1
        assert perf.works[0].work.title == "Saul og David"

    def test_from_dict_minimal_payload(self):
        payload = {
            "performance_id": "perf-2",
            "name": "Concert",
            "performance_date": None,
            "venue": None,
            "city": None,
            "country": None,
            "notes": None,
            "performance_artists": [],
            "performance_works": [],
        }

        perf = Performance.from_dict(payload)

        assert perf.id == "perf-2"
        assert perf.name == "Concert"
        assert perf.performance_date is None
        assert perf.artists == []
        assert perf.works == []

    def test_from_dict_missing_required_field(self):
        with pytest.raises(KeyError):
            Performance.from_dict({"name": "No ID"})
