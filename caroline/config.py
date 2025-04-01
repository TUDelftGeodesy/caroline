import os
import sys


def config_db():
    """Return the environment variables for the database."""
    return {
        "host": os.environ.get("CAROLINE_DB_HOST"),
        "database": os.environ.get("CAROLINE_DB_NAME"),
        "user": os.environ.get("CAROLINE_DB_USER"),
        "password": os.environ.get("CAROLINE_DB_PASSWORD"),
    }


def get_config():
    """Return the path configurations for the CAROLINE environment."""
    return {
        "AOI_OVERVIEW_DIRECTORY": "/project/caroline/Share/caroline-aoi-extents",
        "CAROLINE_INSTALL_DIRECTORY": "/project/caroline/Software/caroline",
        "CAROLINE_PLUGINS_ARCHIVE_DIRECTORY": "/project/caroline/Software/archives/caroline_plugins",
        "CAROLINE_PLUGINS_DIRECTORY": "/project/caroline/Software/caroline-plugins",
        "CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY": "/project/caroline/Software/venv/caroline",
        "CAROLINE_WATER_MASK_DIRECTORY": "/project/caroline/Software/config/caroline-water-masks",
        "CAROLINE_WORK_DIRECTORY": "/project/caroline/Software/run/caroline/work",
        "FROZEN_PARAMETER_FILE_DIRECTORY": "/project/caroline/Software/run/caroline/frozen-parameter-files",
        "PORTAL_UPLOAD_FLAG_DIRECTORY": "/project/caroline/Software/run/caroline/portal-upload-flags",
        "ORBIT_DIRECTORY": "/project/caroline/Data/orbits",
        "SENDMAIl_DIRECTORY": "/usr/sbin/sendmail",
        "SLC_BASE_DIRECTORY": "/project/caroline/Data/radar_data/sentinel1",
        "SLURM_OUTPUT_DIRECTORY": "/project/caroline/Software/run/caroline/slurm-output",
    }


if __name__ == "__main__":
    _, requested_parameter = sys.argv
    print(get_config()[requested_parameter])
