"""
Implementation of SearchAPI for the GNNS Scihub API
This class provides a common interface with search an download functionalities.
API documentation: https://docs.asf.alaska.edu/api/basics/
"""

import datetime
import os
import hashlib
from platform import platform
from download.utils import compute_checksum, convert_date_string
from download import search
from download import data_product


class S1OrbitProvider(search.DataSearch):
    """
    Implementattion of DataSearch for the 
    """

    def __init__(self, connector) -> None:
        """
        Initialise the ASF object

        Args:
            connector (obj): connector object
        """
        self.connector = connector


    def build_query(self, start_date, end_date=None, osvtype='RES'):
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
        
       
        # validate osvtype value
        if osvtype == 'POE':
            product_type= 'AUX_POEORB'
        elif osvtype == 'RES':
                product_type = 'AUX_RESORB'
        else:
            raise ValueError("osvtype must be 'POE' or 'RES' ")
        
        # Define search dates
        start = convert_date_string(start_date)
        print(start)
        if end_date is None: 
            end = start
        else:
            end = convert_date_string(end_date)
        date_string = 'beginposition:[' + start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z TO ' + \
                      end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z] AND endposition:[' + \
                      start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z TO ' + end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z]'
    

        search_url = self.connector.root_url + 'search/?q='
        # search_url = 'https://scihub.copernicus.eu/gnss/search/' + '?q='

       
        platform = 'Sentinel-1'

        query = 'producttype:'+ product_type + ' platformname:'+ platform + ' ' + date_string + '&format=json&rows=100'

        return search_url + query


    def search(self, start_date, end_date=None, osvtype='RES'):
        """
        Searches the SciHub GNSS API for datasets based on input creteria.

        Args:
            start_date (str): first day for search (YYYY-MM-DD)
            end_date (str): last day for search as (YYYY-MM-DD), If None, the start_date will be also used as end_date
            and the query will use a time-window of one day.
            osvtype (str): the type of orbit files; either 'POE'=Precise or 'RES'=restituted

        Returns: a list of products (orbits for Sentinel 1). 
        """

        self.products = [] # collection of products

        print("Searching for products....")
        query = self.build_query(start_date, end_date=end_date, osvtype=osvtype)

        search_results = self.connector.get(query)
        result_json = search_results.json()
        entries= result_json['feed']['entry'] # entries describe product/dataset  

        print("Found ", result_json['feed']["opensearch:totalResults"], " products.")
        if len(entries) !=0:
            for entry in entries:
                product = data_product.Product(entry['title'], entry['id'], entry['link'][0]['href'])
                self.products.append(product)

        else:
            print("No products found for this creteria")

        return self.products

    def download(self, *argv):
        return super().download(*argv)

    def validate_download(self, *argv):
        return super().validate_download(*argv)


if __name__ == '__main__':

    from download import connector

    # "manuelgarciaalvarez", "bYYpjJCc!K!jxxc5Hx5b"

    c =connector.Connector("gnssguest", "gnssguest", 'https://scihub.copernicus.eu/gnss/')
    c.test_connection()
    print(c.status)

    start = '2021-12-13'
    end = '2021-12-14'

    g = S1OrbitProvider(c)
    
    print(g.build_query(start))
    g.search(start, end_date=end)
    
# 
    

    #search date only update on daily basis 

