#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=4
#SBATCH --partition=normal

source ~/.bashrc

source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load **python3_module** **gdal_module**
source **caroline_virtual_environment_directory**/bin/activate

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has started merge-to-stack-matlab.sh (AoI **merge_to_stack_matlab:general:AoI-name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log

export PATH="**merge_to_stack_matlab:general:depsi_group-code-directory**:$PATH"
export PYTHONPATH="**merge_to_stack_matlab:general:depsi_group-code-directory**:$PYTHONPATH"

python3 merge-to-stack-matlab.py || exit 5

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has finished merge-to-stack-matlab.sh (AoI **merge_to_stack_matlab:general:AoI-name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log
