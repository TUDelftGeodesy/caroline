#!/bin/bash

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has started single-s1-download.sh (AoI **download_AoI_name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log

caroline-download --config "**caroline_download_configuration_directory**/download-config.yaml" --geo-search "**caroline_download_configuration_directory**/once/**download_directory**/geosearch.yaml"

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has finished single-s1-download.sh (AoI **download_AoI_name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log


