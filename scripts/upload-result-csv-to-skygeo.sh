#!/bin/bash
#
# upload-result-csv-to-skyeo.sh
#
# Upload the result csv file from depsi_post to the webviewer at skygeo. This script
# must be run from the depsi output directory with the viewer as argument
SKYGEO_USER='caroline'
SKYGEO_VIEWER=$1

if [ "$#" -lt 2 ]; then
  SKYGEO_CUSTOMER='caroline'
else
  SKYGEO_CUSTOMER=$2
fi

SKYGEO_SERVER='portal-tud.skygeo.com'
SKYGEO_UPLOAD_PATH='/tmp'
SKYGEO_ARCHIVE='/home/caroline/upload_archive'
#
# Find the json metadata file. This only works if there is just one json file in the dir,
# which currently is the case. We make sure we only get one file in the result by running
# a pipe trough tail.
JSON_FILE=$(ls -rt *.json | tail -1)
#
# The csv file that we need has the same basename as the json metadata file, but with the 
# csv extention.
CSV_FILE="${JSON_FILE%.json}.csv"
#
# Acquisition end time is obtained from the last column in the acquisition_period field
# in the json metadata file. We remove the dashes ('-') by running through tr.
ACQUISITION_END_TIME=$(jq -r '.acquisition_period' "${JSON_FILE}" \
	                  | awk '{print $NF}' \
			  | tr -d '-')
#
# Append the acquisition_end_time to the csv and json files and remove the
# word portal from the file name
CUR_DATE=$(date '+%Y%m%dT%H%M%S')
JSON_FILE_DATED="${JSON_FILE%_portal.json}_${ACQUISITION_END_TIME}_uploaded${CUR_DATE}.json"
CSV_FILE_DATED="${CSV_FILE%_portal.csv}_${ACQUISITION_END_TIME}_uploaded${CUR_DATE}.csv"
mv "${JSON_FILE}" "${JSON_FILE_DATED}"
mv "${CSV_FILE}" "${CSV_FILE_DATED}"
JSON_FILE="${JSON_FILE_DATED}"
CSV_FILE="${CSV_FILE_DATED}"
#
# Load ssh-agent settings for accessing cached credentials
if [ -f "${HOME}/.keychain/${HOSTNAME}-sh" ]; then
	source "${HOME}/.keychain/${HOSTNAME}-sh"
else
	echo "No ssh-agent found" >&2
	exit 1
fi
#
# Upload json and csv to skygeo
rsync -uav "${CSV_FILE}" "${JSON_FILE}" "${SKYGEO_USER}"@"${SKYGEO_SERVER}":"${SKYGEO_UPLOAD_PATH}/"
#
# Change mode of csv file on skygeo server
ssh "${SKYGEO_USER}"@"${SKYGEO_SERVER}" "chmod 644 ${SKYGEO_UPLOAD_PATH}/${JSON_FILE}"
ssh "${SKYGEO_USER}"@"${SKYGEO_SERVER}" "chmod 644 ${SKYGEO_UPLOAD_PATH}/${CSV_FILE}"
#
# Add the csv data to the viewer on skygeo server
#ssh $USER@portal-tud.skygeo.com "pmantud add_viewer_data_layer /tmp/$CSV_BASENAME.csv $CSV_BASENAME $USER $VIEWER"

CUSTOMER=$(ssh "${SKYGEO_USER}"@"${SKYGEO_SERVER}" "ls /var/www/html/portal" | grep ${SKYGEO_CUSTOMER} | xargs echo)
if [ "$(echo ${CUSTOMER} | wc -c)" -eq "0" ]; then  # viewer does not exist
  echo "Cannot find specified customer ${SKYGEO_CUSTOMER}, aborting.."
  exit 1
fi

VIEWER=$(ssh "${SKYGEO_USER}"@"${SKYGEO_SERVER}" "ls /var/www/html/portal/${SKYGEO_CUSTOMER}" | grep ${SKYGEO_VIEWER} | xargs echo)
if [ "$(echo ${VIEWER} | wc -c)" -eq "0" ]; then  # viewer does not exist
  ssh "${SKYGEO_USER}"@"${SKYGEO_SERVER}" "pmantud add_viewer ${SKYGEO_VIEWER} ${SKYGEO_CUSTOMER}"
fi

ssh "${SKYGEO_USER}"@"${SKYGEO_SERVER}" "pmantud add_viewer_data_layer ${SKYGEO_UPLOAD_PATH}/${CSV_FILE} ${CSV_FILE%.csv} ${SKYGEO_CUSTOMER} ${SKYGEO_VIEWER}"

# Cleanup file from /tmp
ssh "${SKYGEO_USER}"@"${SKYGEO_SERVER}" "find ${SKYGEO_UPLOAD_PATH} -user ${SKYGEO_USER} -name \"*uploaded*.csv\" -exec mv {} ${SKYGEO_ARCHIVE} \;"
ssh "${SKYGEO_USER}"@"${SKYGEO_SERVER}" "find ${SKYGEO_UPLOAD_PATH} -user ${SKYGEO_USER} -name \"*uploaded*.json\" -exec mv {} ${SKYGEO_ARCHIVE} \;"
#
#
# Eof
