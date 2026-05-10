import unittest

from hytek_parser.hy3.schemas import (
    Meet, ParsedHytekFile, Team,
)
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


if __name__ == "__main__":
    unittest.main()
