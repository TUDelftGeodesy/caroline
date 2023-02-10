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

# If the output file with downloaded files has more than 0 bytes, that means new files
# have been downloaded
if [ -s "${NEW_INSAR_FILES_FILE}" ]; then
	# Check if the downloaded files pertain to tracks we are interested in
	TRACKS=$(cat new-insar-files-${RUN_TS}.out \
		| cut -d/ -f7 \
		| sort -u \
		| grep -F -f ${CAROLINE}/area-track-lists/veenwijden.dat)
	echo $TRACKS
fi
