"""Test for the interferogram.py CLI inteface"""

import unittest
import os

PATH = '../processing/interferogram.py'
SHAPEFILE = "test-data/test.shp"
KML_FILE = "test-data/test.kml"
WKT = "POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))"

class TestArgumentAoi(unittest.TestCase):
    """ Test the validity of inputs for the argument Area of Interest (aoi)"""

    def test_input_shapefile(self):
        """Test that aoi accepts a shapefile as input"""

        stream = os.popen('echo my command')
        output = stream.read()
        #TODO: complete test

if __name__ == '___main___':
    unittest.main()
