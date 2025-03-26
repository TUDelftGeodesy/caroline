import os


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
        "CAROLINE_WORK_DIRECTORY": "/project/caroline/Software/run/caroline/work",
        "SLC_BASE_DIRECTORY": "/project/caroline/Data/radar_data/sentinel1",
        "ORBIT_DIRECTORY": "/project/caroline/Data/orbits",
        "CAROLINE_INSTALL_DIRECTORY": "/project/caroline/Software/caroline",
        "CAROLINE_WATER_MASK_DIRECTORY": "/project/caroline/Software/config/caroline-water-masks",
        "FROZEN_PARAMETER_FILE_DIRECTORY": "/project/caroline/Software/run/caroline",
        "SLURM_OUTPUT_DIRECTORY": "/project/caroline/Software/run/caroline/slurm-output",
        "PORTAL_UPLOAD_FLAG_DIRECTORY": "/project/caroline/Software/run/caroline/portal-upload-flags",
        "SENDMAIl_DIRECTORY": "/usr/sbin/sendmail",
    }
