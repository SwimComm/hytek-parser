import unittest
from hytek_parser._utils import safe_cast, int_or_none, select_from_enum
from hytek_parser.hy3.schemas import Stroke

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
        self.assertEqual(None, int_or_none(""))
        self.assertEqual(1, int_or_none("1"))
        self.assertEqual(1, int_or_none("1"))
             
    def test_select_from_enum(self) -> None:
        self.assertEqual(Stroke.FREESTYLE, select_from_enum(Stroke, "A")) 
        self.assertEqual(Stroke.FREESTYLE, select_from_enum(Stroke, 1)) 
        self.assertEqual(Stroke.UNKNOWN, select_from_enum(Stroke, "foo"))
                   
if __name__=='__main__':
	unittest.main()
         