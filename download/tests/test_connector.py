"""
Test for the connector module
"""
import unittest
from download.connector import Connector


USERNAME = 'my-username'
PSWD = 'mysecret-password'
ROOT_URL = 'https://www.google.com/'

class TestPackageImport(unittest.TestCase):

    # test fixtures
    def setUp(self) -> None:
        self.connector_ = Connector(USERNAME, PSWD, ROOT_URL)

    def test_successful_connection(self) -> None:
        """Test that a HTTP connection can be stablished with a URL"""
        self._test=self.connector_.test_connection() 
        self.assertTrue(self._test)

    def test_get(self) -> None:
        """Test that the GET method produces an status code 200"""
        _response = self.connector_.get(ROOT_URL)
        self.assertEqual(_response.status_code, 200)


if __name__ == '__main__':
    unittest.main()

