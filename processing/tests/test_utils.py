"""Tests for utils.py"""
import unittest
from processing.utils import wkt_to_list


class TestWKT_To_List(unittest.TestCase):
    """ Test the validity of inputs for the argument Area of Interest (aoi)"""

    def setUp(self) -> None:
        """set up test fixtures"""
        self.polygon_wkt = "POLYGON((7.218017578125001 53.27178347923819,7.00927734375 53.45534913802113,6.83349609375 52.5897007687178,7.0751953125 52.6030475337285,7.218017578125001 53.27178347923819))"
        self.output = wkt_to_list(self.polygon_wkt)

    def test_output_list(self):
        """Test that function returnes a list of lists"""
        self.assertIsInstance(self.output, list) and self.assertIsInstance(self.output[0], list)

    
    def test_output_length(self):
        """Test that number of output coordinate-pairs match number of input-coordinates"""
        
        output_length = len(self.output)
        self.assertEqual(output_length, 5)


if __name__ == '__main__':
    unittest.main()