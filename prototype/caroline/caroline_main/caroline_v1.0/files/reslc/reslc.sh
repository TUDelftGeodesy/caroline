#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=4
#SBATCH --partition=normal

source ~/.bashrc

source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1

export PATH="{pydepsi_code_dir}:$PATH"
export PYTHONPATH="{pydepsi_code_dir}:$PYTHONPATH"

python3 reslc_{AoI_name}_{sensor}_{asc_dsc}_t{track}.py
