"""
This is an example of how to use the Download Enigne 
within Python.
This example uses the  ASF API. 
Account credentials and destination for dataset must
be provided via an .env file.
WARNING: This example will download 1 datasets (~4GB)
"""
import os
from download import connector
from download.scihub import SciHub
from dotenv import load_dotenv
load_dotenv()

# Configurations should be provided in a .env file
# Need to set user credentials
USERNAME = os.getenv('SCIHUB_USERNAME')
PASSWORD = os.getenv('SCIHUB_PASSWORD')
BASE_URL = os.getenv('SCIHUB_BASE_URL')

# WARNING: This example will attempt to download 2 datasets (>8GB)
if __name__ == '__main__':
        # Create a connector to handle the autentification

        connection = connector.Connector(USERNAME, PASSWORD, BASE_URL)

        connection.test_connection()

        # instantiate API with a connector
        search_api = SciHub(connection)

        # search the API 
        search_results=search_api.search('POLYGON((-155.75 18.90, -155.75 20.2, -154.75 19.50, -155.75 18.90))',
        '2021-08-14', '2021-08-16',  polarisation='VV', orbit_direction='Ascending', 
        sensor_mode='IW', product='SLC', instrument_name='Sentinel-1')

        # Download datasets (a.k.a products found by search())
        search_api.download(search_results) # This might take a long time
