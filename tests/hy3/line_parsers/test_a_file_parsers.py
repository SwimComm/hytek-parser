import unittest
from datetime import datetime
from hytek_parser.hy3.schemas import ParsedHytekFile
from hytek_parser.hy3.line_parsers.a_file_parsers import a1_parser

class TestA1Parser(unittest.TestCase):
    
    def test_date_created(self) -> None:
        line = "A102Meet Entries             Hy-Tek, Ltd    Win-TM 8.0Ga  06272024 12:00 PMOakton Swim Team"
        file = ParsedHytekFile()
        opts = {}
        result = a1_parser(line, file, opts)
        self.assertEqual(datetime.fromisoformat('2024-06-27T12:00:00'), result.date_created)
    
if __name__=='__main__':
	unittest.main()