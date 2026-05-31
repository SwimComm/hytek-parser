import unittest

from hytek_parser.hy3.schemas import (
    Meet, ParsedHytekFile, Team,
)
from hytek_parser.hy3.line_parsers.d_swimmer_parsers import d1_parser
from hytek_parser.hy3.line_parsers.f_relay_parsers import f1_parser, f2_parser, f3_parser


class TestF2BlankDateColumn(unittest.TestCase):
    """Bug 1 — F2 lines with blank date column must populate timing fields
    and leave date None instead of raising."""

    def _build_file_with_relay_entry(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = (
            "FOO",
            Team("Foo Bar", "FOO", "foo", "", "", "", "", "", "", "", "", "", "", "", {}),
        )
        # F1 — declare the relay entry. Use a real-shaped F1 line (will be
        # replaced/extended in Task 2 tests when per-entry attribution lands).
        f1_line = "F1FOO  A   0FFG   200E  0109  0S 30.00  2   112.37Y  112.37Y   52.00    0.00   NN   4           NA                              29"
        file = f1_parser(f1_line, file, opts)
        return file, opts

    def test_f2_parser_with_blank_date_does_not_raise(self):
        file, opts = self._build_file_with_relay_entry()
        # F2 line with finals time, blank date column (positions 103-110 are spaces)
        f2_line = "F2F  111.06Y       0  2  6  4   4  0  111.00  111.16    0.00       111.06     0.00                                              46"
        result = f2_parser(f2_line, file, opts)
        event_num, event = result.meet.last_event
        entry = event.last_entry
        self.assertIsNotNone(entry.finals_time)
        self.assertEqual(111.06, entry.finals_time)
        self.assertIsNone(entry.finals_date)


class TestF1PerEntryAttribution(unittest.TestCase):
    """Bug 2-A — relay_team_id and relay_swim_team_code must live on
    EventEntry (not Event), so that two relays from different teams in the
    same event are distinct entries with correct attribution."""

    def _make_file(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = (
            "AHC",
            Team("AHC Team", "AHC", "ahc", "", "", "", "", "", "", "", "", "", "", "", {}),
        )
        return file, opts

    def test_two_teams_same_event_yield_two_entries_with_per_entry_attribution(self):
        file, opts = self._make_file()
        # F1 for AHC's A relay, event 2 (200 medley, 13-14 girls)
        f1_a = "F1AHC  A   0FFG   200E  0109  0S 30.00  2   112.37Y  112.37Y   52.00    0.00   NN   4           NA                              29"
        # F1 for HA's A relay, same event 2 — DIFFERENT seed time so identity
        # is unambiguous even before we add per-entry attribution
        f1_b = "F1HA   A   0FFG   200E  0109  0S 30.00  2   111.40Y  111.40Y   54.00    0.00   NN   4           NA                              98"
        file = f1_parser(f1_a, file, opts)
        file = f1_parser(f1_b, file, opts)
        event = file.meet.events["2"]

        self.assertEqual(2, len(event.entries), "expected two distinct entries (AHC + HA)")
        self.assertEqual("AHC", event.entries[0].relay_swim_team_code)
        self.assertEqual("A", event.entries[0].relay_team_id)
        self.assertEqual("HA", event.entries[1].relay_swim_team_code)
        self.assertEqual("A", event.entries[1].relay_team_id)

    def test_same_seed_time_two_teams_same_event_yield_two_entries(self):
        """Stronger guard for Bug 2-A: with the pre-fix logic, two relays
        from different teams with identical seed times collapsed into one
        EventEntry because the identity tuple was (swimmers=[], event_number,
        seed_time, ...). Type-aware same_swimmer_entry_as must keep them
        distinct."""
        file, opts = self._make_file()
        # Both relays use the SAME seed time (112.37) — this is the actual
        # collapse-bug scenario. Pre-fix: one collapsed entry. Post-fix: two.
        f1_a = "F1AHC  A   0FFG   200E  0109  0S 30.00  2   112.37Y  112.37Y   52.00    0.00   NN   4           NA                              29"
        f1_b = "F1HA   A   0FFG   200E  0109  0S 30.00  2   112.37Y  112.37Y   52.00    0.00   NN   4           NA                              98"
        file = f1_parser(f1_a, file, opts)
        file = f1_parser(f1_b, file, opts)
        event = file.meet.events["2"]

        self.assertEqual(2, len(event.entries),
                         "same seed time must not collapse different teams")
        self.assertEqual("AHC", event.entries[0].relay_swim_team_code)
        self.assertEqual("HA", event.entries[1].relay_swim_team_code)


class TestF3DictKeyedSwimmers(unittest.TestCase):
    """Bug 2-B — F3 must populate entry.swimmers as dict[int, Swimmer]
    keyed by leg number, preserving leg numbers including alternates
    (legs 5..8) without conflating them with racers."""

    def _file_with_relay_entry_and_4_swimmers(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = (
            "FOO",
            Team("Foo Bar", "FOO", "foo", "", "", "", "", "", "", "", "", "", "", "", {}),
        )
        # Set up 8 swimmers in the meet so F3 can resolve any of them
        # D1 format: pos3=gender(1), pos4-8=meet_id(5), pos9-28=last_name(20),
        #            pos29-48=first_name(20), pos89-96=dob(8), pos97-99=age(3)
        for i in range(1, 9):
            ln = f"LastName{i}"
            fn = f"First{i}"
            d_line = f"D1M{i:5d}{ln:<20}{fn:<20}                                        10272010 13                             {i:02d}"
            file = d1_parser(d_line, file, opts)
        # F1 for the relay
        f1_line = "F1FOO  A   0FFG   200E  0109  0S 30.00  2   112.37Y  112.37Y   52.00    0.00   NN   4           NA                              29"
        file = f1_parser(f1_line, file, opts)
        return file, opts

    def test_f3_with_4_swimmers_yields_dict_keyed_1_to_4(self):
        file, opts = self._file_with_relay_entry_and_4_swimmers()
        # F3 line: 4 swimmers in legs 1, 2, 3, 4
        # Format: 'F3 ' + per-entry blocks (13 chars each: 5-char meet_id, 6-char pad, 1-char leg, 1-char filler)
        f3_line = "F3     1      1     2      2     3      3     4      4                                                                                                                        "
        result = f3_parser(f3_line, file, opts)
        entry = result.meet.last_event[1].last_entry
        self.assertIsInstance(entry.swimmers, dict)
        self.assertEqual(set(entry.swimmers.keys()), {1, 2, 3, 4})

    def test_f3_with_8_swimmers_keeps_all_8_keyed(self):
        file, opts = self._file_with_relay_entry_and_4_swimmers()
        # F3 line: 8 swimmers in legs 1..8 (4 racers + 4 alternates)
        f3_line = "F3     1      1     2      2     3      3     4      4     5      5     6      6     7      7     8      8              "
        result = f3_parser(f3_line, file, opts)
        entry = result.meet.last_event[1].last_entry
        self.assertEqual(set(entry.swimmers.keys()), {1, 2, 3, 4, 5, 6, 7, 8})


class TestF2BackupTimingFields(unittest.TestCase):
    """F2 timing fields. Same offsets as E2 for the five timing
    columns; alt_time_code at col 111 (NOT 96) because F2's date is at col 103."""

    def _build_file_with_relay_entry(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = (
            "FOO",
            Team("Foo Bar", "FOO", "FOO", "", "", "", "", "", "", "", "", "", "", "", {}),
        )
        f1_line = "F1FOO  A   0FFG   200E  0109  0S 30.00  2   112.37Y  112.37Y   52.00    0.00   NN   4           NA                              29"
        file = f1_parser(f1_line, file, opts)
        return file, opts

    def test_f2_with_buttons_and_alt_code_at_col_111(self):
        file, opts = self._build_file_with_relay_entry()
        # F2 with pad+buttons populated and 'A' alt-code at col 111. F2 date at cols 103-110.
        # Verified offsets: button_1(39-46)=108.20, button_2(47-54)=108.10,
        # button_3(55-62)=0.00, pad(63-74)=108.15, backup_4(75-82)=0.00,
        # date(103-110)=02012025, alt_code(111)=A
        f2_line = "F2F  108.15Y        0  2  6  4   4  0   108.20  108.10    0.00      108.15    0.00                    02012025A                 46"
        file = f2_parser(f2_line, file, opts)
        event = file.meet.events[list(file.meet.events.keys())[0]]
        entry = event.last_entry
        self.assertAlmostEqual(108.15, entry.finals_time, places=2)
        self.assertAlmostEqual(108.20, entry.finals_button_1_time, places=2)
        self.assertAlmostEqual(108.10, entry.finals_button_2_time, places=2)
        self.assertIsNone(entry.finals_button_3_time)   # 0.00 → None
        self.assertAlmostEqual(108.15, entry.finals_pad_time, places=2)
        self.assertIsNone(entry.finals_backup_4_time)   # 0.00 → None
        self.assertEqual("A", entry.finals_alt_time_code)

    def test_f2_blank_alt_code(self):
        file, opts = self._build_file_with_relay_entry()
        # F2 with blank alt_code at col 111 — should surface as None
        # Verified offsets: button_1(39-46)=111.00, button_2(47-54)=111.16,
        # pad(63-74)=111.06, date(103-110)=02012025, alt_code(111)=blank
        f2_line = "F2F  111.06Y        0  2  6  4   4  0   111.00  111.16    0.00      111.06    0.00                    02012025                  46"
        file = f2_parser(f2_line, file, opts)
        event = file.meet.events[list(file.meet.events.keys())[0]]
        entry = event.last_entry
        self.assertAlmostEqual(111.06, entry.finals_time, places=2)
        self.assertAlmostEqual(111.00, entry.finals_button_1_time, places=2)
        self.assertAlmostEqual(111.16, entry.finals_button_2_time, places=2)
        self.assertAlmostEqual(111.06, entry.finals_pad_time, places=2)
        self.assertIsNone(entry.finals_alt_time_code)


if __name__ == "__main__":
    unittest.main()
