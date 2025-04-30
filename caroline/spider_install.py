import datetime as dt
import glob
import os
import sys

from config import get_config


def _get_plugins() -> tuple[dict, dict]:
    """Return the GitHub and Tarball plugins."""
    plugins = get_config(f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/config/plugin-definitions.yaml", flatten=False)

    github_plugins = plugins["github"]
    tarball_plugins = plugins["tarball"]
    for plugin in tarball_plugins.keys():
        if "**CAROLINE_PLUGINS_ARCHIVE_DIRECTORY**" in tarball_plugins[plugin]:
            tarball_plugins[plugin] = tarball_plugins[plugin].replace(
                "**CAROLINE_PLUGINS_ARCHIVE_DIRECTORY**", CONFIG["CAROLINE_PLUGINS_ARCHIVE_DIRECTORY"]
            )

    return github_plugins, tarball_plugins


def _install_caroline() -> None:
    """Install CAROLINE in the path specified in get_config."""
    os.system('''echo "Starting CAROLINE install..."''')

    # by copying instead of moving, and then removing the remaining files, the system is still able to query all files
    # at any time, thus not crashing during a new installation. We therefore copy the old one first, the copy the new
    # one over the old one, and finally remove the files that were present in the previous install but no longer should
    # be there (since those do not get overwritten)
    os.system('''echo "Copying previous CAROLINE install..."''')
    if os.path.exists(CONFIG["CAROLINE_INSTALL_DIRECTORY"]):
        # r for recursive, p for preserve timestamp
        os.system(
            f'cp -rp {CONFIG["CAROLINE_INSTALL_DIRECTORY"]} {CONFIG["CAROLINE_INSTALL_DIRECTORY"]}-{CURRENT_TIME}'
        )

    os.system('''echo "Copying new CAROLINE install..."''')
    os.system(f"""cp -rp {CWD}/* {CONFIG["CAROLINE_INSTALL_DIRECTORY"]}/""")

    os.system('''echo "Removing remaining files from previous install..."''')
    # collect all files existing in the directory
    current_files = glob.glob(f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/*", recursive=True)
    current_recursive_files = glob.glob(f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/**", recursive=True)
    current_files.extend(current_recursive_files)

    for file in current_files:
        check_file = file.replace(CONFIG["CAROLINE_INSTALL_DIRECTORY"], CWD)
        if not os.path.exists(check_file):
            os.system(f"rm -rf {file}")

    os.system('''echo "Finished CAROLINE installation!"''')


def _create_config_directories(config_file: str) -> None:
    """Create the configuration directories that do not yet exist.

    Parameters
    ----------
    config_file: str
        Full path to the configuration file that will be used.

    """
    os.system('''echo "Creating directories..."''')

    config_directories = get_config(config_file, flatten=False)["directories"]

    for key in config_directories.keys():
        if not os.path.exists(config_directories[key]):
            if key == "CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY":  # we need to set up the virtual environment instead
                os.system('''echo "Virtual environment does not exist, generating new one..."''')
                venv_name = config_directories[key].split("/")[-1]
                venv_directory = config_directories[key][: -(len(venv_name) + 1)]  # cut off the venv name and last /
                os.makedirs(venv_directory, exist_ok=True)
                os.system(
                    f"cd {venv_directory}; "
                    "source /project/caroline/Software/bin/init.sh; "
                    "module load python/3.10.4; "
                    f"python3 -m venv {venv_name}"
                )
                os.system('''echo "Virtual environment generated!"''')
            else:
                os.makedirs(config_directories[key], exist_ok=True)

    os.system('''echo "Finished creating directories!"''')


def _copy_config_file(config_file: str) -> None:
    """Copy the configuration file into config/installation-config.yaml.

    Parameters
    ----------
    config_file: str
        Full path to the configuration file that will be used.

    """
    os.system('''echo "Copying configuration file..."''')
    os.system(f"""cp -p {config_file} {CONFIG["CAROLINE_INSTALL_DIRECTORY"]}/config/installation-config.yaml""")
    os.system('''echo "Finished copying configuration file!"''')


def _link_default_config_file() -> None:
    """Overwrite the default configuration file in config.py."""
    os.system('''echo "Linking default configuration file..."''')

    f = open(f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/caroline/config.py")
    data = f.read()
    f.close()

    data = data.replace("**CAROLINE_INSTALL_DIRECTORY**", CONFIG["CAROLINE_INSTALL_DIRECTORY"])

    f = open(f"{CONFIG['CAROLINE_INSTALL_DIRECTORY']}/caroline/config.py", "w")
    f.write(data)
    f.close()

    os.system('''echo "Linked default configuration file!"''')


def _install_plugins() -> None:
    """Install the CAROLINE plugins."""
    os.system('''echo "Installing the tarball plugins..."''')
    github_plugins, tarball_plugins = _get_plugins()

    # First the tarball dependencies
    for dependency in tarball_plugins.keys():
        os.system(f'''echo "{dependency}..."''')
        if not os.path.exists(f"{CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/{dependency}"):
            os.system(f"tar -xzf {tarball_plugins[dependency]} -C {CONFIG['CAROLINE_PLUGINS_DIRECTORY']}")

    os.system('''echo "Installing the Github plugins..."''')
    # then the github repositories
    for dependency in github_plugins.keys():
        os.system(f'''echo "{dependency}..."''')
        if os.path.exists(f"{CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/{dependency}"):
            # if the path exists, the directory has already been cloned once before. We need to sync with git pull
            # to the right branch. This is one command as we need to change directories
            if "branch" in github_plugins[dependency].keys():
                os.system(
                    f"cd {CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/{dependency}; git fetch origin; "
                    f"git checkout {github_plugins[dependency]['branch']}; git pull"
                )
            else:  # we're dealing with a tag, so we need to fetch
                os.system(
                    f"cd {CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/{dependency}; git fetch origin; "
                    f"git checkout {github_plugins[dependency]['tag']}"
                )

        else:
            # if it does not exist, simply clone the right branch into the plugins directory
            if "branch" in github_plugins[dependency].keys():
                os.system(
                    f"git clone -b {github_plugins[dependency]['branch']} "
                    f"{github_plugins[dependency]['repo']} {CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/{dependency}"
                )
            else:
                os.system(
                    f"git clone -b {github_plugins[dependency]['tag']} "
                    f"{github_plugins[dependency]['repo']} {CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/{dependency}"
                )

    os.system('''echo "Applying patches to the modules..."''')
    # finally, apply the patches
    os.system(f"""cp -rp {CWD}/patches/* {CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/""")
    os.system('''echo "Finished installing the plugins!"''')


def _update_virtualenvironment() -> None:
    """Update the virtual environment to the current CAROLINE version.

    This function assumes a virtual environment already exists at the location specified in the configuration.
    """
    os.system('''echo "Updating the Virtual environment..."''')
    os.system(
        "source /etc/profile.d/modules.sh; "
        "source /project/caroline/Software/bin/init.sh; "
        "module load python/3.10.4 gdal/3.4.1-alma9; "
        "source ~/.bashrc; "
        f"source {CONFIG['CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY']}/bin/activate; "
        f"pip install {CONFIG['CAROLINE_INSTALL_DIRECTORY']}[plugins]"
    )
    os.system('''echo "Finished updating the virtual environment!"''')


def _update_start_job() -> None:
    """Update the start_job script in the SLURM output location."""
    os.system('''echo "Updating the start_job script..."''')
    os.system(f"cp -p {CONFIG['CAROLINE_INSTALL_DIRECTORY']}/scripts/start_job.sh {CONFIG['SLURM_OUTPUT_DIRECTORY']}/")


def _initialize_force_start_job() -> None:
    """Check if force-start-runs.dat exists."""
    os.system('''echo "Initialising force-start-runs.dat..."''')
    if not os.path.exists(f"{CONFIG['CAROLINE_WORK_DIRECTORY']}/force-start-runs.dat"):
        f = open(f"{CONFIG['CAROLINE_WORK_DIRECTORY']}/force-start-runs.dat", "w")
        f.write("")
        f.close()


if __name__ == "__main__":
    CURRENT_TIME = dt.datetime.now().strftime("%Y%m%dT%H%M%S")

    _, CWD, CONFIGURATION_FILE = sys.argv
    if CONFIGURATION_FILE == "None":
        CONFIGURATION_FILE = f"{CWD}/config/spider-config.yaml"

    os.system(f'''echo "Starting Spider installation using config file {CONFIGURATION_FILE}..."''')

    CONFIG = get_config(CONFIGURATION_FILE)

    _create_config_directories(CONFIGURATION_FILE)

    _install_caroline()

    _copy_config_file(CONFIGURATION_FILE)

    _link_default_config_file()

    _install_plugins()

    _update_virtualenvironment()

    _update_start_job()

    _initialize_force_start_job()

    os.system('''echo "Finished Spider installation!"''')
