#!/bin/bash

for JOB in `squeue --me`
do
  echo "
${JOB}
$(grep $(echo ${JOB} | cut -d" " -f1 | xargs echo) /project/caroline/Software/caroline-prototype*/work/submitted_jobs.log)
"
done
