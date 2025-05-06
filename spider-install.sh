#!/bin/bash
#
# installs caroline on Spider

source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1-alma9

if [ $# -eq 0 ]; then
  CONFIG_FILE="None"
elif [ $# -eq 1 ]; then
  CONFIG_FILE=$1
else
  echo usage: $0 [configuration_file]
fi

CWD=`pwd`

python3 ${CWD}/caroline/spider_install.py ${CWD} ${CONFIG_FILE}
CAROLINE_INSTALL_DIRECTORY=$(python3 ${CWD}/caroline/config.py "CAROLINE_INSTALL_DIRECTORY" "${CWD}/${CONFIG_FILE}")

echo "Updating contextual data..."
bash ${CAROLINE_INSTALL_DIRECTORY}/scripts/manage-contextual-data.sh "verbose"
echo "Finished updating contextual data!"
