#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
# Created By  : Manuel G. Garcia
# Created Date: 06-12-2021

"""
Implementation of SearchAPI for the GNNS Scihub API
This class provides a common interface with search an download functionalities.
API documentation: https://docs.asf.alaska.edu/api/basics/
"""

import datetime
from logging import warning
import os
import warnings
import hashlib
from platform import platform

from download.utils import compute_checksum, convert_date_string
from download import search
from download import data_orbit
from download.utils import validate_scihub_download
from download.exceptions import DataUnavailableError


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


    def build_query(self, start_date, end_date=None, osvtype='RES', start_index=0):
        """
        Builds a query for the API using given the search creteria.

        Args:
            start_date (str): first day for search (YYYY-MM-DD)
            end_date (str): last day for search as (YYYY-MM-DD), If None, the end_date will be set to the next day, 
            and the query will use a time-window of one day.
            osvtype (str): the type of orbit files; either 'POE'=Precise or 'RES'=restituted
            start_index (int): starting index for the page results. Useful for dealing with pagination. 
        
        Returns:
            query string for the first 100 results.
        """
        # example valid request:
        # https://scihub.copernicus.eu/gnss/search/?q=producttype:AUX_POEORB platformname:
        # Sentinel-1 beginPosition:[2021-12-13T17:51:48Z TO 2021-12-13T17:51:48Z] 
        # endPosition:[2021-12-13T17:51:48Z TO 2021-12-13T17:51:48Z]&format=json
        
        platform = 'Sentinel-1'
       
        # validate osvtype value
        if osvtype == 'POE': 
            product_type= 'AUX_POEORB'
        elif osvtype == 'RES':
                product_type = 'AUX_RESORB'
        else:
            raise ValueError("osvtype must be 'POE' or 'RES' ")
        
        # Define search dates
        start = convert_date_string(start_date)
        if end_date is None:  # When no end_date is provided, add 1 day to start date
            end = start + datetime.timedelta(days=1)
        else:
            end = convert_date_string(end_date)
        date_string = 'beginposition:[' + start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z TO ' + \
                      end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z] AND endposition:[' + \
                      start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z TO ' + end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z]'
    
        search_url = self.connector.root_url + 'search/?q='
        query = 'producttype:'+ product_type + ' platformname:'+ platform + ' ' + date_string + f'&start={start_index}&format=json&rows=100'

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

        self.orbits = [] # collection of orbits

        print("Searching for products....")
        query = self.build_query(start_date, end_date=end_date, osvtype=osvtype)

        search_results = self.connector.get(query)
        result_json = search_results.json()
    
        total_results = int(result_json['feed']["opensearch:totalResults"])
        print("Found", total_results , "products.")
       
        if total_results == 0:
            warnings.warn("No products (orbit files) found for these creteria")
            raise DataUnavailableError("Search find zero orbits that match the search creteria.")
        elif total_results == 1:
            entries = [entries] # convert to list
        else: 
            entries = result_json['feed']['entry'] # entries describe product/dataset
            while len(entries) < total_results: # page over results when more than 100 products are found
                page_query = self.build_query(start_date, end_date, osvtype=osvtype, start_index=len(entries))
                page_results = self.connector.get(page_query)
                page_json = page_results.json()
                page_entries = page_json['feed']['entry'] 
                entries = entries + page_entries

        for entry in entries:
            product = data_orbit.Orbit (entry['title'], entry['id'], entry['link'][0]['href'], entry['str'][7]['content'])
            self.orbits.append(product)
            
        return self.orbits

    def download(self, orbits, max_retries=3):
        """
        Downloads data set given a list of orbit files.

        Args:
            orbits (lists): list of products to download.
            max_reties (int): maximum number of connection retries to download a product.

        """
        
        print("Downloading Products....")

        for orbit in orbits:
            orbit.prepare_directory()
            file_path = orbit.download_directory + orbit.file_name + '.EOF'
            
            # Avoid re-download valid products after sudden failure
            if os.path.isfile(file_path):
                print(f'-> Found orbit file in data directory: {orbit.file_name}')
                print('-->> Checking file integrity.....')
                check_existing_file = self.validate_download(orbit, file_path)
                if check_existing_file:
                    print('-->> Orbit file is already downloaded')
                    continue
                else:
                    print("Found a copy of", orbit.file_name, "\n But integrity check failed!")
                    print("-> Downloading a new copy...")

            validity = False
            download_retries = 1 # we required several re-tries to get the download started from SciHub. 
            # Tests suggest that this is an issue with the API

            while validity == False:
                if download_retries > max_retries:
                    print("Download failed after", str(max_retries), "tries. File: ", orbit.file_name)
                    raise RuntimeError("Download attemps reached the maximum of retries. Check the API for orbits is up and running, and internet connection is stable.")
                else:
                    response = self.connector.get(orbit.uri, stream=True)
                    with open(file_path, 'wb' ) as f:
                        
                        for chunk in response.iter_content(chunk_size=100*1024): # bytes
                            f.write(chunk)

                    if download_retries > 1:
                        print('>>>> Trying', str(download_retries) )
                    download_retries += 1
                    validity = self.validate_download(orbit, file_path)

        print('Download complete')
        return None


    # TODO: remove this method from abstract class. Move code to utils.py
    def validate_download(self, orbit, file_path):
        """
        Validates the success of a dowload by performing a data integrity check using checksums.

        Args:
            product (dic): product description including a URI for data download
            file_path (str): path to local copy of the product.
        
        Return: 
            validity chek (bolean)

        """
       
        return validate_scihub_download(self.connector, orbit, file_path)


if __name__ == '__main__':

    from download import connector

    c =connector.Connector("gnssguest", "gnssguest", 'https://scihub.copernicus.eu/gnss/')
    c.test_connection()

    start = '2022-04-01'
    end = '2022-04-10'

    g = S1OrbitProvider(c)
    
    print(g.build_query(start, end))
    results = g.search(start)# page over results when more than 100 products are found
    # print(results)
    # g.download(results)
