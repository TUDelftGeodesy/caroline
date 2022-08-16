#!/bin/bash

# You can control the resources and scheduling with '#SBATCH' settings
# (see 'man sbatch' for more information on setting these parameters)

# The default partition is the 'general' partition
#SBATCH --partition=normal

# The default Quality of Service is the 'short' QoS (maximum run time: 4 hours)
#SBATCH --qos=long

# The default run (wall-clock) time is 1 minute
#SBATCH --time=4-00:00:00

# The default number of parallel tasks per job is 1
#SBATCH --ntasks=1

# Request 1 CPU per active thread of your program (assume 1 unless you specifically set this)
# The default number of CPUs per task is 1 (note: CPUs are always allocated per 2)
#SBATCH --cpus-per-task=8

# The default memory per node is 1024 megabytes (1GB) (for multiple tasks, specify --mem-per-cpu instead)
#SBATCH --mem-per-cpu=8000

#SBATCH --mail-type=END

# Your job commands go below here

# Uncomment these lines when your job requires this software
# Uncomment these lines when your job requires this software

source_path=/project/caroline/Share/users/caroline-svandiepen/software/doris_v5/doris_v5_latest:/project/caroline/Share/users/caroline-svandiepen/software/doris_v5/doris_v5_latest/doris/doris_stack/functions
export PYTHONPATH=$source_path:$PYTHONPATH 
export PATH=/project/caroline/Share/users/caroline-svandiepen/software/doris_v5/doris_v5_lastest:/project/caroline/Share/users/caroline-svandiepen/software/doris_v5/doris_v5_latest/doris/doris_stack/functions:/project/caroline/Software/snaphu:$PATH 
python3 /project/caroline/Share/users/caroline-svandiepen/software/doris_v5/doris_v5_latest/doris/doris_stack/main_code/doris_main.py -p {doris_path}
