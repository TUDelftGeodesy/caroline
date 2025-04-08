import glob
import os
import zipfile
from typing import Literal

import numpy as np

from caroline.config import get_config
from caroline.io import create_shapefile, link_shapefile, read_parameter_file

CONFIG_PARAMETERS = get_config()
EARTH_RADIUS = 6378136  # m
VALID_STEPS_TO_CHECK = ["coregistration", "crop", "reslc", "depsi", "depsi_post"]


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
    search_parameters = [
        "track",
        "asc_dsc",
        "do_coregistration",
        "do_crop",
        "do_depsi",
        "do_depsi_post",
        "sensor",
        "coregistration_directory",
        "crop_directory",
        "depsi_directory",
        "do_reslc",
        "reslc_directory",
        "skygeo_viewer",
        "coregistration_AoI_name",
        "crop_AoI_name",
        "depsi_AoI_name",
        "reslc_AoI_name",
        "skygeo_customer",
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

    if len(tracks_formatted) == 1:
        tracks_formatted = tracks_formatted[0]

    # Extract the run name
    run_id = "_".join(parameter_file.split("/")[-1].split("_")[2:-4])

    # Generate the logs
    log = "==========DEBUG LOGS===========\n\n"

    success_rates = {
        "do_coregistration": [[], []],
        "do_crop": [[], []],
        "do_reslc": [[], []],
        "do_depsi": [[], []],
        "do_depsi_post": [[], []],
    }

    for key in success_rates.keys():
        if out_parameters[key] == "1":
            if key == "do_coregistration":
                if out_parameters["sensor"] == "S1":
                    log += "\n\n---------DORIS v5--------\n\n"
                else:
                    log += "\n\n---------DeInSAR---------\n\n"
            elif key == "do_crop":
                log += "\n\n---------Cropping----------\n\n"
            elif key == "do_reslc":
                log += "\n\n---------Re-SLC------------\n\n"
            elif key == "do_depsi":
                log += "\n\n---------DePSI-------------\n\n"
            elif key == "do_depsi_post":
                log += "\n\n---------DePSI-post--------\n\n"
            for track in range(len(tracks)):
                log += f"---Track {out_parameters['sensor'].lower()}_{asc_dsc[track]}_{tracks[track]:0>3d}---\n\n"

                check = proper_finish_check(parameter_file, key[3:], asc_dsc[track], tracks[track])

                if check["successful_finish"]:
                    log += "Step finished successfully!\n\n"
                    success_rates[key][0] += f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_{tracks[track]:0>3d}"
                elif check["successful_start"]:
                    log += "!!! Step did not finish properly!\n\n"
                    success_rates[key][1] += f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_{tracks[track]:0>3d}"
                else:
                    log += "!!! Step did not start properly!\n\n"
                    success_rates[key][1] += f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_{tracks[track]:0>3d}"

                if check["status_file"] is not None:
                    log += f"Status file: {check['status_file']}\nSlurm output: {check['slurm_file']}\n\n"

                    f = open(check["status_file"])
                    status = f.read()
                    f.close()
                    log += f"Statusfile output:\n\n{status}\n\n"
                else:
                    log += f"Slurm output: {check['slurm_file']}\n\n"
    log += "================"

    project_characteristics = f"""Project characteristics:
Owner: {out_parameters['project_owner']} ({out_parameters['project_owner_email']})
Engineer: {out_parameters['project_engineer']} ({out_parameters['project_engineer_email']})
Objective: {out_parameters['project_objective']}
Notes: {out_parameters['project_notes']}
"""

    lines = {}

    for key in success_rates.keys():
        lines[key] = ""
        if key == "do_depsi_post":
            lines["portal"] = ""
        if out_parameters[key] == "1":
            success_line = ""
            if len(success_rates[key][0]) > 1:
                success_line += f"Proper finish: {success_rates[key][0]}"
            elif len(success_rates[key][0]) == 1:
                success_line += f"Proper finish: {success_rates[key][0][0]}"
            if len(success_rates[key][1]) > 1:
                if len(success_line) > 0:
                    success_line += ", "
                success_line += f"Improper finish: {success_rates[key][0]}"
            elif len(success_rates[key][1]) == 1:
                if len(success_line) > 0:
                    success_line += ", "
                success_line += f"Improper finish: {success_rates[key][0][0]}"

            directory_key = f"{key[3:]}_directory"

            if key == "do_coregistration":
                line_header = "Coregistration"
            elif key == "do_crop":
                line_header = "Cropping"
            elif key == "do_reslc":
                line_header = "Re-SLC"
            elif key == "do_depsi":
                line_header = "DePSI"
            elif key == "do_depsi_post":
                line_header = "DePSI-post & poratl upload"
                directory_key = "depsi_directory"
                lines["portal"] = (
                    "NOTE: it can take a few hours for the results to show up in the portal.\n"
                    + "The DePSI-post results can be accessed at "
                    + "https://caroline.portal-tud.skygeo.com/portal/"
                    + f"{out_parameters['skygeo_customer']}/{out_parameters['skygeo_viewer']} ."
                )
            else:
                raise ValueError(f"Unknown key {key} for line header!")

            lines[key] = f"{line_header}: {success_line} (located in {out_parameters[directory_key]} )"

    message = f"""Dear radargroup,
    
    A new CAROLINE run has just finished on run {run_id}! 
    
    {project_characteristics}
    Run characteristics:
    Track(s): {tracks_formatted}
    Sensor: {out_parameters['sensor']}
    
    The following steps were run:
    {lines['do_coregistration']}

    {lines['do_crop']}
    {lines['do_reslc']}

    {lines['do_depsi']}
    {lines['do_depsi_post']}
    
    {lines['portal']}
    
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


def proper_finish_check(
    parameter_file: str,
    step_check: Literal["coregistration", "crop", "reslc", "depsi", "depsi_post"],
    asc_dsc: Literal["asc", "dsc"],
    track: int,
) -> dict:
    """Check if a process started and finished correctly, and supply the relevant parameter files.

    Parameters
    ----------
    parameter_file: str
        full path to the CAROLINE parameter file
    step_check: Literal["coregistration", "crop", "reslc", "depsi", "depsi_post"]
        which step to check
    asc_dsc: Literal["asc", "dsc"]
        whether track is an ascending or descending track
    track: int
        which track to check

    Returns
    -------
    dict
        Dictionary with four fields:
            successful_start: boolean indicating if the job started correctly
            successful_finish: boolean indicating if the job finished correctly
            slurm_file: identified slurm file belonging to the job (None if it doesn't exist)
            status_file: profile_log for Doris v5, resfile.txt for DePSI, None otherwise (also None if it was not found)
    """
    assert step_check in VALID_STEPS_TO_CHECK, f"Invalid step {step_check} provided! Valid are {VALID_STEPS_TO_CHECK}"

    if step_check == "depsi_post":
        step_key = "depsi"
    else:
        step_key = step_check

    search_parameters = [f"{step_key}_AoI_name", f"{step_key}_directory", "sensor"]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    base_directory = format_process_folder(
        base_folder=out_parameters[f"{step_key}_directory"],
        AoI_name=out_parameters[f"{step_key}_AoI_name"],
        sensor=out_parameters["sensor"],
        asc_dsc=asc_dsc,
        track=track,
    )

    if step_check in ["depsi", "depsi_post"]:
        base_directory += "/psi"

    # Detect the new slurm file
    if step_check == "depsi_post":
        appendix = f"_{step_check}"
    else:
        appendix = ""
    job_id_file = f"{parameter_file.split('/')[-1].split('.')[0]}_job_id{appendix}.txt"
    if not os.path.exists(f"{base_directory}/{job_id_file}"):
        new_slurms = []
    else:
        f = open(f"{base_directory}/{job_id_file}")
        job_id = f.read().strip()
        f.close()
        new_slurms = [f"{CONFIG_PARAMETERS['SLURM_OUTPUT_DIRECTORY']}/slurm-{job_id}.out"]

    if step_check == "depsi_post":
        dir_file = f"{base_directory}/dir_contents_depsi_post.txt"
    else:
        dir_file = f"{base_directory}/dir_contents.txt"

    f = open(dir_file)
    contents = f.read().split("\n")
    f.close()

    if len(new_slurms) > 0:
        slurm_file = new_slurms[0]  # it's the first one that started running after the file was generated
        successful_start = True

        f = open(slurm_file)
        slurm_output = f.read()
        f.close()

        if step_check == "coregistration":
            if out_parameters["sensor"] == "S1":
                # We need to check the profile logs of Doris v5
                profile_logs = glob.glob(f"{base_directory}/profile_log*")
                new_pls = [pl for pl in list(sorted(list(profile_logs))) if pl.split("/")[-1] not in contents]

                if len(new_pls) > 0:  # it started
                    status_file = new_pls[0]
                    f = open(status_file)
                    status = f.read()
                    f.close()
                    if " : end" in status:  # this is the last step, so it finished properly
                        successful_finish = True
                    else:
                        successful_finish = False
                else:  # it did not start
                    status_file = None
                    successful_start = False
                    successful_finish = False

            else:  # we need to check the output of Doris v4
                status_file = None

                # This is a Python/C-based module, so Traceback or EXCEPTION class indicate something went wrong
                if "Traceback (most recent call last):" in slurm_output or "EXCEPTION class" in slurm_output:
                    successful_finish = False
                else:
                    successful_finish = True

        elif step_check == "crop":
            status_file = None

            # this is a Matlab-based module, so 'Error in ' in the slurm file indicates something went wrong
            if "Error in " in slurm_output:
                successful_finish = False
            else:
                successful_finish = True

        elif step_check == "reslc":
            status_file = None

            # This is a Python-based module with a clear end logging
            if "Finishing... Closing client." in slurm_output:
                successful_finish = True
            else:
                successful_finish = False

        elif step_check == "depsi":
            resfiles = glob.glob(f"{base_directory}/*resfile.txt")
            new_resfiles = [res for res in list(sorted(list(resfiles))) if res.split("/")[-1] not in contents]

            if len(new_resfiles) > 0:
                status_file = new_resfiles[0]  # it's the first one

                f = open(status_file)
                status = f.read()
                f.close()

                # this is a matlab-based module with a clear end
                if "group8, end spatio-temporal consistency." in status:
                    successful_finish = True
                else:
                    successful_finish = False
            else:
                status_file = None
                successful_start = False
                successful_finish = False

        elif step_check == "depsi_post":
            status_file = None

            # This is a matlab-based module with a clear end
            if "Write csv web portal file ..." in slurm_output:
                successful_finish = True
            else:
                successful_finish = False

        else:
            raise ValueError(f"step {step_check} has no handling of checking...")

    else:
        slurm_file = None
        successful_start = False
        successful_finish = False
        status_file = None

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
