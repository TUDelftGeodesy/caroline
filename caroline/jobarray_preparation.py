"""All functions in this file aim at figuring out how many jobs are necessary for a job array submission."""

import os

from caroline.config import get_config
from caroline.io import read_parameter_file, write_run_file
from caroline.utils import format_process_folder

CONFIG_PARAMETERS = get_config()
JOB_DEFINITIONS = get_config(
    f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False
)["jobs"]


def jobarray_preparation_scheduler_hook(parameter_file: str, njobs_function: str) -> int:
    """Allow the scheduler to access all functions in this file via job-definitions.yaml without ruff complaining.

    This function acts as a hook for the scheduler in `scheduler.py`. Its purpose is to be called by the scheduler with
    two arguments: the parameter file that is being scheduled, and the name of one of the functions in this file, which
    it has read from `config/job_definitions.yaml` (the `job-array:njobs-in-array-function` key). This function will
    evaluate which function it is, call that function with the parameter file argument, and return the results. This
    way all functions in this file are accessible to the scheduler without having to modify the scheduler when a new
    job requiring array computation is added to Caroline.

    Parameters
    ----------
    parameter_file: str
        Full path to the parameter file
    njobs_function: str
        Name of the function to be called, which needs to exist in this file.

    Returns
    -------
     int
        The number of jobs necessary for the array
    """
    return eval(f"{njobs_function}({parameter_file})")


def njobs_snap_run(parameter_file: str) -> int:
    """Figure out how many jobs are necessary in the array to successfully run the job run_snap.

    Parameters
    ----------
    parameter_file: str
        Full path to the parameter file

    Returns
    -------
    int
        The number of jobs necessary for the array
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)
    if len(out_parameters["general:tracks:track"]) > 1:
        raise ValueError(f"Expected single track, got {out_parameters['general:tracks:track']}!")

    track_fmt = (
        f"{out_parameters['general:input-data:sensor'].lower()}_{out_parameters['general:tracks:asc_dsc']}_"
        f"{out_parameters['general:tracks:track']}"
    )

    snap_directory = format_process_folder(
        parameter_file=parameter_file,
        job_description=JOB_DEFINITIONS["snap_preparation"],
        track=out_parameters["general:tracks:track"][0],
    )

    write_run_file(
        save_path=f"{CONFIG_PARAMETERS['TEMPORARY_STORAGE_DIRECTORY']}/njobs_run_snap.sh",
        template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/snap/generate-snap-graphs.sh",
        asc_dsc=out_parameters["general:tracks:asc_dsc"][0],
        track=out_parameters["general:tracks:track"][0],
        parameter_file=parameter_file,
        parameter_file_parameters=[
            "snap:general:AoI-name",
            "general:timeframe:mother",
            "general:timeframe:start",
            "general:timeframe:end",
        ],
        config_parameters=[
            "caroline_work_directory",
            "caroline_virtual_environment_directory",
            "caroline_install_directory",
            "slc_base_directory",
        ],
        other_parameters={
            "track": out_parameters["general:tracks:track"][0],
            "snap-output-path": snap_directory,
            "dry_run": "1",
            "track_formatted": track_fmt,
        },
    )

    njobs = os.popen(
        f"cd {CONFIG_PARAMETERS['TEMPORARY_STORAGE_DIRECTORY']}; " "bash njobs_run_snap.sh; "
        # "rm -rf njobs_run_snap.sh"
    ).read()

    return int(njobs)
