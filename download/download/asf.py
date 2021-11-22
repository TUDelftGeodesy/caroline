"""
Implementation of SearchAPI for the Alaska Satellite Facility
This class provides a common interface with search an download functionalities.
API documentation: https://docs.asf.alaska.edu/api/basics/
"""

import datetime
import os
import hashlib

from . import search
from . import data_product

# for DAG
# import search
# import data_product


class ASF(search.DataSearch):
    """
    Implementattion of DataSearch for the ASF API
    """

    # base url: https://api.daac.asf.alaska.edu/

    def __init__(self, connector) -> None:
        """
        Initialise the ASF object

        Args:
            connector (obj): connector object
        """

        self.connector = connector # requires a Connector as component
        

    # private method
    def build_query(self, aoi, start_date, end_date=None, track=None, polarisation=None, orbit_direction=None, 
    sensor_mode='IW', product='SLC', instrument_name='Sentinel-1') -> None:
        """
        Builds a query for the API using given the search creteria
        
        Args:
            aoi (str): a polygon geometry formatted as well-known-text (A.K.A.: area of interest)
            start_date (str): first day for search (YYYY-MM-DD)
            end_date (str): last day for search as (YYYY-MM-DD), If None, the start_date will be also used as end_date
            and the query will use a time-window of one day.
            track (int): the number of the for the searching creteria
            polarisation (str): type of polarisation. A single value or a comma-separated list of values E.g., VV or VV,HH
            orbit_direction (srt): Direction of the orbit. E.g., Ascending, Descending 
            sensor_mode (str): beam mode as in the ASF documentation. E.g., IW
            product (str): processing level as in the ASF documentation. E.g., SLC
            instrument (str): name of the platform as in the ASF documentation. E.g., Sentinel-1

        Returns: query string with JSON output type 

        """

        search_url = self.connector.root_url + 'services/search/param?'

        try:
            start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            print('Make sure that start_date is formatted as YEAR-MONTH-DAY')
        if end_date is None: # for the case only a start date is given
            end = start_date
        else:
            try: end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                print('Make sure that end_date is formatted as YEAR-MONTH-DAY')
        
        # arguments left as None will be hadled as empty strings
        if track is None:
            track=''
        if polarisation is None:
            track=''
        if orbit_direction is None:
            orbit_direction=''
        
        query = ''
        if instrument_name:
            # using a leading '&' means parameters can be omitted at will 
            query += '&platform=' + instrument_name
        if sensor_mode:
            query += '&beamMode=' + sensor_mode
        if product:
            query += '&processingLevel=' + product
        if orbit_direction:
            query += '&flightDirection=' + orbit_direction
        if track:
            query += '&relativeOrbit=' + str(track)
        if polarisation:
            query += '&polarization=' + polarisation
        if aoi:
            query += '&intersectsWith=' + aoi 
        
        date_string = '&start=' + start.strftime('%Y-%m-%dT%H:%M:%S') + 'UTC' + \
                      '&end=' + end.strftime('%Y-%m-%dT%H:%M:%S') + 'UTC'

        query += date_string + '&output=JSON'
        query = query[1:] # remove leading '&' from query string 

        return search_url + query
            
    def search(self, aoi, start_date, end_date=None, track=None, polarisation=None, orbit_direction=None, 
    sensor_mode='IW', product='SLC', instrument_name='Sentinel-1') -> None:
        """
        Searches the ASF API for datasets based on input creteria.
        
        Args:
            aoi (str): a polygon geometry formatted as well-known-text (A.K.A.: area of interest)
            start_date (str): first day for search (YYYY-MM-DD)
            end_date (str): last day for search as (YYYY-MM-DD), If None, the start_date will be also used as end_date
            and the query will use a time-window of one day.
            track (int): the number of the for the searching creteria
            polarisation (str): type of polarisation. A single value or a comma-separated list of values E.g., VV or VV,HH
            orbit_direction (srt): Direction of the orbit. E.g., Ascending, Descending 
            sensor_mode (str): beam mode as in the ASF documentation. E.g., IW
            product (str): processing level as in the ASF documentation. E.g., SLC
            instrument (str): name of the platform as in the ASF documentation. E.g., Sentinel-1

        Returns: a list of products.

        """

        self.products =[]

        print("Searching for products....")
        query = self.build_query(aoi, start_date, end_date, track, polarisation, orbit_direction, sensor_mode, product, instrument_name)

        search_results = self.connector.get(query)
        result_json = search_results.json() # returns array of objects
        _objects = result_json[0]

        print("Found ", str(len(_objects)), " products.")

        if len(_objects) != 0:
            for _object in _objects:
                product = data_product.Product(_object['productName'], 
                                                _object['sceneId'], 
                                                _object['downloadUrl'], 
                                                _object['track'],
                                                _object['beamMode'],
                                                _object['processingLevel'],
                                                _object['flightDirection'],
                                                _object['polarization'],
                                                _object['startTime'],
                                                _object['md5sum'],
                                                size_MB=_object['sizeMB']
                )
                                                
                self.products.append(product)
        else:
            print("No products found for this creteria")
        
        return self.products


    def download(self, products, max_retries=3):
        """
        Downloads dataset given for a list of products.

        Args:
            products (obj): list of products as defined by the Product dataclass.
            directory: path to directory to store files.
            max_reties (int): maximum number of connection retries to download a product.

        """

        print("Downloading Products....")

        for product in products:
            product.prepare_directory() 

            file_path = product.download_directory + product.file_name + '.zip'

            # Avoid re-download valid products after sudden failure
            if os.path.isfile(file_path):
                check_existing_file = self.validate_download(product, file_path)
                if check_existing_file:
                    print(f'-->> Product was already dowloaded: {product.file_name}')
                    continue
                else:
                    print("Found local copy of", product.filename, "\n But checksum validation failed! Restarting donwload...")
            
            validity = False
            download_retries = 1 # counter

            while validity == False:
                if download_retries > max_retries:
                    print("Download failed after", str(max_retries), "tries. Product: ", product.title)
                    break
                else:
                    response = self.connector.get(product.uri, stream=True)
                    with open(file_path, 'wb' ) as f:
                        # f.write(b'file content')
                        for chunk in response.iter_content(chunk_size=100*1024): # bytes
                            f.write(chunk)
                
                    print('>>>> Trying', str(download_retries) )
                    download_retries += 1
                    validity = self.validate_download(product, file_path)
                
        return None


    def validate_download(self, product, file_path):
        """
        Validates the success of a dowload by performing a data integrity check using checksums.

        Args:
            product (obj): instance of Product dataclass.
            file_path (str): path to local copy of the product.
        
        Return: 
            validity chek (bolean)

        """

        # extract checksum on remote (MD5)
        remote_checksum = product.checksum

        # Local checksum
        with open (file_path, 'rb') as local_file:
            file_hash = hashlib.md5()
            while True:
                chunk = local_file.read(100*128)
                if not chunk:
                    break
                file_hash.update(chunk)
            
            # while chunk := local_file.read(100*128): # chunk size must be multiple of 128 bytes
                # file_hash.update(chunk)
        
        local_checksum = file_hash.hexdigest()

        if remote_checksum == local_checksum:
            result = True
        else:
            result = False

        return result 
