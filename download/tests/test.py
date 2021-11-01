"""
Write your test here
"""
import unittest
from download.connector import Connector

USENAME = 'my-username'
PSWD = 'mysecret-password'
ROOT_URL = 'https://my-dummy.url'

class TestPackageImport(unittest.TestCase):

    def test_package_import(self) -> None:
        self.connector_ = None 
        return None


if __name__ == '__main__':
    unittest.main()

