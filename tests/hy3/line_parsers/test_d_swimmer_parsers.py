import unittest
from datetime import datetime
from typing import Any
from hytek_parser.hy3.schemas import ParsedHytekFile
from hytek_parser.hy3.line_parsers.d_swimmer_parsers import d1_parser
from hytek_parser.hy3.schemas import Meet, Team, Gender

class TestDSwimmerParser(unittest.TestCase):
    
    def test_d1_parser(self) -> None:
        line = "D1F  260Doe                 Jane                                                        01112016  8                             58"
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team=("FOO", Team("Foo Bar", "FOO", "foo","","","","","","","","","","","",{}))
        opts: dict[str, Any] = {}
        result = d1_parser(line, file, opts)
        for swimmer in result.meet.swimmers.values():
            self.assertEqual(8, swimmer.age)
            self.assertEqual(Gender.FEMALE, swimmer.gender)
            self.assertEqual("Jane", swimmer.first_name)
            self.assertEqual("Doe", swimmer.last_name)
            self.assertEqual(datetime(2016, 1, 11).date(), swimmer.date_of_birth)
            self.assertEqual(None, swimmer.team_id)

    def test_d1_parser_no_dob(self) -> None:
        line = "D1F  260Doe                 Jane                                                                  8                              58"
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team=("FOO", Team("Foo Bar", "FOO", "foo","","","","","","","","","","","",{}))
        opts: dict[str, Any] = {}
        result = d1_parser(line, file, opts)
        for swimmer in result.meet.swimmers.values():
            self.assertEqual(8, swimmer.age)
            self.assertEqual(Gender.FEMALE, swimmer.gender)
            self.assertEqual("Jane", swimmer.first_name)
            self.assertEqual("Doe", swimmer.last_name)
            self.assertIsNone(swimmer.date_of_birth)
            self.assertIsNone(swimmer.team_id)

class TestD1NewFields(unittest.TestCase):
    """Issue #118 — capture D1 citizenship (cols 113-115) and unparsed col 125."""

    def _file_with_team(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = (
            "FOO",
            Team("Foo Bar", "FOO", "FOO", "", "", "", "", "", "", "", "", "", "", "", {}),
        )
        return file, opts

    def test_d1_citizenship_USA(self):
        file, opts = self._file_with_team()
        d1 = "D1M   42Hayon               Gabrielle           Gabby               B           123     11202001  9             USA         N   99"
        self.assertEqual(130, len(d1))
        file = d1_parser(d1, file, opts)
        swimmer = file.meet.swimmers[42]
        self.assertEqual("USA", swimmer.citizenship)
        self.assertEqual("N", swimmer.unparsed_d1_col_125)

    def test_d1_blank_citizenship_and_col_125(self):
        file, opts = self._file_with_team()
        d1 = "D1M   42Hayon               Gabrielle           Gabby               B           123     11202001  9                             99"
        self.assertEqual(130, len(d1))
        file = d1_parser(d1, file, opts)
        swimmer = file.meet.swimmers[42]
        self.assertIsNone(swimmer.citizenship)
        self.assertIsNone(swimmer.unparsed_d1_col_125)


if __name__ == "__main__":
    unittest.main()
