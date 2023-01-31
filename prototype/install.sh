#!/bin/bash
#
# install-caroline-prototype.sh

CAROLINE_HOME='/project/caroline/Software/caroline-prototype'

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

cp -Rvp caroline/caroline_main/caroline_v0.2/ "${CAROLINE_HOME}"

# Eof
