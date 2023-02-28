#!/bin/bash
#
# upload-result-csv-to-skyeo.sh
#
# Upload the result csv file from depsi_post to the webviewer at skygeo. This script
# must be run from the depsi output directory.
SKYGEO_USER='caroline'
SKYGEO_VIEWER='nl_amsterdam'
SKYGEO_SERVER='portal-tud.skygeo.com'
SKYGEO_UPLOAD_PATH='/tmp'
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
# Append the acquisition_end_time to the csv and json files
JSON_FILE_DATED="${JSON_FILE%.json}_${ACQUISITION_END_TIME}.json"
CSV_FILE_DATED="${CSV_FILE%.csv}_${ACQUISITION_END_TIME}.csv"
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
ssh "${SKYGEO_USER}"@"${SKYGEO_SERVER}" "chmod 644 ${SKYGEO_UPLOAD_PATH}/${CSV_FILE}"
#
# Add the csv data to the viewer on skygeo server
#ssh $USER@portal-tud.skygeo.com "pmantud add_viewer_data_layer /tmp/$CSV_BASENAME.csv $CSV_BASENAME $USER $VIEWER"
ssh "${SKYGEO_USER}"@"${SKYGEO_SERVER}" "pmantud add_viewer_data_layer ${SKYGEO_UPLOAD_PATH}/${CSV_FILE} ${CSV_FILE%.csv} ${SKYGEO_USER} ${SKYGEO_VIEWER}"
#
# Eof
