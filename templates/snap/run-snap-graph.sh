#!/bin/bash

# You can control the resources and scheduling with '#SBATCH' settings
# (see 'man sbatch' for more information on setting these parameters)

# Request 1 CPU per active thread of your program (assume 1 unless you specifically set this)
# The default number of CPUs per task is 1 (note: CPUs are always allocated per 2)
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=05:00:00
#SBATCH --cpus-per-task=8
#SBATCH --partition=normal


# The default memory per node is 1024 megabytes (1GB) (for multiple tasks, specify --mem-per-cpu instead)
#SBATCH --mem-per-cpu=8000

#SBATCH --mail-type=END

# Your job commands go below here

# Uncomment these lines when your job requires this software
# Uncomment these lines when your job requires this software

source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1-alma9 snap/13.0.0
source ~/.bashrc
source **caroline_virtual_environment_directory**/bin/activate

echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has started run-snap-graph.sh (ARRAY ID $SLURM_ARRAY_TASK_ID) (AoI **snap:general:AoI-name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log

output_path="**snap-output-path**"
ROME_CONSTRAINED="**rome-constrained**"

graph=`ls ${output_path}/PROCESSID-${SLURM_ARRAY_TASK_ID}-*.xml`

if [ "${ROME_CONSTRAINED}" -eq "1" ]; then  # we have 16GB cores
  gpt_query="gpt -q ${SLURM_CPUS_PER_TASK} -c $((9 * $SLURM_CPUS_PER_TASK))G -J-Xmx$((15 * $SLURM_CPUS_PER_TASK))G -e -x -J-Dsnap.jai.defaultTileSize=512 -J-Dsnap.dataio.reader.tileWidth=512 -J-Dsnap.dataio.reader.tileHeight=512"
else # we have 12GB cores
  gpt_query="gpt -q ${SLURM_CPUS_PER_TASK} -c $((7 * $SLURM_CPUS_PER_TASK))G -J-Xmx$((11 * $SLURM_CPUS_PER_TASK))G -e -x -J-Dsnap.jai.defaultTileSize=512 -J-Dsnap.dataio.reader.tileWidth=512 -J-Dsnap.dataio.reader.tileHeight=512"
fi

${gpt_query} --diag

time ${gpt_query} ${graph}


echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has finished run-snap-graph.sh (ARRAY ID $SLURM_ARRAY_TASK_ID) (AoI **snap:general:AoI-name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log

