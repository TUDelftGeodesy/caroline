#!/bin/bash

param_file=$1
cpath=$2
version=$3
caroline_dir=$4

EMAILS=$(grep "send_completion_email" ${cpath}/${param_file} | cut -d"'" -f2 | xargs echo)
AoI_name=$(echo param_file | cut -d. -f1 | cut -d_ -f7-8 | xargs echo)

python3 ${caroline_dir}/caroline_v${version}/bin/utils/send_success_email.py ${param_file} ${cpath} | mailx -s "CAROLINE: run ${AoI_name} Finished" -v ${EMAILS}
