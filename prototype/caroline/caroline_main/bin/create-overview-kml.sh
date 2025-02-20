#!/bin/bash

# Load required python and gdal modules in case of submissions
source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.9.6 gdal/3.4.1-alma9
#
# Load required python environment with gdal
source /project/caroline/Share/users/caroline-svandiepen/virtual_envs/caroline_v2/bin/activate

python3 /project/caroline/Software/caroline-prototype/caroline_v1.0/bin/utils/create_overview_kml.py
