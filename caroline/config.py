import os


def config_db():
    """Return the environment variables for the database."""
    return {
        "host": os.environ.get("CAROLINE_DB_HOST"),
        "database": os.environ.get("CAROLINE_DB_NAME"),
        "user": os.environ.get("CAROLINE_DB_USER"),
        "password": os.environ.get("CAROLINE_DB_PASSWORD"),
    }
