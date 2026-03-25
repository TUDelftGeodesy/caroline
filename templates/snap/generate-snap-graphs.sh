#!/bin/bash

# You can control the resources and scheduling with '#SBATCH' settings
# (see 'man sbatch' for more information on setting these parameters)

# The default partition is the 'general' partition
#SBATCH --partition=normal

# The default Quality of Service is the 'short' QoS (maximum run time: 4 hours)
#SBATCH --qos=long

# The default run (wall-clock) time is 1 minute
#SBATCH --time=4-12:00:00

# The default number of parallel tasks per job is 1
#SBATCH --ntasks=1

# Request 1 CPU per active thread of your program (assume 1 unless you specifically set this)
# The default number of CPUs per task is 1 (note: CPUs are always allocated per 2)
#SBATCH --cpus-per-task=1

# The default memory per node is 1024 megabytes (1GB) (for multiple tasks, specify --mem-per-cpu instead)
#SBATCH --mem-per-cpu=8000

#SBATCH --mail-type=END

# Your job commands go below here

# Uncomment these lines when your job requires this software
# Uncomment these lines when your job requires this software

source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1-alma9 snap/12.0.0
source ~/.bashrc
source **caroline_virtual_environment_directory**/bin/activate

caroline_install_location="**caroline_install_directory**"
mother="**general:timeframe:mother**"
start="**general:timeframe:start**"
end="**general:timeframe:end**"
track="**track_formatted**"
output_path="**snap-output-path**"
aoi_wkt_path="**snap-output-path**/aoi.wkt"
polarizations="VV"
DRY_RUN="**dry_run**"

start=${start//-/}  # remove the dashes from the dates
end=${end//-/}
mother=${mother//-/}

if [ "${DRY_RUN}" -eq "0" ]; then
  echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has started generate-snap-graphs.sh (AoI **snap:general:AoI-name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log
fi

DO_MOTHER=1
if [ -f ${output_path}/${mother}-coreg.dim ]; then
  DO_MOTHER=0
fi
COUNTER=1
if [ "${DRY_RUN}" -eq "0" ]; then
  COUNTER=$(($COUNTER-1))
fi

s1dir="**slc_base_directory**"

aoi_wkt=`cat ${aoi_wkt_path} | xargs echo`

# first move already existing graphs to a graph archive to not have them accidentally interfere
if [ "${DRY_RUN}" -eq "0" ]; then
  if [ ! -d ${output_path}/graph_archive ]; then
    mkdir ${output_path}/graph_archive
  fi
  ARCHIVE=${output_path}/graph_archive/$(date '+%Y%m%dT%H%M%S')

  mkdir ${ARCHIVE}
  for xml in `ls ${output_path}/*.xml`;
  do
    mv ${xml} ${ARCHIVE}/
  done
fi
# Then generate the new processing graphs

for daughterdir in `ls -d ${s1dir}/${track}/IW_SLC__1SDV_VVVH/*/`;  # only the directories
do
  daughter=$(echo ${daughterdir} | rev | cut -d/ -f2 | rev | xargs echo)  # cut out the daughter date from the file structure
  if [ "${daughter}" != "${mother}" ]; then  # skip the mother
    if [ "${daughter}" -ge "${start}" ]; then  # skip everything before start
      if [ "${daughter}" -le "${end}" ]; then  # skip everything after end
        if [ ! -f ${output_path}/${daughter}-coreg.dim ]; then  # skip everything that already exists
          if [ "${DRY_RUN}" -eq "0" ]; then
            echo "Start generating graph for ${daughter}..."
            if [ "${DO_MOTHER}" -eq "1" ]; then  # check if the mother still has to be done
              time snap-run \
                --scene-paths ${s1dir}/${track}/IW_SLC__1SDV_VVVH/${mother}/*.zip ${s1dir}/${track}/IW_SLC__1SDV_VVVH/${daughter}/*.zip \
                --output-path ${output_path}/${daughter}-coreg.dim \
                --output-mother-path ${output_path}/${mother}-coreg.dim \
                --aoi-wkt "${aoi_wkt}" \
                --polarizations ${polarizations} \
                --graph-path ${output_path}/PROCESSID-${COUNTER}-${mother}-${daughter}-graph.xml
              DO_MOTHER=0
            else
              time snap-run \
                --scene-paths ${s1dir}/${track}/IW_SLC__1SDV_VVVH/${mother}/*.zip ${s1dir}/${track}/IW_SLC__1SDV_VVVH/${daughter}/*.zip \
                --output-path ${output_path}/${daughter}-coreg.dim \
                --aoi-wkt "${aoi_wkt}" \
                --polarizations ${polarizations} \
                --graph-path ${output_path}/PROCESSID-${COUNTER}-${mother}-${daughter}-graph.xml
            fi
          fi
          COUNTER=$(($COUNTER+1))
        fi
      fi
    fi
  fi
done

if [ "${DRY_RUN}" -eq "0" ]; then
  echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) has finished generate-snap-graphs.sh (AoI **snap:general:AoI-name**, track **track**) with slurm-ID $SLURM_JOB_ID)" >> **caroline_work_directory**/submitted_jobs.log
else
  echo ${COUNTER}
fi
