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

    def test_d1_school_class_captured_cols_100_101(self) -> None:
        # D1 cols 100-101 carry the school class (Fr/So/Jr/Sr) in high-school
        # exports; surfaced via the class_year field.
        classes = {
            (s.class_year or "").strip().title()
            for t in self.parsed.meet.teams.values()
            for s in t.swimmers.values()
        }
        self.assertTrue(
            classes & {"Fr", "So", "Jr", "Sr"},
            f"expected at least one Fr/So/Jr/Sr school class, got {sorted(classes)}",
        )


def _slot_field(entry, slot: str, field: str):
    """Return ``{slot}_{field}`` from an entry object."""
    return getattr(entry, f"{slot}_{field}", None)


def _all_entries(meet, relay_only: bool = False, individual_only: bool = False):
    """Yield (event, entry) pairs across all events and entries."""
    for ev in meet.events.values():
        if relay_only and not ev.relay:
            continue
        if individual_only and ev.relay:
            continue
        for e in ev.entries:
            yield ev, e


class TestMM4Col92DivisionCitizenshipTiming(unittest.TestCase):
    """MM4 4.0Ec (2013 YMCA Nationals) — col-92 fields.

    Verifies:
      - Team regions parsed from LSC code (col-92 fallback path)
      - Swimmer citizenship
      - meet_division 'SW' read via col-92 fallback
      - E2/F2 pad and button_1 times on individual entries
      - Relay entry prelim pad + button times
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.parsed = parse_hy3(
            str(FIXTURE_DIR / "mm4_ymca_col92_division_citizenship.hy3")
        )
        cls.meet = cls.parsed.meet

    def test_team_regions_md_ne_ni(self) -> None:
        regions = {t.region for t in self.meet.teams.values() if t.region}
        self.assertIn("MD", regions)
        self.assertIn("NE", regions)
        self.assertIn("NI", regions)

    def test_at_least_one_swimmer_citizenship_usa(self) -> None:
        citizenships = {
            s.citizenship
            for t in self.meet.teams.values()
            for s in t.swimmers.values()
        }
        self.assertIn("USA", citizenships)

    def test_meet_division_sw_col92_fallback(self) -> None:
        """At least one entry carries meet_division='SW' — proves col-92 read."""
        divisions = {
            e.meet_division for _ev, e in _all_entries(self.meet)
        }
        self.assertIn("SW", divisions)

    def test_individual_entry_has_pad_and_button_1_times(self) -> None:
        with_pad_and_btn = [
            e
            for _ev, e in _all_entries(self.meet, individual_only=True)
            for slot in ("prelim", "swimoff", "finals")
            if _slot_field(e, slot, "pad_time") is not None
            and _slot_field(e, slot, "button_1_time") is not None
        ]
        self.assertGreater(
            len(with_pad_and_btn),
            0,
            "no individual entry found with both pad_time and button_1_time",
        )

    def test_relay_entry_prelim_pad_and_button_times(self) -> None:
        """Relay entry has non-None prelim pad ≈ 111.38 and button_1 ≈ 111.33."""
        relay_entries = [
            e for _ev, e in _all_entries(self.meet, relay_only=True)
        ]
        self.assertGreater(len(relay_entries), 0, "no relay entries found")
        entry = relay_entries[0]
        self.assertIsNotNone(entry.prelim_pad_time, "relay prelim_pad_time is None")
        self.assertIsNotNone(
            entry.prelim_button_1_time, "relay prelim_button_1_time is None"
        )
        self.assertAlmostEqual(entry.prelim_pad_time, 111.38, places=2)
        self.assertAlmostEqual(entry.prelim_button_1_time, 111.33, places=2)
        self.assertIsNotNone(
            entry.prelim_button_2_time, "relay prelim_button_2_time is None"
        )
        self.assertAlmostEqual(entry.prelim_button_2_time, 111.36, places=2)


class TestMM5Col77DivisionAltCodeDivergence(unittest.TestCase):
    """MM5 6.0Cc (2015 WI State/Non-State Open) — col-77 fields.

    Verifies:
      - Team region 'WI' (Wisconsin Swimming LSC; 2-char, cols 54-55)
      - meet_division 'JV' read via col-77 primary path
      - finals_alt_time_code values 'A' and 'K' present
      - Pad-vs-button divergence entry (pad > button due to touchpad error)
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.parsed = parse_hy3(str(FIXTURE_DIR / "mm_col77_division.hy3"))
        cls.meet = cls.parsed.meet

    def test_team_region_wi(self) -> None:
        """Region must be the 2-char LSC code 'WI', not the old buggy 'WIP'."""
        regions = {t.region for t in self.meet.teams.values() if t.region}
        self.assertIn("WI", regions)
        self.assertNotIn("WIP", regions)

    def test_at_least_one_swimmer_citizenship_usa(self) -> None:
        citizenships = {
            s.citizenship
            for t in self.meet.teams.values()
            for s in t.swimmers.values()
        }
        self.assertIn("USA", citizenships)

    def test_meet_division_jv_col77_primary(self) -> None:
        """At least one entry carries meet_division='JV' — proves col-77 primary path."""
        divisions = {e.meet_division for _ev, e in _all_entries(self.meet)}
        self.assertIn("JV", divisions)

    def test_alt_time_codes_a_and_k_present(self) -> None:
        """Both 'A' and 'K' must appear across all slot alt_time_code fields."""
        alt_codes: set = set()
        for _ev, e in _all_entries(self.meet):
            for slot in ("prelim", "swimoff", "finals"):
                code = _slot_field(e, slot, "alt_time_code")
                if code is not None:
                    alt_codes.add(code)
        self.assertIn("A", alt_codes)
        self.assertIn("K", alt_codes)

    def test_divergence_entry_pad_above_button_1(self) -> None:
        """The divergence entry has pad_time (107.39) meaningfully above button_1_time (102.49)."""
        divergence_entries = [
            (_slot_field(e, slot, "pad_time"), _slot_field(e, slot, "button_1_time"))
            for _ev, e in _all_entries(self.meet)
            for slot in ("prelim", "swimoff", "finals")
            if _slot_field(e, slot, "pad_time") is not None
            and _slot_field(e, slot, "button_1_time") is not None
            and _slot_field(e, slot, "pad_time") > _slot_field(e, slot, "button_1_time") + 1.0
        ]
        self.assertGreater(
            len(divergence_entries),
            0,
            "no entry found where pad_time exceeds button_1_time by >1 second",
        )
        pad, btn1 = divergence_entries[0]
        self.assertAlmostEqual(pad, 107.39, places=2)
        self.assertAlmostEqual(btn1, 102.49, places=2)


