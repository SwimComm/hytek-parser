import unittest
from hytek_parser.hy3.schemas import ParsedHytekFile
from hytek_parser.hy3.line_parsers.d_swimmer_parsers import d1_parser
from hytek_parser.hy3.line_parsers.e_event_parsers import e1_parser, e2_parser
from hytek_parser.hy3.schemas import Meet, Team, Gender, Stroke

class TestEEventParser(unittest.TestCase):
    
    def test_e1_parser(self) -> None:
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = ("FOO", Team("Foo Bar", "FOO", "foo","","","","","","","","","","","",{}))
        d_line = "D1M   27Hansen              Mads                                                        10272010 13                             27"
        e_line = "E1M   27HanseXX    50D 11109  0U  0.00 22X   37.41S   37.41S    0.00    0.00  0NN               N                               70"
        file = d1_parser(d_line, file, opts)
        result = e1_parser(e_line, file, opts)
        event = result.meet.events.get("22X")
        self.assertIsNotNone(event)
        self.assertEqual(Gender.UNKNOWN, event.gender)
        self.assertEqual(Stroke.BUTTERFLY, event.stroke)
        self.assertEqual(50, event.distance)
        self.assertEqual(11, event.age_min)
        self.assertEqual(109, event.age_max)
        self.assertEqual("22X", event.number)
        entry = event.last_entry
        self.assertEqual(entry.exhibition, False)

    def test_e1_parser_with_exhibition(self) -> None:
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = ("FOO", Team("Foo Bar", "FOO", "foo","","","","","","","","","","","",{}))
        d_line = "D1M   27Hansen              Mads                                                        10272010 13                             27"
        e_line = "E1M   27HanseMM    50A 15 18  0U  0.00  6B   27.76S   27.76S    0.00    0.00  0NN  X            N                               60"
        file = d1_parser(d_line, file, opts)
        result = e1_parser(e_line, file, opts)
        event = result.meet.events.get("6B")
        self.assertIsNotNone(event)
        self.assertEqual(Gender.MALE, event.gender)
        self.assertEqual(Stroke.FREESTYLE, event.stroke)
        self.assertEqual(50, event.distance)
        self.assertEqual(15, event.age_min)
        self.assertEqual(18, event.age_max)
        self.assertEqual("6B", event.number)
        entry = event.last_entry
        self.assertEqual(entry.exhibition, True)

    def test_e1_parser_mixed_exhibition_tracks_per_entry(self) -> None:
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = ("FOO", Team("Foo Bar", "FOO", "foo","","","","","","","","","","","",{}))
        d_line_27 = "D1M   27Hansen              Mads                                                        10272010 13                             27"
        d_line_28 = "D1M   28Hansen              Otto                                                        10272010 13                             28"
        e_line_non_exh = "E1M   27HanseXX    50D 11109  0U  0.00 22X   37.41S   37.41S    0.00    0.00  0NN               N                               70"
        e_line_exh = "E1M   28HanseYY    50D 11109  0U  0.00 22X   37.55S   37.55S    0.00    0.00  0NN  X            N                               70"

        file = d1_parser(d_line_27, file, opts)
        file = d1_parser(d_line_28, file, opts)
        file = e1_parser(e_line_non_exh, file, opts)
        file = e1_parser(e_line_exh, file, opts)

        event = file.meet.events.get("22X")
        self.assertIsNotNone(event)
        self.assertEqual(2, len(event.entries))
        self.assertEqual(False, event.entries[0].exhibition)
        self.assertEqual(True, event.entries[1].exhibition)


