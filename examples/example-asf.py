"""
This an example of how the current version of download engine
is intended to be used. For now only an example on API connection,
search and download.
This example is for the ASF API
Must provide your own account credentials
"""



from download import connector
from download.asf import ASF

def products_to_dict(product_list):
    dictonary={}
    count=1
    for product in product_list:
        dictonary[str(count)] = product.__dict__
        count+=1

    return dictonary


# for DAG
# from download import connector
# from download.asf import ASF

# WARNING: This example will download 4 datasets (>16GB)

# Create a connector to handle the autentification

c = connector.Connector("manuurs", "mEEhKTgSRhb3EHC#77yi", 'https://api.daac.asf.alaska.edu/', retain_auth=True)

c.test_connection()

# instantiate API with the connector
search_api = ASF(c)

# search the API 

search_results=search_api.search('POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))',
        '2018-04-22', '2018-05-08', orbit_direction='Ascending',
        sensor_mode='IW', product='SLC', instrument_name='Sentinel-1')

results = products_to_dict(search_results)
print(results)
print(type(results))

print(results.values())


# Download datasets (a.k.a products found by search())
# search_api.download(search_results, './data/') # This might take a long time
