#!/bin/bash 

#PBS -q guest -l nodes=n03-{node}:ppn=1

module load matlab
matlab -nodisplay -nosplash -nodesktop -r "run('{depsi_dir}/{AoI_name}_s1_{asc_dsc}_t{track}/psi/read_mrm_{AoI_name}_s1_{asc_dsc}_t{track}.m');exit;"

