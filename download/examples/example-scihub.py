"""
This an example of how the current version of download engine
is intended to be used. For now, only an example on API connection,
search and download.
This example is for the SciHub API
"""

from download import connector
from download.scihub import SciHub

# WARNING: This example will attempt to download 2 datasets (>8GB)

# Create a connector to handle the autentification
# Need to set user credentials
c = connector.Connector("USERNAME", "PASSWORD", 'https://scihub.copernicus.eu/dhus/')

c.test_connection()

# instantiate API with the connector
search_api = SciHub(c)

# search the API 
search_results=search_api.search('POLYGON((-155.75 18.90, -155.75 20.2, -154.75 19.50, -155.75 18.90))',
        '2021-08-14', '2021-08-16',  polarisation='VV', orbit_direction='Ascending', 
        sensor_mode='IW', product='SLC', instrument_name='Sentinel-1')

# Download datasets (a.k.a products found by search())
search_api.download(search_results) # This might take a long time
