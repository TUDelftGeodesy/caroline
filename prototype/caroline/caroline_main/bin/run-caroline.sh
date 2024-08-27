#!/bin/bash

# Wrapper script around Caroline_v0_2.sh that first checks for new downloads in the veenwijden area
# and then starts Caroline_v0_2.sh with the veenwijden tracks and a config for further processing
# the nl_amsterdam area

# Figure out where we are installed
CAROLINE=$(readlink -f $(dirname $BASH_SOURCE) | sed -e 's+/bin$++')
CAROLINE_BIN="${CAROLINE}/bin"
CAROLINE_WORK="${CAROLINE}/work"

PATH="${CAROLINE_BIN}:${PATH}"

echo "\$CAROLINE: $CAROLINE"
echo "\$CAROLINE_BIN: $CAROLINE_BIN"
echo "\$CAROLINE_WORK: $CAROLINE_WORK"
echo "\$PATH: $PATH"

# Run script to find if any new files have been downloaded since we last checked and
# save the list of newly downloaded files in an output file
RUN_TS=$(date +%Y%m%dT%H%M%S)
NEW_INSAR_FILES_FILE="${CAROLINE_WORK}/new-insar-files-${RUN_TS}.out"
find-new-insar-files.sh > "${NEW_INSAR_FILES_FILE}"

# If the output file with downloaded files has more than 32 bytes, that means new files
# have been downloaded (the No new files found message is 32 bytes, new files found is 500+ bytes)
if [ "$(cat ${NEW_INSAR_FILES_FILE} | wc -c)" -gt "32" ]; then

  # Loop over the available area-track-lists & corresponding parameter files in run-files
  # area-track-lists ATL.dat requires parameter file param_file_Caroline_v1_0_spider_ATL.txt
  for AREA in `ls ${CAROLINE}/area-track-lists/`
  do
    # Check if the downloaded files pertain to tracks we are interested in
    TRACKS=$(cat "${NEW_INSAR_FILES_FILE}" \
      | cut -d/ -f7 \
      | sort -u \
      | grep -F -f ${CAROLINE}/area-track-lists/${AREA})

    # If we found new files for tracks we are interested in
    if [ ! -z "${TRACKS}" ]; then

      # Convert tracks list into csv
      TRACKS_CSV=$(echo ${TRACKS} | tr ' ' ',')

      # Submit caroline core to job queue
      #
      # Load required python and gdal modules
      source /etc/profile.d/modules.sh
      source /project/caroline/Software/bin/init.sh
      module load python/3.9.6 gdal/3.4.1
      #
      # Load required python environment with gdal
      source /project/caroline/Share/users/caroline-svandiepen/virtual_envs/caroline_v2/bin/activate
      #
      # Chdir to script directory
      cd ${CAROLINE}/caroline_v1.0/run_files/
      #
      # Submit the job to the cluster's scheduler (slurm) with the correct parameter file determined by the AREA name
      sbatch ./Caroline_v1_0.sh \
        --config-file param_file_Caroline_v1_0_spider_$(echo ${AREA} | cut -d. -f1).txt \
        --tracks "${TRACKS_CSV}"
    fi
  done

fi
