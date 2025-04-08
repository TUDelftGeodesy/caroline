#!/bin/bash

if [ $# != 1  ]; then
echo usage: $0 project_id
exit 127
fi

project_id=${1}

tar zcvf ${project_id}_post_tarfile.tar.gz \
${project_id}_mrm_bright_*.ras \
${project_id}_mrm_uint8.raw \
${project_id}_side_lobe_mask.raw \
${project_id}_amp_disp.raw \
${project_id}_*.mat \
${project_id}_ps_ts*.raw \
*.res \
param*.txt \
depsi_post*.m \
plots

