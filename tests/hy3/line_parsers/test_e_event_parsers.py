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


if __name__=='__main__':
    unittest.main()
