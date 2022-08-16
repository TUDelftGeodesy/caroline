#!/bin/bash

if [ $# -lt 4  ]; then
echo usage: $0 project_id Npixels ml_r ml_az [mrm_az0] [mrm_azN] [mrm_r0] [mrm_rN]
exit 127
fi

project_id=${1}
width=${2}
ml_r=${3}
ml_az=${4}
mrm_az0=${5}
mrm_azN=${6}
mrm_r0=${7}
mrm_rN=${8}

cpxfiddle -w ${width} -fr4 -M${ml_r}/${ml_az} -qnormal -osunraster -cgray ${project_id}_mrm.raw > ${project_id}_mrm_${ml_r}x${ml_az}.ras
convert -modulate 200 ${project_id}_mrm_${ml_r}x${ml_az}.ras ${project_id}_mrm_bright_${ml_r}x${ml_az}.ras

echo "cpxfiddle -w ${width} -f r4 -M ${ml_r}/${ml_az} -q normal -o sunraster -c gray -l ${mrm_az0} -L ${mrm_azN} -p ${mrm_r0} -P ${mrm_rN} ${project_id}_mrm.raw > ${project_id}_mrm_${ml_r}x${ml_az}.ras " > ${project_id}_mrm_${ml_r}x${ml_az}.ras.sh
