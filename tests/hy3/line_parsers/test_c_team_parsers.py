import unittest
from hytek_parser.hy3.schemas import ParsedHytekFile, Meet
from hytek_parser.hy3.line_parsers.c_team_parsers import c1_parser


class TestC1TeamRegion(unittest.TestCase):
    """Issue #118 — populate Team.region from the C1 LSC code at cols 54-56."""

    def _file(self):
        file = ParsedHytekFile()
        file.meet = Meet()
        return file, {"default_country": "USA"}

    def test_c1_region_from_col_54(self):
        file, opts = self._file()
        # Real C1 shape: code(3-7), name(8-37), short(38-53), LSC(54-56).
        c1 = "C1ANA  Andover/North Andover YMCA    Andover-MA      NE                                                               0  0      27"
        self.assertEqual(130, len(c1))
        file = c1_parser(c1, file, opts)
        _, team = file.meet.last_team
        self.assertEqual("ANA", team.code)
        self.assertEqual("NE", team.region)

    def test_c1_blank_region_is_none(self):
        file, opts = self._file()
        # Same shape, LSC columns blank
        c1 = "C1AMFY AuglaizeMercer YMCA          AuglaizeMercerOH                                                                  0  0      27"
        self.assertEqual(130, len(c1))
        file = c1_parser(c1, file, opts)
        _, team = file.meet.last_team
        self.assertIsNone(team.region)


if __name__ == "__main__":
    unittest.main()
