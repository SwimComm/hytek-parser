import unittest
from hytek_parser._utils import safe_cast, int_or_none

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
            
if __name__=='__main__':
	unittest.main()
         