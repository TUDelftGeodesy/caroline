#!/bin/bash

# Figure out where we are installed
CAROLINE=$(readlink -f $(dirname $BASH_SOURCE) | sed -e 's+/scripts$++')

# Load required python and gdal modules in case of submissions
source ${CAROLINE}/scripts/imports.sh

# Find the work directory
CAROLINE_WORK=$(python3 ${CAROLINE}/caroline/config.py "CAROLINE_WORK_DIRECTORY")

SQUEUE=`squeue --me`

while [ $(echo $SQUEUE | wc -c) -gt 1 ]
do
  SQUEUE=$(echo ${SQUEUE} | cut -d" " -f9-)
  JOB_ID=$(echo ${SQUEUE} | cut -d" " -f1)
  JOB=$(echo ${SQUEUE} | cut -d" " -f-8)
  if [ $(echo ${JOB_ID} | wc -c) -gt 1 ]; then # a space is left at the end, which we do not want to search for
    echo "
${JOB}
$(grep ${JOB_ID} ${CAROLINE_WORK}/submitted_jobs.log)
"
  fi
done
