#!/bin/bash
#
# install-caroline-prototype.sh

RUNNING=`squeue --user caroline-admin | grep "reslc.sh" | wc -c`
if [ ${RUNNING} -gt "0" ]; then
  echo "ERROR: A CAROLINE SCRIPT IS STILL RUNNING RE-SLC. INSTALLING NOW WILL BREAK THIS RUN. ABORTING..."
  exit 127
fi

CAROLINE='/project/caroline/Software/caroline-prototype'
CAROLINE_PLUGINS_ARCHIVE_DIR='/project/caroline/Software/archives/caroline_plugins'

if [ -d "$CAROLINE" ]; then
	BACKUP_DIR="${CAROLINE}-$(date +%Y%m%dT%H%M%S)"
	echo "Creating backup of existing Caroline prototype directory"
	if [ -d "${BACKUP_DIR}" ]; then
		echo 'ERROR: Backup directory already exists. This should not happen' >&2
		echo 'Aborting. >&2'
		exit 1
	fi
	mv -v "${CAROLINE}" "${BACKUP_DIR}"
fi

if [ ! -d "${CAROLINE}" ]; then
	echo "Creating Caroline prototype directory"
	mkdir -pv "${CAROLINE}"
fi

# Install caroline prototype
cp -Rvp caroline/caroline_main/caroline_v1.0/ "${CAROLINE}"
cp -Rvp caroline/caroline_main/caroline_v0.2/ "${CAROLINE}"
cp -Rvp caroline/caroline_main/bin/ "${CAROLINE}"
cp -Rvp caroline/caroline_main/area-track-lists/ "${CAROLINE}"

# Install plugins
mkdir -p "${CAROLINE}/plugins"

tar -xzf "${CAROLINE_PLUGINS_ARCHIVE_DIR}/cpxfiddle.tar.gz" -C "${CAROLINE}/plugins"
tar -xzf "${CAROLINE_PLUGINS_ARCHIVE_DIR}/depsi_v2.2.1.1.tar.gz" -C "${CAROLINE}/plugins"
git clone -b v2.1.4.0 git@bitbucket.org:grsradartudelft/depsipost.git "${CAROLINE}/plugins/depsi_post_v2.1.4.0"
git clone -b v0.3.4 git@bitbucket.org:grsradartudelft/deinsar.git "${CAROLINE}/plugins/deinsar_v0.3.4"
git clone -b caroline-clone-branch git@github.com:TUDelftGeodesy/DePSI_group.git "${CAROLINE}/plugins/DePSI_group"
# git clone git@github.com:MotionbyLearning/PyDePSI.git "${CAROLINE}/plugins/pydepsi" # Replaced by #10
tar -xzf "${CAROLINE_PLUGINS_ARCHIVE_DIR}/geocoding_v0.9.tar.gz" -C "${CAROLINE}/plugins"
tar -xzf "${CAROLINE_PLUGINS_ARCHIVE_DIR}/rdnaptrans.tar.gz" -C "${CAROLINE}/plugins"

# Apply patch for depsi and depsi-post
cp "${CAROLINE_PLUGINS_ARCHIVE_DIR}/patches/depsi_v2.2.1.1/main/ps_read_process_directory.m" \
	"${CAROLINE}/plugins/depsi_v2.2.1.1/main/"
cp "${CAROLINE_PLUGINS_ARCHIVE_DIR}/patches/depsi_v2.2.1.1/main/ps_calibration.m" \
	"${CAROLINE}/plugins/depsi_v2.2.1.1/main/"
cp "${CAROLINE_PLUGINS_ARCHIVE_DIR}/patches/depsi_post_v2.1.4.0/main/ps_post_write_shape_csv.m" \
  "${CAROLINE}/plugins/depsi_post_v2.1.4.0/main/"

# Install find-new-insar-files.sh
cp -Rvp ../scripts/find-new-insar-files.sh "${CAROLINE}/bin"

# Create work directory
mkdir -pv "${CAROLINE}/work"
cp -Rvp "${BACKUP_DIR}/work/force-start-runs.dat" "${CAROLINE}/work/"

# Copy run_files to run directory
cp -Rvp "${CAROLINE}/caroline_v1.0/run_files"/* "/project/caroline/Software/run/caroline/"

# Eof
