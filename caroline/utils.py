import glob
import os
import zipfile
from typing import Literal

import numpy as np

from caroline.config import get_config
from caroline.io import create_shapefile, link_shapefile, read_parameter_file

CONFIG_PARAMETERS = get_config()
EARTH_RADIUS = 6378136  # m


def format_process_folder(
    base_folder: str, AoI_name: str, sensor: str, asc_dsc: Literal["asc", "dsc"], track: int
) -> str:
    """Format a processing folder name based on processing characteristics.

    Parameters
    ----------
    base_folder: str
        base folder in which the process will run
    AoI_name: str
        Name of the process AoI
    sensor: str
        Name of the sensor
    asc_dsc: Literal["asc", "dsc"]
        Whether the track is ascending (asc) or descending (dsc)
    track: int
        Track number

    Returns
    -------
    str
        Absolute path of the processing folder
    """
    return f"{base_folder}/{AoI_name}_{sensor.lower()}_{asc_dsc.lower()}_t{track:0>3d}"


def remove_incomplete_sentinel1_images(parameter_file: str):
    """Identify and remove incomplete Sentinel-1 image downloads to prevent Doris v5 crashing.

    The identified files are printed to a `bad_zips.txt`.

    Parameters
    ----------
    parameter_file: str
        Full path to the parameter file of the processing run where the images are to be filtered

    """
    search_parameters = ["coregistration_directory", "coregistration_AoI_name", "track", "asc_dsc", "sensor"]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    status = []

    for track in range(len(tracks)):
        base_folder = format_process_folder(
            out_parameters["coregistration_directory"],
            out_parameters["coregistration_AoI_name"],
            out_parameters["sensor"],
            asc_dsc[track],
            tracks[track],
        )
        f = open(f"{base_folder}/good_images/zip_files.txt")
        data = f.read().split("\n")
        f.close()

        # check for incomplete downloads by reading through `zip_files.txt`
        # TODO: split this into io.py
        bad_zips = []
        for line in data:
            if line == "":
                continue
            d_ = line.split(" ")
            d = []
            for i in d_:
                if i != "":
                    d.append(i)
            dirr = d[-1]
            size = d[-5]
            if "SLC__1SDV_" in dirr:  # VV/VH dual polarisation
                if eval(size) < 3000000000:
                    bad_zip = dirr.split("/")[0]
                    if bad_zip not in bad_zips:
                        bad_zips.append(bad_zip)
            elif "SLC__1SSV_" in dirr:  # VV polarisation is half the size
                if eval(size) < 1500000000:
                    bad_zip = dirr.split("/")[0]
                    if bad_zip not in bad_zips:
                        bad_zips.append(bad_zip)
            else:
                print(f"Cannot detect polarisation on {dirr}, skipping...")

        # check for directories without zip files, and test if zip files can be opened
        dirs = glob.glob(f"{base_folder}/good_images/2*")
        for dr in dirs:
            files = glob.glob(f"{dr}/*.zip")
            if len(files) == 0:  # no zip files present
                bad_zip = dr.split("/")[-1]
                if bad_zip not in bad_zips:
                    bad_zips.append(bad_zip)
            for file in files:
                try:
                    _ = zipfile.ZipFile(file)
                except zipfile.BadZipFile:  # zip file cannot be opened --> incomplete download
                    status.append(file)
                    bad_zip = dr.split("/")[-1]
                    if bad_zip not in bad_zips:
                        bad_zips.append(bad_zip)

        # save the bad zips, and move the folders from good images to bad images
        f = open(f"{base_folder}/good_images/bad_zips.txt", "w")
        for zipp in bad_zips:
            if zipp.strip() != "":  # since it is possible an empty string appears
                f.write(f"{zipp}\n")
                os.system(f"rm -rf {base_folder}/bad_images/{zipp}")  # in case it already exists, otherwise mv fails
                os.system(f"mv {base_folder}/good_images/{zipp} {base_folder}/bad_images/{zipp}")  # move it
        f.close()

    if len(status) > 0:
        print("Rejected the following ZIP files as incomplete downloads:")
        for i in status:
            print(i)
    else:
        print("Found no incomplete downloads.")


def find_slurm_job_id(parameter_file: str, job: str) -> int:
    """Find the submission ID of a job given a parameter file.

    This will search for the job in submissions-log.csv

    Parameters
    ----------
    parameter_file: str
        Full path to the frozen parameter file
    job: str
        Name of the job

    Returns
    -------
    int
        Job ID number corresponding to the requested parameter file and job

    """
    data = os.popen(
        f"""grep ";{job};{parameter_file.split("/")[-1]};" """
        f"""{CONFIG_PARAMETERS["CAROLINE_WORK_DIRECTORY"]}/submission-log.csv"""
    ).read()
    job_id = data.split(";")[-1].strip()
    return eval(job_id)


