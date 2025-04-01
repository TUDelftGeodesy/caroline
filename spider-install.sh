#!/bin/bash
#
# installs caroline on Spider

source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1-alma9

CWD=`pwd`

python3 ${CWD}/caroline/spider_install.py ${CWD}
