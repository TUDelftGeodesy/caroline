#!/bin/bash

SQUEUE=`squeue --me`

while [ $(echo $SQUEUE | wc -c) -gt 1 ]
do
  SQUEUE=$(echo ${SQUEUE} | cut -d" " -f9-)
  JOB_ID=$(echo ${SQUEUE} | cut -d" " -f1)
  JOB=$(echo ${SQUEUE} | cut -d" " -f-8)
  echo "
${JOB}
$(grep ${JOB_ID} /project/caroline/Software/caroline-prototype*/work/submitted_jobs.log)
"
done
