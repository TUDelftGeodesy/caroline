"""Test for the interferogram.py CLI inteface"""

import unittest
import os
import processing.interferogram

PATH = '../processing/interferogram.py'
SHAPEFILE = "test-data/test.shp"
KML_FILE = "test-data/test.kml"
WKT = "POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))"
POL = ['VV']

class TestArgumentAoi(unittest.TestCase):
    """ Test the validity of inputs for the argument Area of Interest (aoi)"""

    def test_input_shapefile(self):
        """Test that aoi accepts a shapefile as input"""

        stream = os.popen('echo my command')
        output = stream.read()
        #TODO: complete test


class TestArgumentPolarization(unittest.TestCase):
    """Test the values for this argument are valid. A list of strings"""

    def test_is_list(self):
        """ test values are a list"""
        
        pass

    def test_is_string():
        """Test values in the last are strings"""

        pass



if __name__ == '___main___':
    unittest.main()
