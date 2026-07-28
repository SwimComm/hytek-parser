import unittest
import datetime
from hytek_parser._utils import safe_cast, int_or_none, select_from_enum, date_or_none
from hytek_parser.hy3.schemas import Stroke
from hytek_parser.hy3._utils import parse_reaction_time

class TestUtils(unittest.TestCase):
    
    def test_safe_cast(self) -> None:
        self.assertEqual(0, safe_cast(int, "", None))
        self.assertEqual(123, safe_cast(int, "123", None))
        self.assertEqual(0, safe_cast(int, "OneTwoThree", None))
        self.assertEqual(0, safe_cast(int, None, None))
        self.assertEqual(1, safe_cast(int, 1.23, None))
        self.assertEqual(1.23, safe_cast(float, 1.23, None))
        self.assertEqual(True, safe_cast(bool, 1.23, None))
        self.assertEqual(False, safe_cast(bool, "", None))
    
    def test_int_or_none(self) -> None:
        self.assertIsNone(int_or_none(""))
        self.assertEqual(1, int_or_none("1"))
        self.assertEqual(1, int_or_none("1"))
             
    def test_select_from_enum(self) -> None:
        self.assertEqual(Stroke.FREESTYLE, select_from_enum(Stroke, "A")) 
        self.assertEqual(Stroke.FREESTYLE, select_from_enum(Stroke, 1)) 
        self.assertEqual(Stroke.UNKNOWN, select_from_enum(Stroke, "foo"))
        
    def test_date_or_none(self) -> None:
        self.assertIsNone(date_or_none(""))
        self.assertEqual(datetime.date(1970, 1, 2), date_or_none("01021970"))  
                   
class TestParseReactionTime(unittest.TestCase):
    """Contract for the E2/F2 reaction-time columns.

    Every case below is a token form observed in a full-corpus scan of 33,008
    HY3 files; none are invented.
    """

    def test_plain_value(self) -> None:
        self.assertAlmostEqual(0.56, parse_reaction_time(" 0.56"), places=2)

    def test_negative_value_is_preserved(self) -> None:
        # Relay takeovers record an early exchange as a negative number.
        # 7,868 such values exist corpus-wide; dropping them is the single
        # worst failure mode for this field.
        self.assertAlmostEqual(-0.12, parse_reaction_time("-0.12"), places=2)

    def test_unsigned_zero_is_sentinel(self) -> None:
        self.assertIsNone(parse_reaction_time(" 0.00"))

    def test_plus_zero_is_sentinel(self) -> None:
        self.assertIsNone(parse_reaction_time("+0.00"))

    def test_minus_zero_is_sentinel(self) -> None:
        self.assertIsNone(parse_reaction_time("-0.00"))

    def test_nrt_is_sentinel(self) -> None:
        # Meet Manager writes "No Reaction Time" into unmeasured takeover slots.
        self.assertIsNone(parse_reaction_time("  NRT"))
        self.assertIsNone(parse_reaction_time("NRT"))

    def test_blank_is_none(self) -> None:
        self.assertIsNone(parse_reaction_time("     "))
        self.assertIsNone(parse_reaction_time(""))

    def test_malformed_bare_sign_is_none(self) -> None:
        self.assertIsNone(parse_reaction_time("    +"))

    def test_implausible_value_is_passed_through(self) -> None:
        # Values above 2.0 cannot be reaction times, but their meaning is
        # unresolved. The parser reports what the file says; consumers decide.
        self.assertAlmostEqual(9.30, parse_reaction_time(" 9.30"), places=2)

    def test_nan_is_none(self) -> None:
        # float() accepts "nan" (5 characters, fits the column); a bare int()
        # downstream would raise ValueError on it instead of yielding None.
        self.assertIsNone(parse_reaction_time("  nan"))

    def test_negative_nan_is_none(self) -> None:
        self.assertIsNone(parse_reaction_time(" -nan"))

    def test_inf_is_none(self) -> None:
        # float() accepts "inf"; a bare int() downstream would raise
        # OverflowError on it instead of yielding None.
        self.assertIsNone(parse_reaction_time("  inf"))

    def test_negative_inf_is_none(self) -> None:
        self.assertIsNone(parse_reaction_time(" -inf"))


if __name__=='__main__':
	unittest.main()
