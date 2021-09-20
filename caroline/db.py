import logging
import psycopg2
from caroline.config import config_db

class Database:

    def __init__(self):
        self.connection = self.connect()
        self.cursor = self.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def connect(self):
        try:
            params = config_db()
            return psycopg2.connect(**params)
        except (Exception, psycopg2.DatabaseError) as error:
            logging.exception(error)

    def cursor(self):
        try:
            return self.connection.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            logging.exception(error)

    def db_version(self):
        self.cursor.execute('SELECT version()')
        return self.cursor.fetchone()[0]

    def postgis_version(self):
        self.cursor.execute('SELECT PostGIS_Version()')
        return self.cursor.fetchone()[0]

    def postgis_full_version(self):
        self.cursor.execute('SELECT PostGIS_Full_Version()')
        return self.cursor.fetchone()[0]

    def postgis_geos_version(self):
        self.cursor.execute('SELECT PostGIS_GEOS_Version()')
        return self.cursor.fetchone()[0]

    def postgis_lib_version(self):
        self.cursor.execute('SELECT PostGIS_Lib_Version()')
        return self.cursor.fetchone()[0]

    def postgis_libxml_version(self):
        self.cursor.execute('SELECT PostGIS_LibXML_Version()')
        return self.cursor.fetchone()[0]

    def postgis_proj_version(self):
        self.cursor.execute('SELECT PostGIS_PROJ_Version()')
        return self.cursor.fetchone()[0]