class TestMM5PadButtonDivergenceMultiRegion(unittest.TestCase):
    """MM5 8.0Fd (2025 MT HOT Tropical) — pad-vs-button divergence.

    Verifies:
      - Team regions MT and WY both present
      - Swimmer citizenship USA
      - finals_alt_time_code 'A' present
      - Divergence entry: pad_time roughly half of button_1_time (touchpad misattribution)
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.parsed = parse_hy3(
            str(FIXTURE_DIR / "mm_pad_button_divergence.hy3")
        )
        cls.meet = cls.parsed.meet

    def test_team_regions_mt_and_wy(self) -> None:
        regions = {t.region for t in self.meet.teams.values() if t.region}
        self.assertIn("MT", regions)
        self.assertIn("WY", regions)

    def test_at_least_one_swimmer_citizenship_usa(self) -> None:
        citizenships = {
            s.citizenship
            for t in self.meet.teams.values()
            for s in t.swimmers.values()
        }
        self.assertIn("USA", citizenships)

    def test_alt_time_code_a_present(self) -> None:
        alt_codes: set = set()
        for _ev, e in _all_entries(self.meet):
            for slot in ("prelim", "swimoff", "finals"):
                code = _slot_field(e, slot, "alt_time_code")
                if code is not None:
                    alt_codes.add(code)
        self.assertIn("A", alt_codes)

    def test_divergence_entry_pad_roughly_half_of_button_1(self) -> None:
        """The divergence entry has pad≈36.26 while button_1≈75.29 (pad < 0.6 * button_1)."""
        divergence_entries = [
            (_slot_field(e, slot, "pad_time"), _slot_field(e, slot, "button_1_time"))
            for _ev, e in _all_entries(self.meet)
            for slot in ("prelim", "swimoff", "finals")
            if _slot_field(e, slot, "pad_time") is not None
            and _slot_field(e, slot, "button_1_time") is not None
            and _slot_field(e, slot, "pad_time") < 0.6 * _slot_field(e, slot, "button_1_time")
        ]
        self.assertGreater(
            len(divergence_entries),
            0,
            "no entry found where pad_time < 0.6 * button_1_time",
        )
        pad, btn1 = divergence_entries[0]
        self.assertAlmostEqual(pad, 36.26, places=2)
        self.assertAlmostEqual(btn1, 75.29, places=2)


if __name__ == "__main__":
    unittest.main()
