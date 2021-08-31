"""
This an example of how the current version of download engine
is intende to be used. For now only an example on API connection,
search and download.
This example if for the SciHub API
"""

from download import connector
from download import search


# Create a connector to handle the autentification
c = connector.Connector('manuelgarciaalvarez', 'bYYpjJCc!K!jxxc5Hx5b', 'https://scihub.copernicus.eu/dhus/')

c.test_connection()

# instantiate API with the connector
search_api = search.SciHub(c)

# search the API 
search_results=search_api.search('POLYGON((-155.75 18.90, -155.75 20.2, -154.75 19.50, -155.75 18.90))',
        '2021-08-14', '2021-08-16',  polarisation='VV', orbit_direction='Ascending', 
        sensor_mode='IW', product='SLC', instrument_name='Sentinel-1')

c.close_connection() # only need for this example and user. Otherwhise connection is reused

print(search_results)

# Download datasets (a.k.a products found by search())
search_api.download(search_results, './data/') # This might take a long time
