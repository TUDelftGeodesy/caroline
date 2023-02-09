#!/bin/bash
#
# install-caroline-prototype.sh

CAROLINE_HOME='/project/caroline/Software/caroline-prototype'
CAROLINE_PLUGINS_ARCHIVE_DIR='/project/caroline/Software/archives/caroline_plugins'

if [ -d "$CAROLINE_HOME" ]; then
	BACKUP_DIR="${CAROLINE_HOME}-$(date +%Y%m%dT%H%M%S)"
	echo "Creating backup of exisiting Caroline prototype directory"
	if [ -d "${BACKUP_DIR}" ]; then
		echo 'ERROR: Backup directory already exists. This should not happen' >&2
		echo 'Aborting. >&2'
		exit 1
	fi
	mv -v "${CAROLINE_HOME}" "${BACKUP_DIR}"
fi

if [ ! -d "${CAROLINE_HOME}" ]; then
	echo "Creating Caroline prototype directory"
	mkdir -pv "${CAROLINE_HOME}"
fi

# Install caroline prototype
cp -Rvp caroline/caroline_main/caroline_v0.2/ "${CAROLINE_HOME}"

# Install plugins
mkdir -p "${CAROLINE_HOME}/plugins"

tar -xzf "${CAROLINE_PLUGINS_ARCHIVE_DIR}/cpxfiddle.tar.gz" -C "${CAROLINE_HOME}/plugins"
tar -xzf "${CAROLINE_PLUGINS_ARCHIVE_DIR}/depsi_post_v2.1.2.0.tar.gz" -C "${CAROLINE_HOME}/plugins"
tar -xzf "${CAROLINE_PLUGINS_ARCHIVE_DIR}/depsi_v2.2.1.1.tar.gz" -C "${CAROLINE_HOME}/plugins"
tar -xzf "${CAROLINE_PLUGINS_ARCHIVE_DIR}/geocoding_v0.9.tar.gz" -C "${CAROLINE_HOME}/plugins"
tar -xzf "${CAROLINE_PLUGINS_ARCHIVE_DIR}/rdnaptrans.tar.gz" -C "${CAROLINE_HOME}/plugins"

# Eof
