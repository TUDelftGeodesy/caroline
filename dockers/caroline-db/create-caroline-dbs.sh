#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<-EOSQL
    CREATE USER "${CAROLINE_DB_USER}" ENCRYPTED PASSWORD '${CAROLINE_DB_PASSWORD}';
    CREATE DATABASE "${CAROLINE_DB_NAME}" WITH TEMPLATE template_postgis;
    GRANT ALL PRIVILEGES ON DATABASE "${CAROLINE_DB_NAME}" TO "${CAROLINE_DB_NAME}";
EOSQL
