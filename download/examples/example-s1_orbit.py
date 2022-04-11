"""
This an example of how the current version of download engine
is intended to be used. For now only an example on API connection,
search and download.
This example is for the download of orbit files form the SciHub API
Must provide your own account credentials
"""

from download.s1_orbit import S1OrbitProvider
from download  import connector



def products_to_dict(product_list):
    dictonary={}
    count=1
    for product in product_list:
        dictonary[str(count)] = product.__dict__
        count+=1

    return dictonary

# WARNING: This example will download many datasets

# Create a connector to handle the autentification
c = connector.Connector("gnssguest", "gnssguest", 'https://scihub.copernicus.eu/gnss/')

c.test_connection()

# instantiate API with the connector
search_api = S1OrbitProvider(c)

# search the API 
# the GNSS API doesn't provide orbit files for the entirity of the mission.
search_results=search_api.search('2021-12-21', '2021-12-22')

# print(search_results)
# Download datasets (a.k.a products found by search())
search_api.download(search_results) # This might take a long time
