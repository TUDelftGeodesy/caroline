#!/bin/bash
#
# install-caroline-prototype.sh

CAROLINE_PROTOTYPE_DIR='/project/caroline/Software/caroline-prototype'

if [ -d "$CAROLINE_PROTOTYPE_DIR" ]; then
	BACKUP_DIR="${CAROLINE_PROTOTYPE_DIR}-$(date +%Y%m%dT%H%M%S)"
	echo "Creating backup of exisiting Caroline prototype directory"
	if [ -d "${BACKUP_DIR}" ]; then
		echo 'ERROR: Backup directory already exists. This should not happen' >&2
		echo 'Aborting. >&2'
		exit 1
	fi
	mv -v "${CAROLINE_PROTOTYPE_DIR}" "${BACKUP_DIR}"
fi

if [ ! -d "${CAROLINE_PROTOTYPE_DIR}" ]; then
	echo "Creating Caroline prototype directory"
	mkdir -pv "${CAROLINE_PROTOTYPE_DIR}"
fi

cp -Rvp caroline/caroline_main/caroline_v0.2/ "${CAROLINE_PROTOTYPE_DIR}"

# Eof