def generate_shapefile(parameter_file: str):
    """Generate a shapefile based on a CAROLINE parameter file.

    If `shape_file` is a shapefile, this file will be linked. Otherwise a square is shapefile is generated.

    Parameters
    ----------
    parameter_file: str
        Full path to the parameter file

    """
    search_parameters = ["shape_file"]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    if len(out_parameters["shape_file"]) == 0:
        # no shapefile is generated --> we need a new one
        create_shapefile(parameter_file)
    else:
        link_shapefile(parameter_file)


def _generate_email(parameter_file: str) -> str:
    """Generate the CAROLINE email.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file

    Returns
    -------
    str
        The message that will be emailed.
    """
    jobs = get_config(f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False)

    search_parameters = [
        "track",
        "asc_dsc",
        "skygeo_viewer",
        "skygeo_customer",
        "sensor",
        "project_owner",
        "project_owner_email",
        "project_engineer",
        "project_engineer_email",
        "project_objective",
        "project_notes",
    ]

    out_parameters = read_parameter_file(parameter_file, search_parameters)

    # for appending to the email, we read the entire file anyways
    f = open(parameter_file)
    parameter_file_content = f.read()
    f.close()

    if out_parameters["skygeo_customer"] is None:  # backwards compatibility for #12
        out_parameters["skygeo_customer"] = "caroline"

    # Format the tracks nicely
    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    tracks_formatted = []
    for i in range(len(tracks)):
        tracks_formatted.append(f"{asc_dsc[i]}_t{tracks[i]:0>3d}")

    # the email will send for each track individually
    tracks_formatted = tracks_formatted[0]

    # Extract the run name
    run_id = "_".join(parameter_file.split("/")[-1].split("_")[2:-4])

    # Generate the logs
    log = "==========DEBUG LOGS===========\n\n"

    status_checks = ""
    for job in jobs["jobs"].keys():
        if jobs["jobs"][job]["email"]["include-in-email"]:
            do_key = jobs["jobs"][job]["parameter-file-step-key"]
            job_ran = read_parameter_file(parameter_file, [do_key])[do_key]

            if job_ran == "1":
                # first check the filters
                if jobs["jobs"][job]["filters"] is not None:  # we need to filter on the sensor
                    for key in jobs["jobs"][job]["filters"].keys():
                        value_check = read_parameter_file(parameter_file, [key])[key]
                        if isinstance(jobs["jobs"][job]["filters"][key], str):
                            if value_check.lower() != jobs["jobs"][job]["filters"][key].lower():
                                job_ran = "0"
                        else:  # it's a list, so we check if it exists in the list
                            if value_check.lower() not in [s.lower() for s in jobs["jobs"][job]["filters"][key]]:
                                job_ran = "0"

            if job_ran == "1":  # if it's still 1, it ran
                job_id = find_slurm_job_id(parameter_file, job)

                if jobs["jobs"][job]["bash-file"] is not None:
                    directory = read_parameter_file(
                        parameter_file, [f"{jobs['jobs'][job]['bash-file']['bash-file-base-directory']}_directory"]
                    )[f"{jobs['jobs'][job]['bash-file']['bash-file-base-directory']}_directory"]
                else:
                    directory = CONFIG_PARAMETERS["SLURM_OUTPUT_DIRECTORY"]

                log += f"\n\n-------{job}--------\n\n"

                log += f"---Track {tracks_formatted}---\n\n"

                check = proper_finish_check(parameter_file, job, job_id)

                if check["successful_finish"]:
                    log += "Step finished successfully!\n\n"
                    if job == "portal_upload":
                        status_checks += (
                            "NOTE: it can take a few hours for the results to show up in the portal.\n"
                            + "The DePSI-post results can be accessed at "
                            + "https://caroline.portal-tud.skygeo.com/portal/"
                            + f"{out_parameters['skygeo_customer']}/{out_parameters['skygeo_viewer']} .\n\n"
                        )
                    else:
                        status_checks += f"{job}: {tracks_formatted} finished properly! (located in {directory} )\n\n"
                elif check["successful_start"]:
                    log += "!!! Step did not finish properly!\n\n"
                    status_checks += (
                        f"!!! {job}: {tracks_formatted} did not finish properly! " f"(located in {directory} )\n\n"
                    )
                else:
                    log += "!!! Step did not start properly!\n\n"
                    status_checks += (
                        f"!!! {job}: {tracks_formatted} did not start properly! " f"(located in {directory} )\n\n"
                    )

                if check["status_file"] is not None:
                    log += f"Status file: {check['status_file']}\nSlurm output: {check['slurm_file']}\n\n"

                    f = open(check["status_file"])
                    status = f.read()
                    f.close()
                    log += f"Status file output: \n\n{status}\n\n"
                else:
                    log += f"Slurm output: {check['slurm_file']}\n\n"

    log += "================"

    project_characteristics = f"""Project characteristics:
Owner: {out_parameters['project_owner']} ({out_parameters['project_owner_email']})
Engineer: {out_parameters['project_engineer']} ({out_parameters['project_engineer_email']})
Objective: {out_parameters['project_objective']}
Notes: {out_parameters['project_notes']}
"""

    message = f"""Dear radargroup,
    
A new CAROLINE run has just finished on run {run_id}! 
    
{project_characteristics}
Run characteristics:
Track(s): {tracks_formatted}
Sensor: {out_parameters['sensor']}
    
The following steps were run:
{status_checks}
    
In case of questions, please contact Niels at n.h.jansen@tudelft.nl or Simon at s.a.n.vandiepen@tudelft.nl
    
Kind regards,
The CAROLINE development team,
Freek, Niels, and Simon
    
=======================================
===========DEBUG info==================
=======================================
First logs of the subprocesses, then the parameter file.
=======================================
    
{log}
    
--- PARAMETER FILE: {parameter_file} ---
    
{parameter_file_content}"""

    return message


