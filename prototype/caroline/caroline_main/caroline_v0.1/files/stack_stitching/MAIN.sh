#!/bin/bash 

#PBS -q guest -l nodes=n03-{node}:ppn=1

module load matlab
matlab -nodisplay -nosplash -nodesktop -r "run('{stitch_dir}/{AoI_name}_s1_{asc_dsc}_t{track}/MAIN.m');exit;"

