"""Direct unit tests for EventEntry.same_swimmer_entry_as.

The behaviour is exercised through f1_parser in test_f_relay_parsers.py
(via get_or_create_entry's collapse rule). These tests call the method
directly so that future refactors to the identity tuples are caught
without needing the full state-machine plumbing.
"""

import unittest

from hytek_parser.hy3.enums import Course, Gender
from hytek_parser.hy3.schemas import EventEntry, Swimmer


def _swimmer(meet_id: int, last_name: str = "Smith") -> Swimmer:
    s = Swimmer()
    s.gender = Gender.MALE
    s.meet_id = meet_id
    s.last_name = last_name
    s.first_name = "Test"
    s.nick_name = ""
    s.middle_initial = ""
    s.usa_swimming_id = ""
    s.team_id = None
    s.team_code = "FOO"
    s.date_of_birth = None
    s.age = 12
    s.citizenship = None
    s.status = None
    s.class_year = None
    return s


def _relay_entry(
    *,
    event_number: str = "2",
    team_id: str = "A",
    team_code: str = "FOO",
    seed_time: float = 112.37,
    swimmers: dict | None = None,
) -> EventEntry:
    return EventEntry(
        swimmers=swimmers if swimmers is not None else {},
        relay=True,
        event_number=event_number,
        seed_time=seed_time,
        seed_course=Course.SCY,
        converted_seed_time=seed_time,
        converted_seed_time_course=Course.SCY,
        relay_team_id=team_id,
        relay_swim_team_code=team_code,
    )


def _individual_entry(
    *,
    event_number: str = "1",
    swimmer_id: int = 1,
    seed_time: float = 30.00,
) -> EventEntry:
    return EventEntry(
        swimmers={1: _swimmer(swimmer_id)},
        relay=False,
        event_number=event_number,
        seed_time=seed_time,
        seed_course=Course.SCY,
        converted_seed_time=seed_time,
        converted_seed_time_course=Course.SCY,
    )


class TestSameSwimmerEntryAsRelay(unittest.TestCase):
    """Relay identity: (event_number, team_code, team_id, seed_time, seed_course)."""

    def test_same_team_same_event_same_seed_collapses(self) -> None:
        a = _relay_entry()
        b = _relay_entry()
        self.assertTrue(a.same_swimmer_entry_as(b))

    def test_different_team_code_does_not_collapse(self) -> None:
        """Bug 2-A repro: two clubs in same event, identical seed times.
        Pre-fix logic ignored team attribution and collapsed them."""
        a = _relay_entry(team_code="FOO")
        b = _relay_entry(team_code="BAR")
        self.assertFalse(a.same_swimmer_entry_as(b))

    def test_different_team_letter_does_not_collapse(self) -> None:
        """A and B teams from the same club must remain distinct."""
        a = _relay_entry(team_id="A")
        b = _relay_entry(team_id="B")
        self.assertFalse(a.same_swimmer_entry_as(b))

    def test_relay_identity_ignores_swimmers_dict(self) -> None:
        """Relay identity is set at F1 time, before F3 populates swimmers.
        Prelim and finals entries for the same relay must collapse even
        if F3 had not yet populated swimmers on the prelim entry."""
        a = _relay_entry(swimmers={})
        b = _relay_entry(swimmers={1: _swimmer(10), 2: _swimmer(11)})
        self.assertTrue(a.same_swimmer_entry_as(b))


class TestSameSwimmerEntryAsIndividual(unittest.TestCase):
    """Individual identity unchanged from pre-fix: (swimmers, event_number,
    seed_time, seed_course, converted_seed_time, converted_seed_time_course)."""

    def test_same_swimmer_same_event_collapses(self) -> None:
        a = _individual_entry(swimmer_id=42)
        b = _individual_entry(swimmer_id=42)
        # Same meet_id → equal Swimmer (attrs eq=True). Same event + seed.
        self.assertTrue(a.same_swimmer_entry_as(b))

    def test_different_swimmer_does_not_collapse(self) -> None:
        a = _individual_entry(swimmer_id=42)
        b = _individual_entry(swimmer_id=99)
        self.assertFalse(a.same_swimmer_entry_as(b))

    def test_different_event_does_not_collapse(self) -> None:
        a = _individual_entry(event_number="1")
        b = _individual_entry(event_number="2")
        self.assertFalse(a.same_swimmer_entry_as(b))


class TestSameSwimmerEntryAsMixed(unittest.TestCase):
    """Relay vs individual must never collapse, regardless of other fields."""

    def test_relay_vs_individual_does_not_collapse(self) -> None:
        a = _relay_entry(event_number="2", seed_time=30.00)
        b = _individual_entry(event_number="2", seed_time=30.00)
        self.assertFalse(a.same_swimmer_entry_as(b))
        self.assertFalse(b.same_swimmer_entry_as(a))


if __name__ == "__main__":
    unittest.main()
