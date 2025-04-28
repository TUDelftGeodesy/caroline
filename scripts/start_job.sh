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
source ${VENV_LOCATION}/bin/activate

if [ $# -eq 5 ]; then  # put a note in the working directory as we're not running a bash file
  CAROLINE_WORK=$(python3 ${INSTALL_LOCATION}/caroline/config.py "CAROLINE_WORK_DIRECTORY")
  echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has started job ${JOB_TYPE} (AoI $(echo ${PARAMETER_FILE} | rev | cut -d/ -f1 | rev | cut -d. -f1), track ${TRACK_NUMBER}) with slurm-ID $SLURM_JOB_ID)" >> ${CAROLINE_WORK}/submitted_jobs.log
fi

python3 ${INSTALL_LOCATION}/caroline/preparation.py ${PARAMETER_FILE} ${TRACK_NUMBER} ${JOB_TYPE} || exit 4

if [ $# -eq 5 ]; then  # put a note in the working directory as we're not running a bash file
  echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has finished job ${JOB_TYPE} (AoI $(echo ${PARAMETER_FILE} | rev | cut -d/ -f1 | rev | cut -d. -f1), track ${TRACK_NUMBER}) with slurm-ID $SLURM_JOB_ID)" >> ${CAROLINE_WORK}/submitted_jobs.log

else  # backwards compatibility
  BASH_FILE_DIRECTORY=$6
  BASH_FILE=$7

  echo "----------------------------------------------------"
  echo "Starting bash job with the following characteristics"
  echo "----------------------------------------------------"
  echo "Directory: ${BASH_FILE_DIRECTORY}"
  echo "File: ${BASH_FILE}"
  echo "-----------------------------------------------"
  echo ""

  cd ${BASH_FILE_DIRECTORY}
  bash ${BASH_FILE} || exit 4
fi
