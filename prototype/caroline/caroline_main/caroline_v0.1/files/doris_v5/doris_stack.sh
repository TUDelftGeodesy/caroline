#!/bin/bash 

#PBS -q guest -l nodes=n03-{nodes}:ppn=8

export PYTHONPATH=/home/everybody/python/py_modules/lib64/python2.7/site-packages/lib/python2.7/site-packages:/home/everybody/python/py_modules/lib64/python2.7/site-packages:$PYTHONPATH
source_path=/home/everybody/projects/transponders/stacks/s1/doris
export PYTHONPATH=$source_path:$PYTHONPATH 
export PATH=/home/fjvanleijen/bin/doris/doris_v5_wu_branch:/home/fjvanleijen/bin/doris/doris_v5_wu_branch:/home/everybody/bin/snaphu:$PATH 
python /home/everybody/projects/transponders/stacks/s1/doris/doris/doris_stack/main_code/doris_main.py -p {doris_path}
