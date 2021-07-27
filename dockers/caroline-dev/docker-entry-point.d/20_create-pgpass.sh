#!/bin/bash

# Set up .pgpass for caroline user for easy database access

touch /home/caroline/.pgpass
chmod 600 /home/caroline/.pgpass
chown caroline: /home/caroline/.pgpass
echo "${CAROLINE_DB_HOST}:5432:${CAROLINE_DB_NAME}:${CAROLINE_DB_USER}:${CAROLINE_DB_PASSWORD}" > /home/caroline/.pgpass
