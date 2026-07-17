#!/bin/bash
#
# installs caroline on Spider
CWD=`pwd`

source ${CWD}/scripts/imports.sh

if [ $# -eq 0 ]; then
  CONFIG_FILE="config/spider-config.yaml"
elif [ $# -eq 1 ]; then
  CONFIG_FILE=$1
else
  echo usage: $0 [configuration_file]
fi

python3 ${CWD}/caroline/spider_install.py ${CWD} ${CONFIG_FILE}
CAROLINE_INSTALL_DIRECTORY=$(python3 ${CWD}/caroline/config.py "CAROLINE_INSTALL_DIRECTORY" "${CWD}/${CONFIG_FILE}")

echo "Updating contextual data..."
bash ${CAROLINE_INSTALL_DIRECTORY}/scripts/manage-contextual-data.sh "verbose"
echo "Finished updating contextual data!"

VENV=$(python3 ${CWD}/caroline/config.py "CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY" "${CWD}/${CONFIG_FILE}")
source ${VENV}/bin/activate

echo "Adding download configurations and area-track-lists..."
python3 ${CAROLINE_INSTALL_DIRECTORY}/caroline/preparation.py "installation"
echo "Added download configurations and area-track-lists!"

echo "Finished installation!"
