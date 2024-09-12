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

  # Enter a while loop that checks if all areas are properly submitted after their dependencies
  ALL_DEPENDENCIES_SUBMITTED=0
  COUNTER=0
  while [ ${ALL_DEPENDENCIES_SUBMITTED} -eq "0" ]
  do
    # turn to true, if it is not true it will be turned to false by the following if statements
    ALL_DEPENDENCIES_SUBMITTED=1

    # exit in case of infinite loop (should not be possible
    COUNTER=$((${COUNTER} + 1))
    if [ ${COUNTER} -eq "20" ]; then
      echo "Submission of one or more jobs failed, check loops." | mailx -s "CAROLINE Infinite Loop" s.a.n.vandiepen@tudelft.nl
      exit 127
    fi

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
        # Check if the job has not already been submitted --> job_id_AREA_TS.txt must not exist
        if [ ! -f ${CAROLINE}/caroline_v1.0/run_files/job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt ]; then
          # Check if there is a dependency. If Dependency: None / Dependency: none / Dependency: /
          # no Dependency line in the AREA file, there is no dependency and we continue normally
          DEPENDENCY=$(grep "Dependency" ${CAROLINE}/area-track-lists/${AREA} | cut -d: -f2 | xargs echo)
          if [[ ${DEPENDENCY} = "None" || ${DEPENDENCY} = "none" || -z ${DEPENDENCY} ]]; then

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
              --tracks "${TRACKS_CSV}" > job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt
          else
            # A dependency is introduced. We need to check if it is a valid dependency (if it is in area-track-lists)
            # and if it is already submitted (if job_id_AREA_TIMESTAMP.txt exists)

            if [ -f ${CAROLINE}/area-track-lists/${DEPENDENCY}.dat ]; then # file exists

              #Check if the dependency has been submitted
              if [ -f ${CAROLINE}/caroline_v1.0/run_files/job_id_${DEPENDENCY}_${RUN_TS}.txt ]; then
                # cut out the job ID from the submitted dependency
                DEPENDENCY_JOB_ID=$(cat ${CAROLINE}/caroline_v1.0/run_files/job_id_${DEPENDENCY}_${RUN_TS}.txt | \
                  cut -d" " -f4 | xargs echo)

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
                # with the dependency job id, and the argument that it will be killed if the dependency is invalid
                # (i.e., the process it depended on failed for whatever reason)
                sbatch --dependency=afterok:${DEPENDENCY_JOB_ID} --kill-on-invalid-dep=yes ./Caroline_v1_0.sh \
                  --config-file param_file_Caroline_v1_0_spider_$(echo ${AREA} | cut -d. -f1).txt \
                  --tracks "${TRACKS_CSV}" > job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt

              else
                # it has not been submitted, we need another while loop iteration
                ALL_DEPENDENCIES_SUBMITTED=0
              fi

            else
              # Invalid dependency --> just submit the job and send a warning email to Simon
              echo "Job "${AREA}" submitted with invalid dependency "${DEPENDENCY}", continuing without dependency." | mailx -s "CAROLINE Invalid job dependency" s.a.n.vandiepen@tudelft.nl

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
                --tracks "${TRACKS_CSV}" > job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt

            fi
          fi
        fi
      fi
    done
  done

  # Check if all runs are finished
  ALL_RUNS_FINISHED=0
  cd ${CAROLINE}/caroline_v1.0/run_files/
  ls job_id_*${RUN_TS}.txt > submitted_jobs_${RUN_TS}.txt

  # setup check if we should submit something to the portal, and if so if it already has been done
  for job in `cat submitted_jobs_${RUN_TS}.txt`
  do
    PARAM_FILE="param_file_Caroline_v1_0_spider_$(echo ${job} | cut -c 8- | sed -r 's/.{20}$//').txt"
    DO_DP=$(grep "do_depsi_post" ${PARAM_FILE} | cut -d= -f2 | xargs echo)
    DP_MODE=$(grep "depsi_post_mode" ${PARAM_FILE} | cut -d"'" -f2 | xargs echo)
    PORTAL_REQ=0
    if [ ${DO_DP} -eq 1 ]; then
      if [ "${DP_MODE}" = "csv" ]; then
        PORTAL_REQ=1
      fi
    fi
    echo ${PORTAL_REQ} > portal_${job}
  done

  while [ ${ALL_RUNS_FINISHED} -eq "0" ]
  do
    ALL_RUNS_FINISHED=1

    # call the squeue with the me filter
    squeue > squeue_${RUN_TS}.txt
    for run in `cat submitted_jobs_${RUN_TS}.txt`
    do
      if [ `cat portal_${job}` -eq 1 ]; then
        JOB_ID=$(cat ${run} | cut -d" " -f4 | xargs echo)
        FINISHED=$(grep "${JOB_ID}" squeue_${RUN_TS}.txt)
        if [ "$(echo ${FINISHED} | wc -c)" -gt "0" ]; then
          ALL_RUNS_FINISHED=0
        else
          # set to 0 so we only upload once
          echo "0" > portal_${run}
          # retrieve the directories we need to upload
          AUX_DIR=$(grep "Running with config file" slurm-${JOB_ID}.out | cut -d" " -f5 | cut -d/ -f1)
          DEPSI_DIR=`cat ${AUX_DIR}/depsi_directory.txt`
          cd ${DEPSI_DIR}
          for dir in `cat ${CAROLINE}/caroline_v1.0/run_files/${AUX_DIR}/loop_directories_depsi.txt`
          do
            cd ${dir}/psi
            upload-result-csv-to-skygeo.sh
            cd ${DEPSI_DIR}
          done
          cd ${CAROLINE}/caroline_v1.0/run_files/
        fi
      fi
    done
    if [ ${ALL_RUNS_FINISHED} -eq "0" ]; then
      echo "Not all runs finished yet, sleeping..."
      sleep 60
    fi
  done

fi
