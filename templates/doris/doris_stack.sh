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

source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1-alma9
source ~/.bashrc
source **caroline_virtual_environment_directory**/bin/activate

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has started doris_stack.sh (AoI **coregistration_AoI_name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log

source_path=**doris_code_directory**:**doris_code_directory**/doris/doris_stack/functions:**doris_code_directory**/doris/doris_stack/main_code
export PYTHONPATH=$source_path:$PYTHONPATH 
export PATH=**doris_code_directory**:**doris_code_directory**/doris/doris_stack/functions:**doris_code_directory**/doris/doris_stack/main_code:/project/caroline/Software/snaphu:$PATH
python3 **doris_code_directory**/doris/doris_stack/main_code/doris_main.py -p **coregistration_directory** || exit 5

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has finished doris_stack.sh (AoI **coregistration_AoI_name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log
