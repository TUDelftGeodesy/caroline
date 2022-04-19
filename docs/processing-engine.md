# Download Engine

The Processing Engine is a Python package that provides a CLI around RIPPL for data processing. Specifically for the production of interferograms.

## Requirements

* Python 3.8 or later
* Dependencies:
  * rippl
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
4. Install Rippl: https://bitbucket.org/grsradartudelft/rippl/src/master/rippl/ 
5. Go to the package (**processing**) root directory (where the `setup.py` is located).
6. Install the package using `PIP`:
    ```shell
    pip install .
    ```
    or for developing mode:
    ```shell
    pip install -e .
    ```

## Configuration

### Pacakge Configuration
Package level configurations are managed using an `.env` file which is expected to be in the package root directory. For the examples shown here, the following is required:

```shell
PRODUCTS_DIR="/project/caroline/Share/users/caroline-mgarcia/products"
TMP_DIR="</path/to/temporal/directory/>"
MULTILOOK_TMP="</path/to/temporal/directory/for-multilook>"
RESAMPLING_TMP="</path/to/temporal/directory/for-resampling>"
```

`PRODUCTS_DIR` is where the main outputs of processing will be stored, e.g. interferogram. `TMP_DIR, MULTILOOK_TMP, RESAMPLING_TMP` are directories to store partial processing results. When a path for multilook and resampling is not provided, all partial results will be saved to `TMP_DIR`.

### Rippl Configuration

The processing engine depends on the internal configurations of the *rippl* package. In *rippl*, configurations are stored in the `user_settings.txt` file, which is created as part of the package setup step. See the rippl's documentation for details. Therefore, part of the behaviour of the processing engine is currently controlled by the configuration of rippl itself. 

The user settings of *rippl* that influence the Processing Engine are:

```shell
radar_data_stacks: /path/to/store/dat_stacks
radar_database: /path/to/radar-data/pool
orbit_database: /path/orbits-files/pool
DEM_database: /path/to/dem-files
NWP_model_database: /path/to/nwp-models
GIS_database: /path/to/gis/directory
Snaphu_path: /path/snaphu
radar_data_products: /path/to/directory/for/data-products
...
```
  

## Examples

### Creating interferogram using the CLI

To create an interferogram, call the `main.py` program in the `processing/processing/interferogram` directory.

```shell
python processing/interferogram/main.py --start_date <start_date> --end_date <end_date> --mdate <master_date> --process <number-of-processes> --name <name-output-datastack> --file <path/to/KML-or-SHP/file> --resplanar <output-resolution> --pol <polarisation-type>
```

The outputs will be saved to the directory specified by `radar_data_products` in the `user_settings.txt` of the rippl's installation.

