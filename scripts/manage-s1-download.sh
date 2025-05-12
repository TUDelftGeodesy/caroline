#!/bin/bash

# This script manages the Sentinel-1 data download by checking every hour

# Figure out where we are installed
CAROLINE=$(readlink -f $(dirname $BASH_SOURCE) | sed -e 's+/scripts$++')

# Load required python and gdal modules in case of submissions
source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1-alma9
source ~/.bashrc
#
# Load required python environment with gdal
VENV_LOCATION=$(python3 ${CAROLINE}/caroline/config.py "CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY")
source ${VENV_LOCATION}/bin/activate

DOWNLOAD_CONFIG=$(python3 ${CAROLINE}/caroline/config.py "CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY")

for FOLDER in `ls "${DOWNLOAD_CONFIG}/periodic"`
do
  caroline-download --config "${DOWNLOAD_CONFIG}/download-config.yaml" --geo-search "${DOWNLOAD_CONFIG}/periodic/${FOLDER}/geosearch.yaml"
done
