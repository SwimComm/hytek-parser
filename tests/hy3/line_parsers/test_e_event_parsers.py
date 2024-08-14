import unittest
from hytek_parser.hy3.schemas import ParsedHytekFile
from hytek_parser.hy3.line_parsers.d_swimmer_parsers import d1_parser
from hytek_parser.hy3.line_parsers.e_event_parsers import e1_parser
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

if __name__=='__main__':
	unittest.main()
     