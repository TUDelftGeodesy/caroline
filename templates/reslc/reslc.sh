#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=4
#SBATCH --partition=normal

source ~/.bashrc

source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1-alma9

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has started reslc.sh (AoI **reslc_AoI_name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log

export PATH="**reslc_code_dir**:$PATH"
export PYTHONPATH="**reslc_code_dir**:$PYTHONPATH"

python3 reslc.py

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has finished reslc.sh (AoI **reslc_AoI_name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log
