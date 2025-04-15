import os
import sys

import yaml


def config_db():
    """Return the environment variables for the database."""
    return {
        "host": os.environ.get("CAROLINE_DB_HOST"),
        "database": os.environ.get("CAROLINE_DB_NAME"),
        "user": os.environ.get("CAROLINE_DB_USER"),
        "password": os.environ.get("CAROLINE_DB_PASSWORD"),
    }


def get_config(config_file: str | None = None, flatten: bool = True) -> dict:
    """Retrieve the path configurations for the CAROLINE environment.

    Parameters
    ----------
    config_file: str | None (optional)
        Full path to the configuration yaml file to read the files from. If `None`, the configuration file is
        assumed to be `config/installation-config.yaml`.
    flatten: bool (optional)
        Whether the configuration should be returned in its original tree format (False) or flattened (True, default)

    Returns
    -------
    dict
        Dictionary with as arguments the path configurations, as values the paths.

    """
    if config_file is None:
        cwd = os.getcwd()
        config_file = f"{cwd}/../config/installation-config.yaml"

    assert config_file.split(".")[-1] == "yaml", f"Expected a .yaml configuration file, got {config_file}!"

    with open(config_file) as f:
        paths = yaml.safe_load(f)

    if not flatten:
        return paths

    # otherwise, flatten the yaml
    flattened_paths = {}
    for key in paths.keys():
        for subkey in paths[key].keys():
            flattened_paths[subkey] = paths[key][subkey]

    return flattened_paths


if __name__ == "__main__":
    _, requested_parameter = sys.argv
    print(get_config()[requested_parameter])
