
"""
Test for the utils module
"""
import unittest
from download.connector import Connector
import datetime
from download.utils import convert_date_string

class TestUitls(unittest.TestCase):
    
    def test_convert_date_sting_datatype(self):
        """Test output is of type datetime object"""

        _string = '2021-12-01'
        self.assertIsInstance(convert_date_string(_string), datetime.datetime )

    def test_convert_date_sting_exeption(self):
        """Test exception on malform input"""

        with self.assertRaises(Exception):
            convert_date_string('YEAR-12-01')
       
if __name__ == '__main__':
    unittest.main()

