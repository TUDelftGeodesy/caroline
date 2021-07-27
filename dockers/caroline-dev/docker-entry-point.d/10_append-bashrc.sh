#!/bin/bash

# Append settings to caroline's bashrc to make life easier

set -e

cat >> /home/caroline/.bashrc <<EOF

# Added by ${0}
export PGHOST="${CAROLINE_DB_HOST}"
export PATH="/home/caroline/.local/bin:${PATH}"
# End ${0} additions
EOF

# Eof
