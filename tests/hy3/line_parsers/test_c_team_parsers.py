import unittest
from hytek_parser.hy3.schemas import ParsedHytekFile, Meet
from hytek_parser.hy3.line_parsers.c_team_parsers import c1_parser


# Helper to build a deterministic 130-char C1 line from parts.
# Layout (1-based cols):
#   1-2   prefix  "C1"
#   3-7   code    5 chars
#   8-37  name    30 chars
#  38-53  short   16 chars
#  54-55  lsc     2 chars
#  56-85  c1      30 chars  (contact_name_1)
#  86-115 c2      30 chars  (contact_name_2)
# 116-128 flags   13 chars
# 129-130 chk     2 chars
def _make_c1(
    code: str = "TESTC",
    name: str = "Test Team",
    short: str = "Test Short",
    lsc: str = "NE",
    contact1: str = "",
    contact2: str = "",
    flags: str = "0  0         ",
    chk: str = "27",
) -> str:
    line = (
        "C1"
        + code.ljust(5)[:5]
        + name.ljust(30)[:30]
        + short.ljust(16)[:16]
        + lsc.ljust(2)[:2]
        + contact1.ljust(30)[:30]
        + contact2.ljust(30)[:30]
        + flags.ljust(13)[:13]
        + chk.ljust(2)[:2]
    )
    assert len(line) == 130, f"line length {len(line)} != 130"
    return line


class TestC1TeamRegion(unittest.TestCase):
    """populate Team.region from the C1 LSC code at cols 54-55."""

    def _file(self):
        file = ParsedHytekFile()
        file.meet = Meet()
        return file, {"default_country": "USA"}

    def test_c1_region_from_col_54(self):
        file, opts = self._file()
        # Real C1 shape: code(3-7), name(8-37), short(38-53), LSC(54-55).
        # LSC has trailing spaces so 2-char or 3-char extraction both work here.
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

    def test_c1_region_width_regression(self):
        """Regression: LSC must be exactly 2 chars; contact name at col 56 must NOT bleed in.

        With extract(54, 3) the region becomes e.g. 'NED' (first letter of
        'David McCrary').  With the correct extract(54, 2) it is 'NE'.
        """
        file, opts = self._file()
        c1 = _make_c1(lsc="NE", contact1="David McCrary")
        self.assertEqual(130, len(c1))
        file = c1_parser(c1, file, opts)
        _, team = file.meet.last_team
        # Must be exactly 2 chars — NOT 'NED'
        self.assertEqual("NE", team.region)


class TestC1ContactNames(unittest.TestCase):
    """C1 cols 56-85 / 86-115 → Team.contact_name_1 / contact_name_2."""

    def _file(self):
        file = ParsedHytekFile()
        file.meet = Meet()
        return file, {"default_country": "USA"}

    def test_contact_name_1_populated(self):
        file, opts = self._file()
        c1 = _make_c1(contact1="Test Contact")
        file = c1_parser(c1, file, opts)
        _, team = file.meet.last_team
        self.assertEqual("Test Contact", team.contact_name_1)

    def test_contact_name_2_populated(self):
        file, opts = self._file()
        c1 = _make_c1(contact1="Test Contact", contact2="Another Person")
        file = c1_parser(c1, file, opts)
        _, team = file.meet.last_team
        self.assertEqual("Another Person", team.contact_name_2)

    def test_contact_name_1_and_2_identical(self):
        """Contact names are often identical — both should be populated."""
        file, opts = self._file()
        c1 = _make_c1(contact1="Same Person", contact2="Same Person")
        file = c1_parser(c1, file, opts)
        _, team = file.meet.last_team
        self.assertEqual("Same Person", team.contact_name_1)
        self.assertEqual("Same Person", team.contact_name_2)

    def test_blank_contact_1_is_none(self):
        """Blank contact_name_1 slot → None."""
        file, opts = self._file()
        c1 = _make_c1(contact1="", contact2="")
        file = c1_parser(c1, file, opts)
        _, team = file.meet.last_team
        self.assertIsNone(team.contact_name_1)

    def test_blank_contact_2_is_none(self):
        """Blank contact_name_2 slot → None even when contact_name_1 is set."""
        file, opts = self._file()
        c1 = _make_c1(contact1="Test Contact", contact2="")
        file = c1_parser(c1, file, opts)
        _, team = file.meet.last_team
        self.assertIsNone(team.contact_name_2)


if __name__ == "__main__":
    unittest.main()
