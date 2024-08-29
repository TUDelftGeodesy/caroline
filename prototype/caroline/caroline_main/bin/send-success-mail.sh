#!/bin/bash

param_file=$1
cpath=$2
AoI_name=$3
version=$4
caroline_dir=$5

EMAILS=$(grep "send_completion_email" ${cpath}/${param_file} | cut -d"'" -f2 | xargs echo)

python3 ${caroline_dir}/caroline_v${version}/bin/utils/send_success_email.py ${param_file} ${cpath} ${AoI_name} | mailx -s "CAROLINE: run ${AoI_name} Finished" -v ${EMAILS}
