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

# Load required python and gdal modules in case of submissions
# source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.9.6 gdal/3.4.1-alma9
#
# Load required python environment with gdal
source /project/caroline/Share/users/caroline-svandiepen/virtual_envs/caroline_v2/bin/activate
#
# Chdir to script directory
cd ${CAROLINE}/caroline_v1.0/run_files/

# Run script to find if any new files have been downloaded since we last checked and
# save the list of newly downloaded files in an output file
RUN_TS=$(date +%Y%m%dT%H%M%S)
NEW_INSAR_FILES_FILE="${CAROLINE_WORK}/new-insar-files-${RUN_TS}.out"
find-new-insar-files.sh > "${NEW_INSAR_FILES_FILE}"

if [ "$(cat ${CAROLINE_WORK}/force-start-runs.dat | wc -c)" -gt "0" ]; then
  for LINE in `cat ${CAROLINE_WORK}/force-start-runs.dat`
  do
    AREA=$(echo ${LINE} | cut -d";" -f1)
    TRACKS_CSV=$(echo ${LINE} | cut -d";" -f2)

    echo "FORCE_STARTED_AT_${RUN_TS}" > ${CAROLINE}/caroline_v1.0/run_files/timestamp_${AREA}_${RUN_TS}.txt

    # Submit the job to the cluster's scheduler (slurm) with the correct parameter file determined by the AREA name
    sbatch ./Caroline_v1_0.sh \
      --config-file param_file_Caroline_v1_0_spider_${AREA}.txt \
      --tracks "${TRACKS_CSV}" > job_id_${AREA}_${RUN_TS}.txt
    echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) submitted Caroline_v1_0.sh (AoI ${AREA}, tracks ${TRACKS_CSV}) with slurm-ID $(cat job_id_${AREA}_${RUN_TS}.txt | cut -d" " -f4 | xargs echo)" >> ${CAROLINE_WORK}/submitted_jobs.log
  done
