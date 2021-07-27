#!/bin/bash

# Entry point script for caroline docker

set -e

# Execute entry point scripts
for SCRIPT in /docker-entry-point.d/*; do
	[[ -x "${SCRIPT}" ]] && "${SCRIPT}"
done

# Fire up systemd so we have a daemon that wil keep the container running
exec /lib/systemd/systemd

# Eof
