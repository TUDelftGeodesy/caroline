"""
This example is for the download of orbit files form the SciHub API
Must provide your own account credentials
WARNING: This example will download many datasets
NOTICE: The location for donwloaded files must be set in the .env 
configuratin file
"""

from download.s1_orbit import S1OrbitProvider
from download  import connector

# Create a connector to handle the autentification
connection = connector.Connector("gnssguest", "gnssguest", 'https://scihub.copernicus.eu/gnss/')

connection.test_connection()

# instantiate API with the connector
search_api = S1OrbitProvider(connection)

# search the API 
# the GNSS API doesn't provide orbit files for the entirity of the mission.
search_results=search_api.search('2021-12-21', '2021-12-22')

# print(search_results)
# Download datasets (a.k.a products found by search())
search_api.download(search_results) # This might take a long time
