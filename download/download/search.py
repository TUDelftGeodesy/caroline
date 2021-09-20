"""
Classes for implementing search funcitionalidy of particular data sources
"""

# from _typeshed import Self
from abc import ABC, abstractmethod
from shapely.geometry import Polygon
import datetime
import os
import hashlib
from . import data_product

class DataSearch(ABC):
    """
    Abstract class for specifying DataApi's (data sources)
    """

    @abstractmethod
    def build_query(self, *argv):
        pass
    
    @abstractmethod
    def search(self, *argv):
        pass

    @abstractmethod
    def download(self, *argv):
        pass

    @abstractmethod
    def validate_download(self, *argv):
        pass


class SciHub(DataSearch):
    """
    Implementation of DataSearch for the SciHub.
    SciHub provides two API's, one with search functionality and another with downloading functionality.
    This class provides a common interface with search an download functionalities.
    """
    
    def __init__(self, connector) -> None:
        """
        Initialise the SciHubAPI object

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
            polarisation (str): type of polarsation as on SciHub documentation. E.g., HH
            orbit_direction (srt): Direction of the orbit. E.g., Ascending, Descending 
            sensor_mode (str): acquisition mode as in the SciHub documentation. E.g., IW
            product (str): SciHub product level as in the SciHub documentation. E.g., SLC
            instrument (str): name of the platform as in the SciHub documentation. E.g., Sentinel-1

        Returns: query string for the first 100 results

        """

        search_url = self.connector.root_url + 'search?q=' # extending the root url to define the SearchAPI endpoint

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

        # arguments left as None will be hadle as empty strings
        if track is None:
            track=''
        if polarisation is None:
            track=''
        if orbit_direction is None:
            orbit_direction=''

        query = ''
        if instrument_name:
            query += 'platformname:' + instrument_name
        if sensor_mode:
            query += ' AND ' + 'sensoroperationalmode:' + sensor_mode
        if product:
            query += ' AND ' + 'producttype:' + product
        if orbit_direction:
            query += ' AND ' + 'orbitdirection:' + orbit_direction
        if track:
            query += ' AND ' + 'relativeorbitnumber:' + str(track)
        if polarisation:
            query += ' AND ' + 'polarisationmode:' + polarisation
        if aoi:
            query += ' AND footprint:"Intersects(' + aoi + ')"'

        date_string = 'beginposition:[' + start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z TO ' + \
                      end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z] AND endposition:[' + \
                      start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z TO ' + end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z]'
        query += ' AND ' + date_string

        return search_url + query + '&format=json&rows=100'
        

    def search(self, aoi, start_date, end_date=None, track=None, polarisation=None, orbit_direction=None, 
        sensor_mode='IW', product='SLC', instrument_name='Sentinel-1'):
        """
        Searches the SciHub API for datasets based on input creteria.

        Args:
            aoi (str): a polygon geometry formatted as well-known-text (A.K.A.: area of interest)
            start_date (str): first day for search (YYYY-MM-DD)
            end_date (str): last day for search as (YYYY-MM-DD), If None, the start_date will be also used as end_date
            and the query will use a time-window of one day.
            track (int): the number of the for the searching creteria
            polarisation (str): type of polarsation as on SciHub documentation. E.g., HH
            orbit_direction (srt): Direction of the orbit. E.g., Ascending, Descending 
            sensor_mode (str): acquisition mode as in the SciHub documentation. E.g., IW
            product (str): SciHub product level as in the SciHub documentation. E.g., SLC
            instrument (str): name of the platform as in the SciHub documentation. E.g., Sentinel-1

        Returns: a list of products. 
        """

        self.products = [] # collection of products

        print("Searching for products....")
        query = self.build_query(aoi, start_date, end_date, track, polarisation, orbit_direction, sensor_mode, product, instrument_name)

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
        
        #TODO: requirement time shall be propvided in different formats such as a single specific time, a list of specific times, an interval, or  list of intervals
        # though for the system only two formats might be necessary. A single time (considering the temporal resolution of the sensor), and an interval with a start and end


    def download(self, products, download_directory, max_retries=3):
        """
        Downloads data set given for the list of products.

        Args:
            products (dic): list of products to download.
            directory: path to directory to store files.
            max_reties (int): maximum number of connection retries to download a product.

        """

        if os.path.exists(download_directory) == False:
            os.mkdir(download_directory)
        
        print("Downloading Products....")

        for product in products:
            file_path = download_directory + product.title + '.zip'

            # Avoid re-download valid products after sudden failure
            if os.path.isfile(file_path) and self.validate_download(product, file_path):
                continue
            else:
                print("Found local copy of", product.title, "\n But checksum validation failed! Restarting donwload...")

            validity = False
            download_retries = 1 # we required several re-tries to get the download started from SciHub. Tests point out that this is an issue with their API

            while validity == False:
                if download_retries > max_retries:
                    print("Download failed after", str(max_retries), "tries. Product: ", product.title)
                    break
                else:
                    response = self.connector.get(product.uri, stream=True)
                    with open(file_path, 'wb' ) as f:
                        
                        for chunk in response.iter_content(chunk_size=100*1024): # bytes
                            f.write(chunk)
                
                    print('>>>> Trying', str(download_retries) )
                    download_retries += 1
                    validity = self.validate_download(product, file_path)
                
        return None

    # private method
    def validate_download(self, product, file_path):
        """
        Validates the success of a dowload by performing a data integrity check using checksums.

        Args:
            product (dic): product description including a URI for data download
            file_path (str): path to local copy of the product.
        
        Return: 
            validity chek (bolean)

        """

        #checksum on remote (MD5)
        dowload_uri = product.uri
        checksum_uri = dowload_uri.split('$')[0] + 'Checksum/Value/$value' 
        remote_checksum = self.connector.get(checksum_uri).text

        # Local checksum
        with open (file_path, 'rb') as local_file:
            file_hash = hashlib.md5()
            while chunk := local_file.read(100*128): # chunk size must be multiple of 128 bytes
                file_hash.update(chunk)
        
        local_checksum = file_hash.hexdigest()

        if remote_checksum == local_checksum:
            result = True
        else:
            result = False

        return result 


