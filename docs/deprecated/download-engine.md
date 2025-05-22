# Download Engine

The Download Engine is a Python packages that provides functionality to connect to different SAR data providers. It Downloads datasets based on geographic location, observation time and several sensor's properties (e.g., polarisation or orbit direction).

## Requirements

* Python 3.8 or later
* Dependencies:
  * python-dotenv
  * requests
  * shapely
  * fiona
  * gdal


## Installation

1. Make sure that GDAL and Python-GDAL are installed.
2. Clone the repository: `https://manuGilbert@bitbucket.org/grsradartudelft/caroline.git`
3. Create and activate a virtual environment:
   
   ```shell
    $ virtualenv my-venv
    $ source my-venv/bin/activate
   ```
4. Go to the package root directory (where the `setup.py` is located).
5. Install the package using `PIP`:
    ```shell
    pip install .
    ```
    or for developing mode:
    ```shell
    pip install -e .
    ```

## Configuration

Package level configurations are managed using an `.env` file which is expected to be in the package root directory. For the examples shown here the following is required:

    ```shell
    ASF_USERNAME="<ASF account username>"
    ASF_PASSWORD="<ASF account password>"
    ASF_BASE_URL="https://api.daac.asf.alaska.edu/"
    ORB_USERNAME="gnssguest"
    ORB_PASSWORD="gnssguest"
    ORB_BASE_URL="https://scihub.copernicus.eu/gnss/"
    BASE_DATA_DIRECTORY="<path/to/directory/to-store/SAR-data>"
    BASE_ORBIT_DIRECTORY="<path/to/directory/to-store/orbit-files>"
    ```

## Examples

### Python Interface

1. **Download SAR data**

    ```python
    """
    This is an example of how to use the Download Enigne 
    within Python.
    This example uses the  ASF API. 
    Account credentials and destination for dataset must
    be provided via an .env file.
    WARNING: This example will download 1 dataset (~4GB)
    """

    import os
    from download  import connector
    from download.asf import ASF
    from dotenv import load_dotenv
    load_dotenv()

    USERNAME = os.getenv('ASF_USERNAME')
    PASSWORD = os.getenv('ASF_PASSWORD')
    ASF_BASE_URL = os.getenv('ASF_BASE_URL')

    if __name__ == '__main__':
        # Create a connector to handle the autentification
        connetion = connector.Connector(USERNAME, PASSWORD, ASF_BASE_URL, retain_auth=True)

        connetion.test_connection()

        # instantiate API with the connector
        search_api = ASF(connetion)

        # search the API 
        search_results=search_api.search('POLYGON((-155.75 18.90,-155.75 20.2,-154.75 19.50,-155.75 18.90))',
                '2018-04-22', '2018-05-01', orbit_direction='Ascending',
                sensor_mode='IW', product='SLC', instrument_name='Sentinel-1', polarisation='HH,VV')

        # Download datasets ( a.k.a products found by search() )
        search_api.download(search_results) # This might take a long time

    ```

2. **Download Orbits**

    ```python
    """
    This example is for the download of orbit files form the SciHub API
    Must provide your own account credentials
    WARNING: This example will download many datasets
    NOTICE: The location for downloaded files must be set in the .env 
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

    ```

## Command Line Interface:

1. **Download SAR data**

    The CLI interface is available by calling the `main.py` program. It has two modes (accessible via subcommands). The `conf` subcommand or *configuration* mode expects credentials for the data provider API to be available via the `.env` configuration file. The `manual` subcommand expects credentials to be passed to the program as arguments. Use `python main.py -h` for more information.

    ```shell
    python main.py conf <start_date> <end_date> --file <path/to/KML-or-SHP/file> --orbit <orbit direction> 
    ```

1. **Download orbits**

    The CLI interface is available by calling the `orbits.py` program. It has two modes (accessible via subcommands). The `conf` subcommand or *configuration* mode expects credentials for the data provider API to be available via the `.env` configuration file. The `manual` command expects credentials to be passed to the program as arguments. Use `python orbits.py -h` for more information.

    ```shell
    python orbits.py conf <start_date> <end_date> --type <type of orbits>
    ```

## Extending the Funtionality 

The package provides an abstract class `DataSearch` as a common interface for querying and downloading datasets from REST APIs.
To extend the package to use other data providers (assuming they implement authentification using username and password), inherit from the `DataSerach` and implement the methods below to match the API specification of the data provider.

```python
from download.search import DataSearch

class MyDataProvider(DataSearch):
    """
    Implementation of DataSearch for a new data provider
    """
    
    def __init__(self, connector) -> None:
        """
        Initialise the SciHubAPI object
        Args:
            connector (obj): connector object
        """
        self.connector = connector # requires a Connector as component

    def build_query(self, *argv):
        "Implmentation for my data provider"
        pass
    
    def search(self, *argv):
        "Implmentation for my data provider"
        pass

    def download(self, *argv):
        "Implmentation for my data provider"
        pass

    def validate_download(self, *argv):
        "Implmentation for my data provider"
        pass

```
