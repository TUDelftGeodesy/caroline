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
#SBATCH --cpus-per-task=2

# The default memory per node is 1024 megabytes (1GB) (for multiple tasks, specify --mem-per-cpu instead)

#SBATCH --mail-type=END

# Your job commands go below here

# Uncomment these lines when your job requires this software
# Uncomment these lines when your job requires this software

module --ignore-cache load matlab/R2021b

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has started crop.sh (AoI {AoI_name}, tracks {track}) with slurm-ID $SLURM_JOB_ID)" >> {caroline_work}/submitted_jobs.log

#srun matlab -nodisplay -nosplash -nodesktop < {crop_dir}/{AoI_name}_{sensor}_{asc_dsc}_t{track}/crop.m
srun matlab -nodisplay -nosplash -nodesktop -r "run('{crop_dir}/{AoI_name}_{sensor}_{asc_dsc}_t{track}/crop.m');exit;"

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has finished crop.sh (AoI {AoI_name}, tracks {track}) with slurm-ID $SLURM_JOB_ID)" >> {caroline_work}/submitted_jobs.log
