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


if __name__ == "__main__":
    unittest.main()
