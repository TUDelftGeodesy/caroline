#!/bin/bash

# This script starts the find-new-insar-files.sh script, and submits to the scheduler

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

# Find the work directory
CAROLINE_WORK=$(python3 ${CAROLINE}/caroline/config.py "CAROLINE_WORK_DIRECTORY")

# Identify the run mode
RUN_MODE=$(python3 ${CAROLINE}/caroline/config.py "RUN_MODE")

# Run script to find if any new files have been downloaded since we last checked and
# save the list of newly downloaded files in an output file
RUN_TS=$(date +%Y%m%dT%H%M%S)
NEW_INSAR_FILES_FILE="${CAROLINE_WORK}/new-insar-files-${RUN_TS}.out"

if [ "${RUN_MODE}" = "LIVE" ]; then
  bash ${CAROLINE}/scripts/find-new-insar-files.sh > "${NEW_INSAR_FILES_FILE}"
else
  echo "" > "${NEW_INSAR_FILES_FILE}"
fi

# Move the Force start file
FORCE_START_FILE="${CAROLINE_WORK}/force-start-runs-${RUN_TS}.dat"

if [ $# -eq 2 ]; then  # something needs to be force-started still, so let's add that one first, then move it
  FS_AOI=$1
  FS_TRACK=$2
  echo "${FS_AOI};${FS_TRACK}" > "${CAROLINE_WORK}/force-start-runs.dat"
fi

mv "${CAROLINE_WORK}/force-start-runs.dat" ${FORCE_START_FILE}
echo "" > "${CAROLINE_WORK}/force-start-runs.dat"

# submit the new files to the scheduler
python3 ${CAROLINE}/caroline/scheduler.py ${NEW_INSAR_FILES_FILE} ${FORCE_START_FILE}
