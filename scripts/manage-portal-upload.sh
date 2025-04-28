#!/bin/bash

# This script manages the portal upload

# Figure out where we are installed
CAROLINE=$(readlink -f $(dirname $BASH_SOURCE) | sed -e 's+/scripts$++')

# Load required python and gdal modules in case of submissions
source /etc/profile.d/modules.sh
source /project/caroline/Software/bin/init.sh
module load python/3.10.4 gdal/3.4.1-alma9
source ~/.bashrc
#
# Load required python environment with gdal
VENV_LOCATION=$(python3 ${CAROLINE}/caroline/config.py "CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY")
source ${VENV_LOCATION}/bin/activate

# Find the portal upload flag directory, work directory and sendmail directory
PORTAL_UPLOAD=$(python3 ${CAROLINE}/caroline/config.py "PORTAL_UPLOAD_FLAG_DIRECTORY")
CAROLINE_WORK=$(python3 ${CAROLINE}/caroline/config.py "CAROLINE_WORK_DIRECTORY")
SENDMAIL=$(python3 ${CAROLINE}/caroline/config.py "SENDMAIL_EXECUTABLE")

# loop over all the files there
for upload_file in `ls ${PORTAL_UPLOAD}/*`
do
  STATUS=$(grep "Status: " ${upload_file} | cut -d: -f2 | xargs echo)
  if [ "${STATUS}" = "TBD" ]; then
    # it still needs to be done, so we start the upload
    # first read the other parameters
    DEPSI_DIR=$(grep "Directory: " ${upload_file} | cut -d: -f2 | xargs echo)
    SKYGEO_VIEWER=$(grep "Viewer: " ${upload_file} | cut -d: -f2 | xargs echo)
    SKYGEO_CUSTOMER=$(grep "Customer: " ${upload_file} | cut -d: -f2 | xargs echo)

    # check if the SSH agent is active
    if [ -f "${HOME}/.keychain/${HOSTNAME}-sh" ]; then

      # overwrite the upload so that it is only uploaded once
      echo "Status: In Progress
Directory: ${DEPSI_DIR}
Viewer: ${SKYGEO_VIEWER}
Customer: ${SKYGEO_CUSTOMER}" > ${upload_file}

      # go to the DePSI directory
      cd ${DEPSI_DIR}

      # and upload
      echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) initiated portal push to portal ${SKYGEO_VIEWER}" >> ${CAROLINE_WORK}/submitted_jobs.log
      ${CAROLINE}/scripts/upload-result-csv-to-skygeo.sh ${SKYGEO_VIEWER} ${SKYGEO_CUSTOMER}
      echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) finished portal push to portal ${SKYGEO_VIEWER}" >> ${CAROLINE_WORK}/submitted_jobs.log

      # overwrite the upload so that it is only uploaded once
      echo "Status: Finished
Directory: ${DEPSI_DIR}
Viewer: ${SKYGEO_VIEWER}
Customer: ${SKYGEO_CUSTOMER}" > ${upload_file}
    else
      # The SSH key is not present, so send an email and exit
      echo "Subject: CAROLINE SSH Key missing (${upload_file})
from:noreply@surf.nl

Hello admins,

CAROLINE tried to push run ${upload_file} to the portal, but it failed since the SSH key is missing.
Can one of you add the SSH key on ui-01?

Kind regards,
The CAROLINE system" | ${SENDMAIL} s.a.n.vandiepen@tudelft.nl,f.j.vanleijen@tudelft.nl,n.h.jansen@tudelft.nl
      exit 1
    fi
  fi
done
