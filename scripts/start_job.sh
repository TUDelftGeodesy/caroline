#!/bin/bash
# This file is located in the slurm output directory. It is the start of all jobs, which are first prepared and then
# executed (if a bash file is passed)

if [ $# -lt 4  ]; then
  echo usage: $0 parameter_file track_number job_type caroline_install_location caroline_venv_location [bash_file_directory] [bash_file] [slurm_job_file]
  exit 127
fi

PARAMETER_FILE=$1
TRACK_NUMBER=$2
JOB_TYPE=$3
INSTALL_LOCATION=$4
VENV_LOCATION=$5

echo "-----------------------------------------------"
echo "Starting job with the following characteristics"
echo "-----------------------------------------------"
echo "Parameter file: ${PARAMETER_FILE}"
echo "Track: ${TRACK_NUMBER}"
echo "Job: ${JOB_TYPE}"
echo "Caroline install location: ${INSTALL_LOCATION}"
echo "Caroline virtual environment: ${VENV_LOCATION}"
echo "-----------------------------------------------"
echo ""

# Load required python and gdal modules
source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1-alma9
source ~/.bashrc
conda activate ${VENV_LOCATION}

# add CAROLINE to the path and python path since it sometimes cannot find it in the virtual environment
export PATH="${INSTALL_LOCATION}:${VENV_LOCATION}:$PATH"
export PYTHONPATH="${INSTALL_LOCATION}:${VENV_LOCATION}:$PYTHONPATH"

python3 ${INSTALL_LOCATION}/caroline/preparation.py ${PARAMETER_FILE} ${TRACK_NUMBER} ${JOB_TYPE}

if [ $# -eq 8 ]; then
  BASH_FILE_DIRECTORY=$6
  BASH_FILE=$7

  SLURM_FILE=$8

  echo "----------------------------------------------------"
  echo "Starting bash job with the following characteristics"
  echo "----------------------------------------------------"
  echo "Directory: ${BASH_FILE_DIRECTORY}"
  echo "File: ${BASH_FILE}"
  echo "Slurm job file: ${SLURM_FILE}"
  echo "-----------------------------------------------"
  echo ""

  echo "$SLURM_JOB_ID" > ${SLURM_FILE}

  cd ${BASH_FILE_DIRECTORY}
  bash ${BASH_FILE}
fi
