"""
Implementation of SearchAPI for the GNNS Scihub API
This class provides a common interface with search an download functionalities.
API documentation: https://docs.asf.alaska.edu/api/basics/
"""

import datetime
import os
import hashlib
from .utils import compute_checksum
from . import search
from . import data_product


class GNNS(search.DataSearch):
    """
    Implementattion of DataSearch for the ASF API
    """

    def __init__(self, connector) -> None:
        """
        Initialise the ASF object

        Args:
            connector (obj): connector object
        """
        self.connector = connector

    def build_query(self,start_date, end_date=None, osvtype='RES'):
        """
        Builds a query for the API using given the search creteria.

        Args:
            start_date (str): first day for search (YYYY-MM-DD)
            end_date (str): last day for search as (YYYY-MM-DD), If None, the start_date will be also used as end_date
            and the query will use a time-window of one day.
            osvtype (str): the type of orbit files; either 'POE'=Precise or 'RES'=restituted
        
        Returns:
            query string for the first 100 results
        """
        # example valid request:
        # https://scihub.copernicus.eu/gnss/search/?q=producttype:AUX_POEORB platformname:
        # Sentinel-1 beginPosition:[2021-12-13T17:51:48Z TO 2021-12-13T17:51:48Z] 
        # endPosition:[2021-12-13T17:51:48Z TO 2021-12-13T17:51:48Z]&format=json

        # root_url = https://scihub.copernicus.eu/gnss/search/
        
        search_url = self.connector.root_url + 'search?q='


    def download(self, *argv):
        return super().download(*argv)

    def validate_download(self, *argv):
        return super().validate_download(*argv)



