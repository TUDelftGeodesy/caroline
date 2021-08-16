"""
Abstract class for implementing searc funcitionalidy of particular data sources
"""

from abc import ABC, abstractmethod
# from download.download.connector import Connector
from shapely.geometry import Polygon
import datetime

# TODO: Implement search and dowload as abstract classes.

class DataApi(ABC):
    '''
    Abstract class for specifying DataApi's (data sources)
    '''

    @abstractmethod
    def build_query(self, *argv):
        pass
    
    @abstractmethod
    def search(self, *argv):
        pass

    @abstractmethod
    def download(selt, *argv):
        pass


class SciHub(DataApi):
    '''
    Implementation of DataAPI for the SciHub.
    SciHub provides two API's, one with search functionality and another with downloading functionality.
    This class provides a common interface with search an download functionalities.
    '''
    
    def __init__(self, connector=None ) -> None:
        '''
        Initialise the SciHubAPI object

        Args:
            connector (obj): connector object

        '''

        self.connector = connector # requires a Connector as component

    # private method
    def build_query(self, aoi, start_date, end_date=None, track=None, polarisation=None, orbit_direction=None, 
    sensor_mode='IW', product='SLC', instrument_name='Sentinel-1'):
        '''
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

        '''

        # self.connector.root_url     
        search_url = 'https://scihub.copernicus.eu/dhus/' + 'search?q=' # extending the root url to define the SearchAPI endpoint

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
                      start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z TO ' + end.strftime('%Y-%m-%dT%H:%M:%S.%f')[
                                                                              :-3] + 'Z]'
        query += ' AND ' + date_string

        return search_url + query
        

    def search(self, aoi, start_date, end_date, track, polarisarion, orbit_direction):

        self.build_query(aoi, start_date, end_date, track, polarisarion, orbit_direction)

        # 1. build query
        # 2. send request to API
        # 3 collect results (dataset endpoints)
        
        #TODO: requirement time shall be propvided in different formats sucha as a single specific time, a list of specific times, an interval, or  list of intervals
        # though for the system only two formats might be necessary. A single time (considering the temporal resolution of the sensor), and an interval with a start and end

        #call build_query here
        return

    def download(selt, *argv):
        pass

class EarthData(DataApi):
    pass
    # estend for other APIs



    
api=SciHub()

q=api.build_query('POLYGON((-4.53 29.85, 26.75 29.85, 26.75 46.80,-4.53 46.80,-4.53 29.85))',
        '2021-08-14', '2021-08-16', track=81, polarisation='VV', orbit_direction='Ascending', 
        sensor_mode='IW', product='SLC', instrument_name='Sentinel-1')
print(q)

