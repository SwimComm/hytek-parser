import unittest
from datetime import datetime
from hytek_parser.hy3.schemas import ParsedHytekFile
from hytek_parser.hy3.line_parsers.b_meet_parsers import b1_parser

class TestB1Parser(unittest.TestCase):
    
    def test_meet_line_parse(self) -> None:
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
    
if __name__=='__main__':
	unittest.main()
 