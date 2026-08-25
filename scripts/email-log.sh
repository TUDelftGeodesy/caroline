#!/bin/bash

# Figure out where we are installed
CAROLINE=$(readlink -f $(dirname $BASH_SOURCE) | sed -e 's+/scripts$++')

# Load required python and gdal modules in case of submissions
source ${CAROLINE}/scripts/imports.sh

# Find the work directory
CAROLINE_WORK=$(python3 ${CAROLINE}/caroline/config.py "CAROLINE_WORK_DIRECTORY")
SENDMAIL=$(python3 ${CAROLINE}/caroline/config.py "SENDMAIL_EXECUTABLE")


DATE=$(date -d 'yesterday 12:00' '+%Y-%m-%d')

echo "Subject: CAROLINE log ${DATE}
from:noreply@spider.surfsara.nl

The following CAROLINE processes were logged on ${DATE}:

----------------

$(grep ${DATE} ${CAROLINE_WORK}/submitted_jobs.log | cut -dT -f2-)

----------------" | ${SENDMAIL} s.a.n.vandiepen@tudelft.nl