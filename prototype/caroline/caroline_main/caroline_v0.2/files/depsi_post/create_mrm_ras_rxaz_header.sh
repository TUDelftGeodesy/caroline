#!/bin/bash

if [ $# -lt 5  ]; then
echo usage: $0 project_id Npixels ml_r ml_az cpxfiddle_dir [mrm_az0] [mrm_azN] [mrm_r0] [mrm_rN]
exit 127
fi

project_id=${1}
width=${2}
ml_r=${3}
ml_az=${4}
mrm_az0=${6}
mrm_azN=${7}
mrm_r0=${8}
mrm_rN=${9}
cpxfiddle_dir=${5}

$cpxfiddle_dir -w ${width} -f r4 -M ${ml_r}/${ml_az} -q normal -o sunraster -c gray ${project_id}_mrm.raw > ${project_id}_mrm_${ml_r}x${ml_az}.ras
convert -modulate 200 ${project_id}_mrm_${ml_r}x${ml_az}.ras ${project_id}_mrm_bright_${ml_r}x${ml_az}.ras

echo "cpxfiddle -w ${width} -f r4 -M ${ml_r}/${ml_az} -q normal -o sunraster -c gray -l ${mrm_az0} -L ${mrm_azN} -p ${mrm_r0} -P ${mrm_rN} ${project_id}_mrm.raw > ${project_id}_mrm_${ml_r}x${ml_az}.ras " > ${project_id}_mrm_${ml_r}x${ml_az}.ras.sh
