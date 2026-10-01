import datetime
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


class TestE1FloatDistance(unittest.TestCase):
    """distance is a float, so non-integer values (e.g. open-water '2.4' miles)
    survive the parse instead of being truncated to 0 by an int cast."""

    def _build_file(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = (
            "TST",
            Team("Test Team", "TST", "TST", "", "", "", "", "", "", "", "", "", "", "", {}),
        )
        # Synthetic swimmer — placeholder name, no real person
        d_line = "D1M   10Doe                 John                                                        01011990 30                             10"
        file = d1_parser(d_line, file, opts)
        return file, opts

    def test_float_distance_preserved(self):
        """'   2.4' (open-water miles) -> distance=2.4."""
        file, opts = self._build_file()
        # distance field (cols 16-21) = '   2.4'; safe_cast(float, '2.4') -> 2.4
        e1 = "E1M   10Doe  MM   2.4A 11109  0U  0.00  1    30.00S   30.00S    0.00    0.00  0NN               N                               70"
        file = e1_parser(e1, file, opts)
        event = file.meet.events["1"]
        self.assertEqual(2.4, event.distance)

    def test_integer_distance_is_float(self):
        """'  1000' -> distance=1000.0."""
        file, opts = self._build_file()
        e1 = "E1M   10Doe  MM  1000A 11109  0U  0.00  2    30.00S   30.00S    0.00    0.00  0NN               N                               70"
        file = e1_parser(e1, file, opts)
        event = file.meet.events["2"]
        self.assertEqual(1000.0, event.distance)

    def test_blank_distance_is_zero(self):
        """Blank distance field -> distance=0.0."""
        file, opts = self._build_file()
        e1 = "E1M   10Doe  MM      A 11109  0U  0.00  3    30.00S   30.00S    0.00    0.00  0NN               N                               70"
        file = e1_parser(e1, file, opts)
        event = file.meet.events["3"]
        self.assertEqual(0.0, event.distance)


class TestE2ResultDateColumn(unittest.TestCase):
    """Blank or invalid E2 dates must not discard otherwise valid results."""

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

    def test_e2_parser_with_invalid_date_does_not_raise(self):
        file, opts = self._build_file_with_event()
        e2_line = "E2F   54.79Y       0  2  3  4  12  0    0.00   54.93    0.00        54.79     0.00     99999999                           0     25"
        result = e2_parser(e2_line, file, opts)
        entry = result.meet.events["22X"].last_entry
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


class TestE2ReactionTime(unittest.TestCase):
    """E2 col 83-87 carries the swimmer's start reaction time."""

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

    def test_e2_reaction_time_populated(self):
        """Real row: 2026 CA SCS Summer A-G Champs, reaction 0.56."""
        file, opts = self._build_file()
        e2 = "E2P   38.78L       0  1  3  6  34  0   38.87   38.63    0.00        38.78     0.00 0.5607242026    0                            27"
        self.assertEqual(130, len(e2))
        file = e2_parser(e2, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertAlmostEqual(0.56, entry.prelim_reaction_time, places=2)

    def test_e2_reaction_time_does_not_shift_the_date(self):
        """Offset regression: reading col 83-87 must leave the date at col 88.

        A one-column error still yields plausible-looking floats, so the date
        is the only cheap tripwire that catches it.
        """
        file, opts = self._build_file()
        e2 = "E2P   38.78L       0  1  3  6  34  0   38.87   38.63    0.00        38.78     0.00 0.5607242026    0                            27"
        file = e2_parser(e2, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertEqual(datetime.date(2026, 7, 24), entry.prelim_date)
        # The pad time must also be untouched by the new read.
        self.assertAlmostEqual(38.78, entry.prelim_pad_time, places=2)

    def test_e2_zero_reaction_time_is_none(self):
        """Real row: 2014 STAR Tarheel States, reaction column reads 0.00."""
        file, opts = self._build_file()
        e2 = "E2F   56.83Y       0  1  3  5  15  0   56.75    0.00    0.00        56.83     0.00 0.0003222014                           0     76"
        self.assertEqual(130, len(e2))
        file = e2_parser(e2, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertIsNone(entry.finals_reaction_time)

    def test_e2_blank_reaction_time_is_none(self):
        """Real row from the same meet with an empty reaction column."""
        file, opts = self._build_file()
        e2 = "E2P   36.26L       0  1  3  3  74  0   36.43   36.46    0.00        36.26     0.00     07262026    0                            56"
        self.assertEqual(130, len(e2))
        file = e2_parser(e2, file, opts)
        entry = file.meet.events["22X"].last_entry
        self.assertIsNone(entry.prelim_reaction_time)
        self.assertEqual(datetime.date(2026, 7, 26), entry.prelim_date)


class TestE2DqSlotAnchor(unittest.TestCase):
    """e2_parser records the DQ slot it populates under opts[LAST_DQ_SLOT_KEY] so
    the H1/H2 detail lines that follow attach to that slot; a non-DQ result
    clears it."""

    def _build_file(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = ("FOO", Team("Foo Bar", "FOO", "foo", "", "", "", "", "", "", "", "", "", "", "", {}))
        d_line = "D1M   27Hansen              Mads                                                        10272010 13                             27"
        e1_line = "E1M   27HanseXX    50D 11109  0U  0.00 22X   37.41S   37.41S    0.00    0.00  0NN               N                               70"
        file = d1_parser(d_line, file, opts)
        file = e1_parser(e1_line, file, opts)
        return file, opts

    @staticmethod
    def _e2_dq(result_type, dq_code):
        base = "E2P   38.78L       0  1  3  6  34  0   38.87   38.63    0.00        38.78     0.00 0.5607242026    0                            27"
        line = list(base)
        line[2] = result_type          # col 3: P / S / F
        line[12] = "Q"                 # col 13: DISQUALIFICATION time code
        line[13], line[14] = dq_code[0], dq_code[1]  # cols 14-15: DQ code
        return "".join(line)

    def test_finals_dq_sets_anchor(self):
        from hytek_parser.hy3.line_parsers.h_dq_parsers import LAST_DQ_SLOT_KEY
        file, opts = self._build_file()
        file = e2_parser(self._e2_dq("F", "7T"), file, opts)
        self.assertEqual("finals_dq_info", opts[LAST_DQ_SLOT_KEY])

    def test_prelim_dq_sets_anchor(self):
        from hytek_parser.hy3.line_parsers.h_dq_parsers import LAST_DQ_SLOT_KEY
        file, opts = self._build_file()
        file = e2_parser(self._e2_dq("P", "1M"), file, opts)
        self.assertEqual("prelim_dq_info", opts[LAST_DQ_SLOT_KEY])

    def test_non_dq_clears_anchor(self):
        from hytek_parser.hy3.line_parsers.h_dq_parsers import LAST_DQ_SLOT_KEY
        file, opts = self._build_file()
        opts[LAST_DQ_SLOT_KEY] = "finals_dq_info"  # stale from a prior DQ
        clean = "E2P   38.78L       0  1  3  6  34  0   38.87   38.63    0.00        38.78     0.00 0.5607242026    0                            27"
        file = e2_parser(clean, file, opts)
        self.assertIsNone(opts[LAST_DQ_SLOT_KEY])


if __name__=='__main__':
    unittest.main()
