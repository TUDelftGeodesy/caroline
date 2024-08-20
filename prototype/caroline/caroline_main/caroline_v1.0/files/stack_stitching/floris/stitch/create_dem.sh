#!/bin/bash 

source_path=/home/everybody/projects/transponders/stacks/s1/doris
export PYTHONPATH=$source_path:$PYTHONPATH 
python /home/everybody/projects/transponders/stacks/s1/doris/doris/prepare_stack/create_dem.py /home/fmgheuff/processing/s1/s1_dsc_t110 SRTM3 
