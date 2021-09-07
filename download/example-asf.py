"""
This an example of how the current version of download engine
is intended to be used. For now only an example on API connection,
search and download.
This example is for the ASF API
Must provide your own account credentials
"""

from download import connector
from download import search


# Create a connector to handle the autentification
c = connector.Connector('manuurs', 'mEEhKTgSRhb3EHC#77yi', 'https://api.daac.asf.alaska.edu/')

c.test_connection()

# TODO: test query doesn't return any results, it should return 2

# instantiate API with the connector
search_api = search.ASF(c)

# search the API 


# TODO: polarization always return zero results for some reason.
search_results=search_api.build_query('POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))',
        '2018-04-22', '2018-05-08', orbit_direction='Ascending',
        sensor_mode='IW', product='SLC', instrument_name='Sentinel-1')


# c.close_connection() # only need for this example and user. Otherwhise connection is reused

# print(search_results)

# Download datasets (a.k.a products found by search())
# search_api.download(search_results, './data/') # This might take a long time
