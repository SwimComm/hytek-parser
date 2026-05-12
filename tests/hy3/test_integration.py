"""End-to-end integration tests against real Hy-Tek hy3 fixtures.

These fixtures were extracted from real MM output files and PII-redacted
(swimmer names, DOBs, USA-Swimming IDs, and team contact info replaced
with placeholders) — see tests/hy3/fixtures/README.md.

Together they cover all three bugs fixed in the 2.0.0 release across
multiple MM versions:
    Bug 1   — blank E2/F2 date column
    Bug 2-A — relay attribution per-entry (not per-event)
    Bug 2-B — F3 dict-keyed swimmers preserving alternates
"""

from pathlib import Path
import unittest

from hytek_parser import parse_hy3

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class TestMM2BlankDateAndRelayMultiTeam(unittest.TestCase):
    """MM2 2.0Fg (2007 Pacific Committee R-W SC Meet).

    Exercises Bug 1 (every individual E2 line in this generation omits
    the date column) and Bug 2-A (event 21 has six relay entries across
    four teams, including ROSE-A/ROSE-B and WEST-A/WEST-B).
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.parsed = parse_hy3(str(FIXTURE_DIR / "mm2_2_0fg_relay_multi_team.hy3"))

    def test_file_version_is_mm2(self) -> None:
        # A1 header for these fixtures encodes "MM2 2.0Fg" — Hy-Tek major
        # generation 2. Sanity-check the parsed Software so a future
        # refactor that drops MM version recognition fails loudly.
        self.assertIn("2", self.parsed.software.name + self.parsed.software.version)

    def test_bug1_blank_date_does_not_drop_individual_results(self) -> None:
        individual_entries = [
            e
            for ev in self.parsed.meet.events.values()
            if not ev.relay
            for e in ev.entries
        ]
        # Every E2 row had a blank date in the source; finals_time must still
        # be populated and finals_date must be None.
        with_finals = [e for e in individual_entries if e.finals_time is not None]
        self.assertGreater(len(with_finals), 0, "no finals times parsed")
        self.assertTrue(
            all(e.finals_date is None for e in with_finals),
            "MM2 fixture has all-blank date columns; finals_date should be None",
        )

    def test_bug2a_six_relay_entries_distinct_per_team_and_letter(self) -> None:
        ev21 = self.parsed.meet.events["21"]
        self.assertEqual(6, len(ev21.entries))
        attribution = {
            (e.relay_swim_team_code, e.relay_team_id) for e in ev21.entries
        }
        # Four distinct team codes, with ROSE and WEST fielding A+B teams.
        self.assertEqual(
            {
                ("BRSC", "A"),
                ("LAC", "A"),
                ("ROSE", "A"),
                ("ROSE", "B"),
                ("WEST", "A"),
                ("WEST", "B"),
            },
            attribution,
        )


class TestMM3BlankDateAllIndividual(unittest.TestCase):
    """MM3 3.0Ea (2011 CA CSSC Fall Mile).

    Exercises Bug 1 on a different MM generation. All-individual file
    (mile + 500/1000 free), every E2 line has a blank date column.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.parsed = parse_hy3(
            str(FIXTURE_DIR / "mm3_3_0ea_individuals_blank_date.hy3")
        )

    def test_bug1_all_individual_results_have_blank_date(self) -> None:
        entries = [
            e for ev in self.parsed.meet.events.values() for e in ev.entries
        ]
        self.assertEqual(60, len(entries))
        for e in entries:
            self.assertIsNone(e.prelim_date)
            self.assertIsNone(e.swimoff_date)
            self.assertIsNone(e.finals_date)

    def test_finals_times_populated_despite_missing_date(self) -> None:
        with_finals = [
            e
            for ev in self.parsed.meet.events.values()
            for e in ev.entries
            if e.finals_time is not None
        ]
        self.assertGreater(len(with_finals), 0)


class TestMM5RelayAlternates(unittest.TestCase):
    """MM5 8.0Fd (2025 WMPSSDL Championships).

    Exercises Bug 2-B: F3 lines emit five swimmers (legs 1..5) for some
    4-leg relays. Library must preserve the leg-keyed dict so consumers
    can distinguish racers from alternates.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.parsed = parse_hy3(str(FIXTURE_DIR / "mm5_8_0fd_relay_alternates.hy3"))

    def test_bug2b_relay_entries_with_alternates_preserve_leg_numbers(self) -> None:
        ev17 = self.parsed.meet.events["17"]
        entries_with_alternates = [e for e in ev17.entries if len(e.swimmers) > 4]
        self.assertGreater(
            len(entries_with_alternates),
            0,
            "expected at least one entry with alternates",
        )
        for entry in entries_with_alternates:
            self.assertIsInstance(entry.swimmers, dict)
            # Leg numbers must be preserved as the dict keys, not collapsed
            # into a positional 0..N list.
            self.assertTrue(
                all(isinstance(k, int) for k in entry.swimmers.keys()),
                f"non-int leg keys: {list(entry.swimmers.keys())}",
            )
            # Alternates live at leg numbers > 4.
            self.assertTrue(
                any(leg > 4 for leg in entry.swimmers.keys()),
                f"no alternate legs found: {sorted(entry.swimmers.keys())}",
            )


if __name__ == "__main__":
    unittest.main()