fi
mv ${CAROLINE_WORK}/force-start-runs.dat ${CAROLINE_WORK}/force-start-runs-${RUN_TS}.dat
echo "" > ${CAROLINE_WORK}/force-start-runs.dat

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
    for AREA_FORMAT in ${CAROLINE}/area-track-lists/[!I]*.dat  # excludes files starting with INACTIVE (or any capital I)
    do
      AREA=$(echo ${AREA_FORMAT} | rev | cut -d/ -f1 | rev | xargs echo) # cut out the area name (last field, so reverse)
      # Check if the downloaded files pertain to tracks we are interested in
      TRACKS=$(cat "${NEW_INSAR_FILES_FILE}" \
        | cut -d/ -f7 \
        | sort -u \
        | grep -F -f ${CAROLINE}/area-track-lists/${AREA})

      # If we found new files for tracks we are interested in
      if [ ! -z "${TRACKS}" ]; then

        if [ ! -f ${CAROLINE}/caroline_v1.0/run_files/timestamp_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt ]; then
          # get the formatted timestamps for the email
          ALL_TIMESTAMPS=""
          for TRACK in ${TRACKS}
          do
            LAST_EPOCH=$(grep ${TRACK} ${NEW_INSAR_FILES_FILE} | cut -d/ -f9 | sort -u | tail -1)
            EPOCH_TIME=$(grep ${TRACK} ${NEW_INSAR_FILES_FILE} | grep ${LAST_EPOCH} | cut -d/ -f10 | sort -u | head -1 | cut -d_ -f6 | cut -dT -f2 | rev | cut -c 3- | rev | xargs echo)
            FMT_TIME=$(echo ${EPOCH_TIME} | rev | cut -c 3- | rev)":"$(echo ${EPOCH_TIME} | cut -c 3-)"UTC"
            TIMESTAMP=${LAST_EPOCH}"T"${FMT_TIME}
            ALL_TIMESTAMPS=${ALL_TIMESTAMPS}${TIMESTAMP}","
          done

          ALL_TIMESTAMPS=$(echo ${ALL_TIMESTAMPS} | rev | cut -c 2- | rev)
          echo ${ALL_TIMESTAMPS} > ${CAROLINE}/caroline_v1.0/run_files/timestamp_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt
        fi

        # Check if the job has not already been submitted --> job_id_AREA_TS.txt must not exist
        if [ ! -f ${CAROLINE}/caroline_v1.0/run_files/job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt ]; then
          # Check if there is a dependency. If Dependency: None / Dependency: none / Dependency: /
          # no Dependency line in the AREA file, there is no dependency and we continue normally
          DEPENDENCY=$(grep "Dependency" ${CAROLINE}/area-track-lists/${AREA} | cut -d: -f2 | xargs echo)
          if [[ ${DEPENDENCY} = "None" || ${DEPENDENCY} = "none" || -z ${DEPENDENCY} ]]; then

            # Convert tracks list into csv
            TRACKS_CSV=$(echo ${TRACKS} | tr ' ' ',')

            # Submit the job to the cluster's scheduler (slurm) with the correct parameter file determined by the AREA name
            sbatch ./Caroline_v1_0.sh \
              --config-file param_file_Caroline_v1_0_spider_$(echo ${AREA} | cut -d. -f1).txt \
              --tracks "${TRACKS_CSV}" > job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt
            echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) submitted Caroline_v1_0.sh (AoI $(echo ${AREA} | cut -d. -f1), tracks ${TRACKS_CSV}) with slurm-ID $(cat  job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt | cut -d" " -f4 | xargs echo)" >> ${CAROLINE_WORK}/submitted_jobs.log

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

                # Submit the job to the cluster's scheduler (slurm) with the correct parameter file determined by the AREA name
                # with the dependency job id, and the argument that it will be killed if the dependency is invalid
                # (i.e., the process it depended on failed for whatever reason)
                sbatch --dependency=afterok:${DEPENDENCY_JOB_ID} --kill-on-invalid-dep=yes ./Caroline_v1_0.sh \
                  --config-file param_file_Caroline_v1_0_spider_$(echo ${AREA} | cut -d. -f1).txt \
                  --tracks "${TRACKS_CSV}" > job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt
                echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) submitted Caroline_v1_0.sh (AoI $(echo ${AREA} | cut -d. -f1), tracks ${TRACKS_CSV}) with slurm-ID $(cat job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt | cut -d" " -f4 | xargs echo) as dependency to slurm-ID ${DEPENDENCY_JOB_ID}" >> ${CAROLINE_WORK}/submitted_jobs.log

              else
                # it has not been submitted, we need another while loop iteration
                ALL_DEPENDENCIES_SUBMITTED=0
              fi

            else
              # Invalid dependency --> just submit the job and send a warning email to Simon
              echo "Job "${AREA}" submitted with invalid dependency "${DEPENDENCY}", continuing without dependency." | mailx -s "CAROLINE Invalid job dependency" s.a.n.vandiepen@tudelft.nl

              # Convert tracks list into csv
              TRACKS_CSV=$(echo ${TRACKS} | tr ' ' ',')

              # Submit the job to the cluster's scheduler (slurm) with the correct parameter file determined by the AREA name
              sbatch ./Caroline_v1_0.sh \
                --config-file param_file_Caroline_v1_0_spider_$(echo ${AREA} | cut -d. -f1).txt \
                --tracks "${TRACKS_CSV}" > job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt
              echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) submitted Caroline_v1_0.sh (AoI $(echo ${AREA} | cut -d. -f1), tracks ${TRACKS_CSV}) with slurm-ID $(cat job_id_$(echo ${AREA} | cut -d. -f1)_${RUN_TS}.txt | cut -d" " -f4 | xargs echo)" >> ${CAROLINE_WORK}/submitted_jobs.log

            fi
          fi
        fi
      fi
    done
  done
fi