def proper_finish_check(parameter_file: str, job: str, job_id: int) -> dict:
    """Check if a process started and finished correctly, and supply the relevant parameter files.

    Parameters
    ----------
    parameter_file: str
        full path to the CAROLINE parameter file
    job: str
        which job to check
    job_id: int
        SLURM job ID of the job

    Returns
    -------
    dict
        Dictionary with four fields:
            successful_start: boolean indicating if the job started correctly
            successful_finish: boolean indicating if the job finished correctly
            slurm_file: identified slurm file belonging to the job (None if it doesn't exist)
            status_file: file as defined by `status-file-search-key` in `job-definitions.yaml`. None if it does not
                exist
    """
    status_file = None
    slurm_file = f"{CONFIG_PARAMETERS['SLURM_OUTPUT_DIRECTORY']}/slurm-{job_id}.out"
    successful_finish = True
    successful_start = True

    if not os.path.exists(slurm_file):  # if the slurm file output does not exist, thus the job did not start
        # Return immediately
        successful_start = False
        successful_finish = False
        slurm_file = None

        output = {
            "successful_start": successful_start,
            "successful_finish": successful_finish,
            "slurm_file": slurm_file,
            "status_file": status_file,
        }

        return output

    data = get_config(f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False)[
        "jobs"
    ][job]

    # first find the status file
    if data["email"]["status-file-search-key"] is not None:  # search for the status file
        assert data["bash-file"] is not None, (
            f"Requested status file search for job {job} but there "
            "is no bash file call that could have generated it!"
        )

        # find the directory
        parameters = read_parameter_file(
            parameter_file,
            [
                f"{data['bash-file']['bash-file-base-directory']}_directory",
                f"{data['bash-file']['bash-file-base-directory']}_AoI_name",
                "sensor",
                "track",
                "asc_dsc",
            ],
        )
        track = eval(parameters["track"])[0]  # as there is only one
        asc_dsc = eval(parameters["asc_dsc"])[0]
        base_directory = (
            format_process_folder(
                base_folder=parameters[f"{data['bash-file']['bash-file-base-directory']}_directory"],
                AoI_name=parameters[f"{data['bash-file']['bash-file-base-directory']}_AoI_name"],
                sensor=parameters["sensor"],
                asc_dsc=asc_dsc,
                track=track,
            )
            + data["bash-file"]["bash-file-directory-appendix"]
        )

        dir_file = f"{base_directory}/dir_contents{data['directory-contents-file-appendix-file']}.txt"
        if os.path.exists(dir_file):
            f = open(dir_file)
            contents = f.read().split("\n")
            f.close()

            # Find the status files
            status_files = glob.glob(f"{base_directory}/{data['email']['status-file-search-key']}")
            new_sfs = [sf for sf in list(sorted(list(status_files))) if sf.split("/")[-1] not in contents]

            if len(new_sfs) > 0:  # it started
                status_file = new_sfs[0]

    # we check for the status using the sacct command, which if successful will return exit code 0:0 and status
    # COMPLETED
    job_status = os.popen(f"""sacct --jobs={job_id}""").read().split("\n")[2:]

    for status_line in job_status:
        status_data = status_line.split(" ")  # remove all the spacess
        status_data = [st for st in status_data if st != ""]
        if len(status_data) > 0:  # ignore empty lines
            if status_data[-1] != "0:0":  # wrong exit code
                successful_finish = False
            elif status_data[-2] != "COMPLETED":  # wrong exit message (CANCELLED still returns 0:0 exit code)
                successful_finish = False
            elif status_data[2] == "matlab":  # Matlab can return a zero exit code while still experiencing an error
                # So we need to check for a matlab error in the SLURM output
                f = open(slurm_file)
                slurm_output = f.read()
                f.close()
                if "Error in " in slurm_output:  # this means Matlab has in fact encountered an error
                    successful_finish = False

    output = {
        "successful_start": successful_start,
        "successful_finish": successful_finish,
        "slurm_file": slurm_file,
        "status_file": status_file,
    }

    return output


