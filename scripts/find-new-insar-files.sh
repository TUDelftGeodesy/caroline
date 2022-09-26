#!/bin/bash

# find-new-insar-files.sh
#
# Author: Niels Jansen <n.h.jansen@tudelft.nl>
#
# This script is meant to run periodically. It checks if new InSAR files have
# been downloaded in SCAN_DIR since the last time new files were found.
#
# When new files are found they are listed and exit code 0 is returned. When
# no files have been found, this is reported and exit code 1 is returned. This
# way this script can be used as a test like so:
#
# if find-new-insar-files.sh; then
#     echo "Start processing"
# fi

SCAN_DIR='/project/caroline/Data/radar_data/sentinel1'
ORBIT_DIR='/project/caroline/Data/orbits/sentinel1/restituted'
TIMESTAMP_FILE="/project/caroline/Share/users/${USER}/run/find-new-insar-files-timestamp"

main () {
	local NEW_DOWNLOADS=()
	local OPTIONS=''
	local NEW_TIMESTAMP=''

	# Parse commandline arguments with getopt
	OPTIONS=$(getopt -o hr: --long help,reset-timestamp: -- "$@")
	[ $? -eq 0 ] || {
		print_usage
		exit 1
	}
	eval set -- "${OPTIONS}"
	while true; do
		case "$1" in
			-h|--help)
				print_usage
				exit
				;;
			-r|--reset-timestamp)
				shift;
				NEW_TIMESTAMP="${1}"
				;;
			--)
				shift
				break
		esac
		shift
	done

	#
	# Process options
	#
	# Reset timestamp if --reset-timestamp option is given
	if [ ! -z "${NEW_TIMESTAMP}" ]; then
		reset_timestamp "${NEW_TIMESTAMP}"
		exit
	fi

	# Create a timestamp file if it is not there yet
	if [ ! -f "${TIMESTAMP_FILE}" ]; then
		mkdir -p $(dirname ${TIMESTAMP_FILE})
		touch "${TIMESTAMP_FILE}"
	fi
	
	# - Find download directories in the SCAN_DIR with xml files that are 
	#   newer than the timestamp file.
	# - Check if all files have been downloaded
	# - Check if orbits files have been downloaded for the products
	#   in the download directories
	#
	# If a directory has been found AND all files have been downloaded
	# AND orbit files for the products have been downloaded, append the
	# directory to new_downloads
	for DOWNLOAD_DIR in $(find "${SCAN_DIR}" \
		               -newer "${TIMESTAMP_FILE}" \
			       -name "*.xml" \
			       -exec dirname {} \; | sort -u)
	do
		if is_download_complete "${DOWNLOAD_DIR}"; then
			if orbits_downloaded "${DOWNLOAD_DIR}"; then
				NEW_DOWNLOADS+=("${DOWNLOAD_DIR}")
			fi
		fi
	done
	
	# If new downloads have been found we update the timestamp and print 
	# out the files we found. We return exit code 0 so that if this script
	# is used as a test the test will pass. If no new downloads were found
	# we report this and return exit 1 so that if this script is used as
	# a test the test will fail
	if [ ${#NEW_DOWNLOADS[@]} -gt 0 ]; then
		# Upate the timestamp file
		touch "${TIMESTAMP_FILE}"

		# List the zipfiles we found
		for DOWNLOAD_DIR in ${NEW_DOWNLOADS[@]}; do
			ls "${DOWNLOAD_DIR}"/*.zip
		done

		# Return succes so that if this script is used as a test
		# the test will pass
		exit 0
	else
		# Report that no files have been found
		echo "No new complete downloads found"

		# Return exit code 1 so that if this script is used as a test
		# the test will fail
		exit 1
	fi

}

get_last_orbit_epoch () {
	local SATELLITE_ID="${1}"

	local LAST_ORBIT_TS=$(get_last_orbit_ts ${SATELLITE_ID})
	ts_to_epoch "${LAST_ORBIT_TS}"
}

get_last_orbit_ts () {
	local SATELLITE_ID="${1}"

	local OLD_CWD=$(pwd)

	cd ${ORBIT_DIR}

	for FILE in ${SATELLITE_ID}*.EOF; do
		echo $FILE
	done | sed -e 's/.*_//' | sed -e 's/\.EOF$//' | sort | tail -1
}

# Get the epoch of the last stop timestamp
#
# We can't trust the timestamp of the downloaded file so we
# need to check the actual timestamp in the file name
get_product_last_stop_epoch () {
	local DOWNLOAD_DIR="${1}"

	local LAST_STOP_EPOCH=0

	for PRODUCT_PATH in "${DOWNLOAD_DIR}"/*.zip; do
		PRODUCT_FILE_NAME=$(basename "${PRODUCT_PATH}")
		PRODUCT_STOP_TS=$(echo "${PRODUCT_FILE_NAME}" | cut -d'_' -f 7)
		PRODUCT_STOP_EPOCH=$(ts_to_epoch "${PRODUCT_STOP_TS}")

		if [ ${PRODUCT_STOP_EPOCH} -gt ${LAST_STOP_EPOCH} ]; then
			LAST_STOP_EPOCH="${PRODUCT_STOP_EPOCH}"
		fi
	done

	echo ${LAST_STOP_EPOCH}
}

get_satellite_id () {
	local DOWNLOAD_DIR=${1}

	local SATELLITE_ID=''

	for PRODUCT_PATH in "${DOWNLOAD_DIR}"/*.zip; do
		PRODUCT_FILE_NAME=$(basename "${PRODUCT_PATH}")
		SATELLITE_ID=$(echo "${PRODUCT_FILE_NAME}" | cut -d'_' -f 1)
	done

	echo "${SATELLITE_ID}"
}

# Check if a download is complete
#
# Check we have a zip file for each xml file found
#
is_download_complete () {
	local DOWNLOAD_DIR="${1}"

	# Check every xml file in the download directory for a corresponding
	# zip file
	for XMLFILE in "${DOWNLOAD_DIR}"/*.xml; do
		ZIPFILE="${XMLFILE%.xml}.zip"

		# Check if zip file exists for this xml file. If there is no
		# zip file, the download is not complete so return false
		if [ ! -f "${ZIPFILE}" ]; then
			return 1
		fi

		# Test zipfile integrity with the zipinfo command. If the 
		# test fails we return false because the download is 
		# not complete
		if ! zipinfo -t "${ZIPFILE}" >/dev/null 2>&1; then
			return 1
		fi
	done
	
	# If we end up here we have a xml file for every zip file so return 
	# true
	return 0
}

# Check if orbitfiles have been downloaded for products in a download
# directory
#
# The downloaded orbit files need to cover the 
# need to know if downloaded products are within time range of
# downloaded orbit files for that specific satellite
#
orbits_downloaded () {
	local DOWNLOAD_DIR="${1}"

	# Get last end time for downloaded product
	PRODUCT_LAST_STOP_EPOCH=$(get_product_last_stop_epoch \
					"${DOWNLOAD_DIR}")

	# Get the id of the source satellite
	PRODUCT_SATELLITE_ID=$(get_satellite_id \
					"${DOWNLOAD_DIR}")

	# Get the epoch time of the last orbit data for the satellite
	LAST_SATELLITE_ORBIT_EPOCH=$(get_last_orbit_epoch \
					"${PRODUCT_SATELLITE_ID}")

	# If the timestamp of the last orbit data is lower than the timestamp
	# of the product last end time we do not have enough orbit data to
	# start processing.
	if [ ${LAST_SATELLITE_ORBIT_EPOCH} -lt ${PRODUCT_LAST_STOP_EPOCH} ];
	then
		return 1
	fi

	# Previous test has passed, so we have enough orbit data to start 
	# processing
	return 0
}

print_usage () {
	cat <<-EOF
	usage: find-new-insar-files.sh [-h | --help] [-r | --reset-timestamp]

	This script is meant to run periodically. It checks if new InSAR files have
	been downloaded in SCAN_DIR since the last time new files were found.

	When new files are found they are listed and exit code 0 is returned. When
	no files have been found, this is reported and exit code 1 is returned. This
	way this script can be used as a test like so:

	if find-new-insar-files.sh; then
	    echo "Start processing"
	fi

	options:
	  -h, --help             show this help message and exit
	  -r TIMESTAMP, --reset-timestamp=TIMESTAMP
	                         reset time timestamp file and exit

	TIMESTAMP
	  A time stamp in a format that is acceptible for the touch(1) command,
	  e.g.: "2022-09-01 14:00:00" will reset the timestamp file to a date
	  of September 1st 2022 at 14:00 hrs.

	EXAMPLES
	  Find new images:
	    find-new-insar-files.sh

	  Show help:
	    find-new-insar-files.sh -h

	  Reset timestamp:
	    find-new-insar-files.sh --reset-timestamp="2022-09-01 14:00:00"

	EOF
}

reset_timestamp () {
	local TIMESTAMP="${1}"
	echo "Setting timestamp to '${TIMESTAMP}'"
	if touch --date="${TIMESTAMP}" "${TIMESTAMP_FILE}"; then
		echo "Timestamp updated:"
		ls -l "${TIMESTAMP_FILE}"
	else
		echo "Failed to update timestamp"
		exit 1
	fi
}

# Convert a timestamp to time in epoch
ts_to_epoch () {
	local TS="${1}"
        
	# Get the individual segments from the timestamp string
	local YEAR="${TS:0:4}"
	local MONTH="${TS:4:2}"
	local DAY="${TS:6:2}"
	local HOUR="${TS:9:2}"
	local MIN="${TS:11:2}"
	local SEC="${TS:13:2}"

	# Use the date command to convert the date into epoch and return
	# that value
	date --date="${MONTH}/${DAY}/${YEAR} ${HOUR}:${MIN}:${SEC} UTC" +"%s"
}

# Main
main "$@"

# Eof