class TestE2BlankDateColumn(unittest.TestCase):
    """Bug 1 — MM2 2.0 (and other MM versions) export E2 lines with a blank
    date column. e2_parser must populate timing fields and leave date as None
    rather than raising ValueError on the empty strptime."""

    def _build_file_with_event(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = ("FOO", Team("Foo Bar", "FOO", "foo", "", "", "", "", "", "", "", "", "", "", "", {}))
        d_line = "D1M   27Hansen              Mads                                                        10272010 13                             27"
        e1_line = "E1M   27HanseXX    50D 11109  0U  0.00 22X   37.41S   37.41S    0.00    0.00  0NN               N                               70"
        file = d1_parser(d_line, file, opts)
        file = e1_parser(e1_line, file, opts)
        return file, opts

    def test_e2_parser_with_blank_date_does_not_raise(self):
        file, opts = self._build_file_with_event()
        # E2 line with blank date column (positions 88-95 are spaces) — MM2 2.0 shape
        e2_line = "E2F   54.79Y       0  2  3  4  12  0    0.00   54.93    0.00        54.79     0.00                                        0     25"
        # Should not raise
        result = e2_parser(e2_line, file, opts)
        event = result.meet.events.get("22X")
        entry = event.last_entry
        self.assertIsNotNone(entry.finals_time)
        self.assertEqual(54.79, entry.finals_time)
        self.assertIsNone(entry.finals_date)


class TestE1MeetDivision(unittest.TestCase):
    """capture Meet Division at cols 77-79 (e.g. 'VR', 'JV', 'A'/'AA'/numeric)."""

    def _build_file(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = (
            "FOO",
            Team("Foo Bar", "FOO", "FOO", "", "", "", "", "", "", "", "", "", "", "", {}),
        )
        d_line = "D1M   27Hansen              Mads                                                        10272010 13                             27"
        file = d1_parser(d_line, file, opts)
        return file, opts

    def test_e1_meet_division_VR(self):
        file, opts = self._build_file()
        # E1 with 'VR ' at cols 77-79 (1-based); indices [76:79] in the 130-char line.
        e1 = "E1M   27HanseXX    50D 11109  0U  0.00 22X   37.41S   37.41S    0.00    0.00VR NN               N                               70"
        self.assertEqual(130, len(e1))
        file = e1_parser(e1, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertEqual("VR", entry.meet_division)

    def test_e1_meet_division_blank(self):
        file, opts = self._build_file()
        e1 = "E1M   27HanseXX    50D 11109  0U  0.00 22X   37.41S   37.41S    0.00    0.00   NN               N                               70"
        self.assertEqual(130, len(e1))
        file = e1_parser(e1, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertIsNone(entry.meet_division)

    def test_e1_meet_division_col92_fallback(self):
        """MM4/MM5-7.0Fa store the division at cols 92-93 (col 77-79 blank).
        meet_division must fall back to col 92."""
        file, opts = self._build_file()
        # 130-char line: col 77-79 (indices [76:79]) is blank, col 92-93 (indices [91:93]) = 'SW'
        e1 = "E1M   27HanseXX    50D 11109  0U  0.00 22X   37.41S   37.41S    0.00    0.00   NN          SW   N                               70"
        self.assertEqual(130, len(e1))
        file = e1_parser(e1, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertEqual("SW", entry.meet_division)


class TestE2BackupTimingFields(unittest.TestCase):
    """capture pad, 3 buttons, backup_4, alt_time_code from E2 rows."""

    def _build_file(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = (
            "FOO",
            Team("Foo Bar", "FOO", "FOO", "", "", "", "", "", "", "", "", "", "", "", {}),
        )
        d_line = "D1M   27Hansen              Mads                                                        10272010 13                             27"
        e1_line = "E1M   27HanseXX    50D 11109  0U  0.00 22X   37.41S   37.41S    0.00    0.00  0NN               N                               70"
        file = d1_parser(d_line, file, opts)
        file = e1_parser(e1_line, file, opts)
        return file, opts

    def test_e2_with_pad_and_buttons_and_alt_code(self):
        """Allie Cooper failure mode: pad=12.80, buttons=41.16/40.88, alt=K."""
        file, opts = self._build_file()
        # 130-char E2 line. Column anchors (1-indexed):
        #  4-11 time, 12 course, 13 time_code, 21-23 heat, 24-26 lane,
        #  27-29 heat_place, 30-33 overall_place,
        #  39-46 button_1, 47-54 button_2, 55-62 button_3,
        #  63-74 pad, 75-82 backup_4, 88-95 date, 96 alt_code.
        e2 = "E2F   12.80Y          4  5  1   1   0    41.16   40.88    0.00       12.80    0.00     12012018K                          0     66"
        self.assertEqual(130, len(e2))
        file = e2_parser(e2, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertEqual(12.80, entry.finals_time)
        self.assertAlmostEqual(12.80, entry.finals_pad_time, places=2)
        self.assertAlmostEqual(41.16, entry.finals_button_1_time, places=2)
        self.assertAlmostEqual(40.88, entry.finals_button_2_time, places=2)
        self.assertIsNone(entry.finals_button_3_time)  # 0.00 → None
        self.assertIsNone(entry.finals_backup_4_time)
        self.assertEqual("K", entry.finals_alt_time_code)

    def test_e2_clean_row_with_all_three_buttons(self):
        """Three populated buttons, blank alt code, clean pad."""
        file, opts = self._build_file()
        e2 = "E2F   54.00Y          2  3  2  14   0    54.25   54.22   54.16       54.00    0.00     11202010                           0     66"
        self.assertEqual(130, len(e2))
        file = e2_parser(e2, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertAlmostEqual(54.25, entry.finals_button_1_time, places=2)
        self.assertAlmostEqual(54.22, entry.finals_button_2_time, places=2)
        self.assertAlmostEqual(54.16, entry.finals_button_3_time, places=2)
        self.assertAlmostEqual(54.00, entry.finals_pad_time, places=2)
        self.assertIsNone(entry.finals_alt_time_code)

    def test_e2_blank_timing_fields_all_none(self):
        """Hand-timed: no pad/buttons recorded → all six new fields None."""
        file, opts = self._build_file()
        e2 = "E2F   54.79Y          2  3  4  12   0     0.00    0.00    0.00        0.00    0.00     12012018                           0     25"
        self.assertEqual(130, len(e2))
        file = e2_parser(e2, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertEqual(54.79, entry.finals_time)
        self.assertIsNone(entry.finals_pad_time)
        self.assertIsNone(entry.finals_button_1_time)
        self.assertIsNone(entry.finals_button_2_time)
        self.assertIsNone(entry.finals_button_3_time)
        self.assertIsNone(entry.finals_backup_4_time)
        self.assertIsNone(entry.finals_alt_time_code)

    def test_e2_genuinely_blank_button_field_is_none(self):
        """A blank (all-spaces) button field must yield None, not a time code enum."""
        file, opts = self._build_file()
        # button_1 (cols 39-46, 0-indexed [38:46]) left blank/spaces instead of 0.00
        e2 = "E2F   54.79Y          2  3  4  12   0             0.00    0.00        0.00    0.00     12012018                           0     25"
        self.assertEqual(130, len(e2))
        file = e2_parser(e2, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertIsNone(entry.finals_button_1_time)


if __name__=='__main__':
    unittest.main()
