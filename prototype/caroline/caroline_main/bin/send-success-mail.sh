#!/bin/bash

param_file=$1
cpath=$2
version=$3
caroline_dir=$4
tracks_csv=$5
timestamps=$6
if [ "$#" -eq 6 ]; then
  slurm_id="UNABLE_TO_IDENTIFY"  # backwards compatibility with already running jobs
else
  slurm_id=$7
fi

EMAILS=$(grep "^send_completion_email*" ${cpath}/${param_file} | cut -d"'" -f2 | xargs echo)
AoI_name=$(echo ${param_file} | cut -d_ -f9- | cut -d/ -f1 | sed -r 's/.{16}$//' | xargs echo)
sensor=$(grep "^sensor*" ${cpath}/${param_file} | cut -d"'" -f2 | xargs echo)

echo "Subject: CAROLINE: ${sensor}/${tracks_csv}/${timestamps}/${AoI_name}

$(python3 ${caroline_dir}/caroline_v${version}/bin/utils/send_success_email.py ${param_file} ${cpath} ${slurm_id})" | /usr/sbin/sendmail ${EMAILS}