# Check for straggling portal uploads that didn't upload because of the reset at 1am UTC on Thursday (only once,
# so effectively once every 5 hours). Note that runs in this run are ignored as the portal files have not yet been
# generated
cd ${CAROLINE}/caroline_v1.0/run_files/
squeue > squeue_${RUN_TS}.txt # initialize the squeue file
for straggling_job in `ls portal_*`
do
  if [ $(cat ${straggling_job}) -eq 1 ]; then
    # if the portal upload file is 1, there was an upload that has not been pushed to a portal yet.
    # However, we need to first check two things: 1) if the original run-caroline is no longer running (otherwise
    # that run will handle the upload 2) if the job is finished
    JOB=$(echo ${straggling_job} | cut -d_ -f2-)
    TIMESTAMP=$(echo ${JOB} | rev | cut -d_ -f1 | rev | cut -d. -f1)
    LAST_UPDATE=`date -r squeue_${TIMESTAMP}.txt`
    NOW=`date`
    DELTAT=$(($(date -d "${NOW}" +%s) - $(date -d "${LAST_UPDATE}" +%s)))  # in seconds
    # if DELTAT is larger than 5 minutes (300 seconds), the original run-caroline is no longer running
    if [ ${DELTAT} -gt 300 ]; then
      SLURM_ID=$(cat ${JOB} | cut -d" " -f4 | xargs echo)
      FINISHED=$(grep "${SLURM_ID}" squeue_${RUN_TS}.txt)
      # if FINISHED did not find the job ID (it finds only 1 character), then the job is done
      if [ "$(echo ${FINISHED} | wc -c)" -eq "1" ]; then
        # Check if the job ever started by checking if the slurm output is there
        if [ ! -f slurm-${SLURM_ID}.out ]; then
          # the output is not there, so the job never started and is gone. Just turn the portal output to 0
          echo "0" > ${straggling_job}
        else
          if [ -f "${HOME}/.keychain/${HOSTNAME}-sh" ]; then  # if the SSH key is available
            # get the auxiliary directory, then get the Skygeo viewer and depsi directory and upload
            AUX_DIR=$(grep "Running with config file" slurm-${SLURM_ID}.out | cut -d" " -f5 | cut -d/ -f1)
            DEPSI_DIR=`cat ${AUX_DIR}/depsi_directory.txt`
            SKYGEO_VIEWER=`cat ${AUX_DIR}/skygeo_viewer.txt`
            cd ${DEPSI_DIR}
            for dir in `cat ${CAROLINE}/caroline_v1.0/run_files/${AUX_DIR}/loop_directories_depsi.txt`
            do
              cd ${dir}/psi
              echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) initiated portal push of straggling job to portal ${SKYGEO_VIEWER}" >> ${CAROLINE_WORK}/submitted_jobs.log
              upload-result-csv-to-skygeo.sh ${SKYGEO_VIEWER}
              echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) finished portal push of straggling job to portal ${SKYGEO_VIEWER}" >> ${CAROLINE_WORK}/submitted_jobs.log
              cd ${DEPSI_DIR}
            done
            cd ${CAROLINE}/caroline_v1.0/run_files/
            echo "0" > ${straggling_job}
          fi
        fi
      fi
    fi
  fi
done

# Check if all runs are finished
ALL_RUNS_FINISHED=0
cd ${CAROLINE}/caroline_v1.0/run_files/
ls job_id_*${RUN_TS}.txt > submitted_jobs_${RUN_TS}.txt

if [ "$(cat submitted_jobs_${RUN_TS}.txt | wc -c)" -gt "0" ]; then
  # setup check if we should submit something to the portal, and if so if it already has been done
  for job in `cat submitted_jobs_${RUN_TS}.txt`
  do
    PARAM_FILE="param_file_Caroline_v1_0_spider_$(echo ${job} | cut -c 8- | sed -r 's/.{20}$//').txt"
    DO_DP=$(grep "do_depsi_post" ${PARAM_FILE} | cut -d= -f2 | cut -d# -f1 | xargs echo)
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
      if [ `cat portal_${run}` -eq 1 ]; then
        JOB_ID=$(cat ${run} | cut -d" " -f4 | xargs echo)
        FINISHED=$(grep "${JOB_ID}" squeue_${RUN_TS}.txt)
        if [ "$(echo ${FINISHED} | wc -c)" -gt "1" ]; then
          ALL_RUNS_FINISHED=0
        else
          if [ -f "${HOME}/.keychain/${HOSTNAME}-sh" ]; then  # if the SSH key is available
            # set to 0 so we only upload once
            echo "0" > portal_${run}
            # retrieve the directories we need to upload
            AUX_DIR=$(grep "Running with config file" slurm-${JOB_ID}.out | cut -d" " -f5 | cut -d/ -f1)
            DEPSI_DIR=`cat ${AUX_DIR}/depsi_directory.txt`
            SKYGEO_VIEWER=`cat ${AUX_DIR}/skygeo_viewer.txt`
            cd ${DEPSI_DIR}
            for dir in `cat ${CAROLINE}/caroline_v1.0/run_files/${AUX_DIR}/loop_directories_depsi.txt`
            do
              cd ${dir}/psi
              echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) initiated portal push to portal ${SKYGEO_VIEWER}" >> ${CAROLINE_WORK}/submitted_jobs.log
              upload-result-csv-to-skygeo.sh ${SKYGEO_VIEWER}
              echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) finished portal push to portal ${SKYGEO_VIEWER}" >> ${CAROLINE_WORK}/submitted_jobs.log
              cd ${DEPSI_DIR}
            done
            cd ${CAROLINE}/caroline_v1.0/run_files/
          fi
        fi
      fi
    done
    if [ ${ALL_RUNS_FINISHED} -eq "0" ]; then
      echo "Not all runs finished yet, sleeping..."
      sleep 60
    fi
  done
fi
