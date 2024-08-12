import unittest
from datetime import datetime
from hytek_parser.hy3.schemas import ParsedHytekFile
from hytek_parser.hy3.line_parsers.d_swimmer_parsers import d1_parser
from hytek_parser.hy3.schemas import Meet, Team, Gender

class TestDSwimmerParser(unittest.TestCase):
    
    def test_d1_parser(self) -> None:
        line = "D1F  260Doe                 Jane                                                        01112016  8                             58"
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team=("FOO", Team("Foo Bar", "FOO", "foo","","","","","","","","","","","",{}))
        opts = {}
        result = d1_parser(line, file, opts)
        for swimmer in result.meet.swimmers.values():
            self.assertEqual(8, swimmer.age)
            self.assertEqual(Gender.FEMALE, swimmer.gender)
            self.assertEqual("Jane", swimmer.first_name)
            self.assertEqual("Doe", swimmer.last_name)
            self.assertEqual(datetime(2016, 1, 11).date(), swimmer.date_of_birth)
            self.assertEqual(None, swimmer.team_id)

if __name__=='__main__':
	unittest.main()
 