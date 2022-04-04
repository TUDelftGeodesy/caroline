#!/bin/bash

#--- Define the job requirements ---

#SBATCH -N 1			# number of nodes
#SBATCH -c 4			# number of cores; coupled to 8000 MB memory per core
#SBATCH -t 5:00:00		# maximum run time in [HH:MM:SS] or [MM:SS] or [minutes]
#SBATCH -p normal		# partition (queue); job can run up to 5 days
#SBATCH --qos=long		
#SBATCH --ntasks=1		

echo "Start"; date
TEMP_DIR="/project/caroline/Share/users/caroline-mgarcia/tmp"

# Cleanup temporary folder
function clean_up {
  rm --recursive --force "$TEMP_DIR" && echo "Clean up of $tmp_dir completed successfully."
  exit
}

# Setup clean_up to run on exit
trap 'clean_up' EXIT

#--- Run your application ---

source /project/caroline/Software/caroline/caroline-venv/bin/activate
cd /project/caroline/Share/users/caroline-mgarcia

python interferogram.py -s 20160101 -e 20160120 -c 5 -n test_stack -f amsterdam.kml -R 2000 -pl VV -t $TEMP_DIR -md 20160107 

echo "Done"; date
