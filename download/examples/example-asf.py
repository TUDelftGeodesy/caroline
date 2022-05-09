"""
This is an example of how to use the Download Enigne 
within Python.
This example uses the  ASF API. 
Account credentials and destination for dataset must
be provided via an .env file.
WARNING: This example will download 1 datasets (~4GB)
"""

import os
from download  import connector
from download.asf import ASF
from dotenv import load_dotenv
load_dotenv()

# Configurations should be provided in a .env file
USERNAME = os.getenv('ASF_USERNAME')
PASSWORD = os.getenv('ASF_PASSWORD')
ASF_BASE_URL = os.getenv('ASF_BASE_URL')

if __name__ == '__main__':
    # Create a connector to handle the autentification
    connection = connector.Connector(USERNAME, PASSWORD, ASF_BASE_URL, retain_auth=True)

    connection.test_connection()

    # instantiate API with the connector
    search_api = ASF(connection)

    # search the API 
    search_results=search_api.search('POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))',
            '2018-04-22', '2018-05-01', orbit_direction='Ascending',
            sensor_mode='IW', product='SLC', instrument_name='Sentinel-1', polarisation='HH,VV')

    # Download datasets (a.k.a products found by search())
    search_api.download(search_results) # This might take a long time