def _failed_email_generation(error: Exception) -> str:
    """Generate the notification that email generation failed.

    Parameters
    ----------
    error: Exception
        The error that was encountered by `generate_email`

    Returns
    -------
    str
        The message to notify that the email generation failed.
    """
    message = f"""Dear radargroup,

It appears the CAROLINE email generation has encountered an error. Please create an issue on the CAROLINE GitHub project
https://github.com/TUDelftGeodesy/caroline/issues mentioning:
1) that the email generation failed
2) the subject of this mail
3) the following error message:

{error}


Please add the labels Priority-0 and bug, and assign Simon.

Thank you in advance, and sorry for the inconvenience.

Kind regards,
The CAROLINE development team,
Freek, Niels, and Simon

"""
    return message


def generate_email(parameter_file: str) -> str:
    """Generate the CAROLINE email.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file

    Returns
    -------
    str
        The message that will be emailed.
    """
    try:
        message = _generate_email(parameter_file)
    except Exception as error:
        message = _failed_email_generation(error)

    return message


def detect_sensor_pixelsize(sensor: str) -> tuple[int, int]:
    """Retrieve the size of the pixels of a specific sensor.

    Parameters
    ----------
    sensor: str
        Abbreviated name of the sensor. Options are "TSX", "RSAT2", "ERS", "ENV", "Cosmo", "PAZ", ALOS2", "TDX".

    Returns
    -------
    tuple[int, int]
        Azimuth pixel size in meters, range pixel size in meters

    Raises
    ------
    ValueError
        If an unknown sensor is provided.

    """
    # returns pixel size in m
    if sensor == "TSX":
        d_az = 3
        d_r = 3
    elif sensor == "RSAT2":
        d_az = 11.8
        d_r = 8
    elif sensor == "ERS":
        d_az = 8
        d_r = 4
    elif sensor == "ENV":
        d_az = 30
        d_r = 30
    elif sensor == "Cosmo":
        d_az = 15
        d_r = 15
    elif sensor == "PAZ":
        d_az = 3
        d_r = 3
    elif sensor == "ALOS2":
        d_az = 10
        d_r = 10
    elif sensor == "TDX":
        d_az = 3
        d_r = 3
    else:
        raise ValueError(f"Unknown sensor {sensor}!")
    return d_az, d_r


def haversine(lat1: float, lat2: float, lon1: float, lon2: float) -> float:
    """Calculate the spherical distance between [lat1, lon1] and [lat2, lon2].

    Parameters
    ----------
    lat1 : float
        Latitude of point 1
    lat2 : float
        Latitude of point 2
    lon1 : float
        Longitude of point 1
    lon2 : float
        Longitude of point 2

    Returns
    -------
    float
        Spherical distance in meters between [lat1, lon1] and [lat2, lon2].

    """
    dphi = np.radians(lat1 - lat2)
    dlambda = np.radians(lon1 - lon2)
    dist = (
        2
        * EARTH_RADIUS
        * np.arcsin(
            np.sqrt(
                (1 - np.cos(dphi) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * (1 - np.cos(dlambda))) / 2
            )
        )
    )
    return dist


def write_directory_contents(directory: str, filename: str = "dir_contents.txt") -> None:
    """Write the contents of a directory into a text file in that directory.

    Parameters
    ----------
    directory: str
        Directory of which the contents should be saved
    filename: str, optional
        Name of the output text file. Default `dir_contents.txt`
    """
    files = glob.glob(f"{directory}/*")
    filenames = [file.split("/")[-1] for file in files]

    save_string = "\n".join(filenames)
    f = open(f"{directory}/{filename}", "w")
    f.write(save_string)
    f.close()
