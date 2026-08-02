import unittest

from hytek_parser._utils import select_from_enum
from hytek_parser.hy3.schemas import Gender


class TestGenderCaseInsensitivity(unittest.TestCase):
    def test_sex_column_decodes_regardless_of_case(self) -> None:
        """A lowercase sex byte states a fact; a blank one does not.

        UNKNOWN is the "file did not say" value. Folding a lowercase 'm'
        into it records a stated fact as unstated, and every consumer
        downstream then treats the swimmer as having no gender at all.
        These cases belong in ONE test: upcasing unconditionally would
        fix the first assertion and break the second.
        """
        # The fix.
        self.assertIs(Gender.MALE, select_from_enum(Gender, "m"))
        self.assertIs(Gender.FEMALE, select_from_enum(Gender, "f"))
        self.assertIs(Gender.UNKNOWN, select_from_enum(Gender, "u"))

        # Unchanged: the ordinary uppercase path.
        self.assertIs(Gender.MALE, select_from_enum(Gender, "M"))
        self.assertIs(Gender.FEMALE, select_from_enum(Gender, "F"))
        self.assertIs(Gender.UNKNOWN, select_from_enum(Gender, "U"))

        # Unchanged: genuinely-unstated. extract() strips, so "" is the
        # real blank column and " " is the pre-strip form.
        self.assertIs(Gender.UNKNOWN, select_from_enum(Gender, ""))
        self.assertIs(Gender.UNKNOWN, select_from_enum(Gender, " "))

        # Unchanged: 'X' marks a Mixed event on millions of records and
        # must keep falling through, and an unrecognized byte must stay
        # unrecognized rather than be coerced into a plausible value.
        self.assertIs(Gender.UNKNOWN, select_from_enum(Gender, "X"))
        self.assertIs(Gender.UNKNOWN, select_from_enum(Gender, "s"))
        self.assertIs(Gender.UNKNOWN, select_from_enum(Gender, "S"))


if __name__ == "__main__":
    unittest.main()