class ASF(DataSearch):
    """
    Implementation of SearchAPI for the Alaska Satellite Facility
    This class provides a common interface with search an download functionalities.
    API documentation: https://docs.asf.alaska.edu/api/basics/
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
                product = data_product.Product(_object['productName'], _object['sceneId'], _object['downloadUrl'], checksum=_object['md5sum'])
                self.products.append(product)
        else:
            print("No products found for this creteria")
        
        return self.products


    def download(self, products, download_directory, max_retries=3):
        """
        Downloads dataset given for a list of products.

        Args:
            products (obj): list of products as defined by the Product dataclass.
            directory: path to directory to store files.
            max_reties (int): maximum number of connection retries to download a product.

        """

        if os.path.exists(download_directory) == False:
            os.mkdir(download_directory)
        
        print("Downloading Products....")

        for product in products:
            file_path = download_directory + product.title + '.zip'

            # Avoid re-download valid products after sudden failure
            if os.path.isfile(file_path) and self.validate_download(product, file_path):
                continue
            else:
                print("Found local copy of", product.title, "\n But checksum validation failed! Restarting donwload...")
            
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
            while chunk := local_file.read(100*128): # chunk size must be multiple of 128 bytes
                file_hash.update(chunk)
        
        local_checksum = file_hash.hexdigest()

        if remote_checksum == local_checksum:
            result = True
        else:
            result = False

        return result 


class EarthData(DataSearch):
    """
    Implementation of DataAPI for the EarthData.
    This class provides a common interface with search an download functionalities.
    """

    def build_query(self, *argv):
        pass
        

    
    def search(self, *argv):
        pass


    def download(self, *argv):
        pass

    def validate_download(self, *argv):
        pass
    




