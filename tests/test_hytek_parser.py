import unittest
from hytek_parser import __version__

class TestHytekParser(unittest.TestCase):
    
    def test_version(self) -> None:
        self.assertTrue( __version__ == '1.1.1')

if __name__=='__main__':
	unittest.main()
 