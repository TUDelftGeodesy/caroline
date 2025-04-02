import datetime as dt
import glob
import os
import sys

from config import get_config

CONFIG = get_config()
CURRENT_TIME = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
GITHUB_DEPENDENCIES = {
    "depsi_post_v2.1.4.0": {"repo": "git@bitbucket.org:grsradartudelft/depsipost.git", "branch": "v2.1.4.0"},
    "deinsar_v0.3.4": {"repo": "git@bitbucket.org:grsradartudelft/deinsar.git", "branch": "v0.3.4"},
    "DePSI_group": {"repo": "git@github.com:TUDelftGeodesy/DePSI_group.git", "branch": "caroline-clone-branch"},
}
TARBALL_DEPENDENCIES = {
    "cpxfiddle": f"{CONFIG['CAROLINE_PLUGINS_ARCHIVE_DIRECTORY']}/cpxfiddle.tar.gz",
    "depsi_v2.2.1.1": f"{CONFIG['CAROLINE_PLUGINS_ARCHIVE_DIRECTORY']}/depsi_v2.2.1.1.tar.gz",
    "geocoding_v0.9": f"{CONFIG['CAROLINE_PLUGINS_ARCHIVE_DIRECTORY']}/geocoding_v0.9.tar.gz",
    "rdnaptrans": f"{CONFIG['CAROLINE_PLUGINS_ARCHIVE_DIRECTORY']}/rdnaptrans.tar.gz",
}


def _install_caroline() -> None:
    """Install CAROLINE in the path specified in get_config."""
    os.system('''echo "Starting CAROLINE install on Spider using config.py"''')

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


def _create_config_directories() -> None:
    """Create the configuration directories that do not yet exist."""
    os.system('''echo "Creating directories..."''')
    for key in CONFIG.keys():
        if not os.path.exists(CONFIG[key]):  # necessary since the sendmail path is a file
            os.makedirs(CONFIG[key], exist_ok=True)
    os.system('''echo "Finished creating directories!"''')


def _install_plugins() -> None:
    """Install the CAROLINE plugins."""
    os.system('''echo "Installing the tarball plugins..."''')
    # First the tarball dependencies
    for dependency in TARBALL_DEPENDENCIES.keys():
        os.system(f'''echo "{dependency}..."''')
        if not os.path.exists(f"{CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/{dependency}"):
            os.system(f"tar -xzf {TARBALL_DEPENDENCIES[dependency]} -C {CONFIG['CAROLINE_PLUGINS_DIRECTORY']}")

    os.system('''echo "Installing the Github plugins..."''')
    # then the github repositories
    for dependency in GITHUB_DEPENDENCIES.keys():
        os.system(f'''echo "{dependency}..."''')
        if os.path.exists(f"{CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/{dependency}"):
            # if the path exists, the directory has already been cloned once before. We need to sync with git pull
            # to the right branch. This is one command as we need to change directories
            os.system(
                f"cd {CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/{dependency}; git pull; "
                f"git checkout {GITHUB_DEPENDENCIES[dependency]['branch']}; git pull"
            )
        else:
            # if it does not exist, simply clone the right branch into the plugins directory
            os.system(
                f"git clone -b {GITHUB_DEPENDENCIES[dependency]['branch']} "
                f"{GITHUB_DEPENDENCIES[dependency]['repo']} {CONFIG['CAROLINE_PLUGINS_DIRECTORY']}/{dependency}"
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
        f"pip install {CONFIG['CAROLINE_INSTALL_DIRECTORY']}"
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
    os.system('''echo "Starting Spider installation..."''')

    _, CWD = sys.argv

    _create_config_directories()

    _install_caroline()

    _install_plugins()

    _update_virtualenvironment()

    _update_start_job()

    _initialize_force_start_job()

    os.system('''echo "Finished Spider installation!"''')
