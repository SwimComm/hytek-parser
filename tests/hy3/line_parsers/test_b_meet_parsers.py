import unittest
from datetime import datetime
from hytek_parser.hy3.schemas import ParsedHytekFile
from hytek_parser.hy3.line_parsers.b_meet_parsers import b1_parser

from hytek_parser.hy3.schemas import Meet
from hytek_parser.hy3.line_parsers.b_meet_parsers import b2_parser


class TestBMeetParser(unittest.TestCase):
    
    def test_b1_parser(self) -> None:
        line = "B1NVSL A-Meet ML@OAK                           Oakton                                       062220240622202406012024            61"
        file = ParsedHytekFile()
        opts = {"default_country": "USA"}
        result = b1_parser(line, file, opts)
        self.assertEqual("NVSL A-Meet ML@OAK", result.meet.name)
        self.assertEqual("Oakton", result.meet.facility)
        self.assertEqual(datetime(2024, 6, 22).date(), result.meet.start_date)
        self.assertEqual(datetime(2024, 6, 22).date(), result.meet.end_date)
        self.assertEqual(None, result.meet.altitude)
        
        line = "B1NVSL A-Meet ML@OAK                           Oakton                                       062220240622202406012024 1234       61"
        result = b1_parser(line, file, opts)
        self.assertEqual("NVSL A-Meet ML@OAK", result.meet.name)
        self.assertEqual("Oakton", result.meet.facility)
        self.assertEqual(datetime(2024, 6, 22).date(), result.meet.start_date)
        self.assertEqual(datetime(2024, 6, 22).date(), result.meet.end_date)
        self.assertEqual(1234, result.meet.altitude)
    
class TestB2MeetParser(unittest.TestCase):

    def _file_with_meet(self):
        file = ParsedHytekFile()
        file.meet = Meet()
        return file

    def test_b2_notes_and_sanction(self) -> None:
        line = "B22026  YMCA Short Course Time Trials                                                       010105Y1  0.00  NC26062APTT         76"
        file = self._file_with_meet()
        result = b2_parser(line, file, {"default_country": "USA"})
        self.assertEqual("2026  YMCA Short Course Time Trials", result.meet.notes)
        self.assertEqual("NC26062APTT", result.meet.sanction_number)

    def test_b2_notes_present_no_sanction(self) -> None:
        line = "B2Hosted by NCAP and Sponsored by TYR                                                       010101Y1 18.00                      85"
        file = self._file_with_meet()
        result = b2_parser(line, file, {"default_country": "USA"})
        self.assertEqual("Hosted by NCAP and Sponsored by TYR", result.meet.notes)
        self.assertIsNone(result.meet.sanction_number)

    def test_b2_blank_notes_is_none(self) -> None:
        line = "B2                                                                                          010101Y1  3.00                      61"
        file = self._file_with_meet()
        result = b2_parser(line, file, {"default_country": "USA"})
        self.assertIsNone(result.meet.notes)
        self.assertIsNone(result.meet.sanction_number)


if __name__=='__main__':
	unittest.main()
