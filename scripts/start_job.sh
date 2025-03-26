#!/bin/bash
# This file is located in the slurm output directory. It is the start of all jobs, which are first prepared and then
# executed (if a bash file is passed)

if [ $# -lt 4  ]; then
  echo usage: $0 parameter_file track_number job_type caroline_install_location caroline_venv_location [bash_file_directory] [bash_file]
  exit 127
fi

PARAMETER_FILE=$1
TRACK_NUMBER=$2
JOB_TYPE=$3
INSTALL_LOCATION=$4
VENV_LOCATION=$5

# Load required python and gdal modules in case of submissions
source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1-alma9
source ${VENV_LOCATION}/bin/activate

python3 ${INSTALL_LOCATION}/caroline/preparation.py ${PARAMETER_FILE} ${TRACK_NUMBER} ${JOB_TYPE}

if [ $# -eq 7 ]; then
  BASH_FILE_DIRECTORY=$6
  BASH_FILE=$7
  cd ${BASH_FILE_DIRECTORY}
  bash ${BASH_FILE}
fi
