import glob
import os
import zipfile
from math import log

import asf_search as asf
import numpy as np

from caroline.config import get_config
from caroline.io import create_shapefile, link_shapefile, read_parameter_file, read_shp_extent

BYTE_PREFIX = " kMGTPEZYRQ"
CONFIG_PARAMETERS = get_config()
EARTH_RADIUS = 6378136  # m


def format_process_folder(job_description: dict, parameter_file: str, track: int) -> str:
    """Format a processing folder name based on processing characteristics.

    Parameters
    ----------
    job_description: dict
        Dictionary readout from `config/job-definitions.yaml` of the job that the processing folder should be
        generated for.
    parameter_file: str
        Full path to the parameter file for which the processing folder should be generated.
    track: int
        Track for which the processing should be generated.

    Returns
    -------
    str
        Absolute path of the processing folder
    """
    if job_description["bash-file"] is None:
        raise ValueError(f"Cannot generate directory for job {job_description} as bash-file key is None!")

    directory_key = job_description["bash-file"]["bash-file-base-directory"]
    directory_appendix = job_description["bash-file"]["bash-file-directory-appendix"]
    directory_reusable = job_description["bash-file"]["bash-file-directory-is-reusable"]

    if not directory_reusable:  # we need to append a date to the file -> the date in the parameter file name
        directory_appendix = f"""-{parameter_file.split("_")[-1].split(".")[0]}{directory_appendix}"""

    parameters = read_parameter_file(
        parameter_file,
        [f"{directory_key}_directory", f"{directory_key}_AoI_name", "sensor", "asc_dsc", "track"],
    )
    base_folder = parameters[f"{directory_key}_directory"]
    AoI_name = parameters[f"{directory_key}_AoI_name"]
    sensor = parameters["sensor"]
    asc_dsc = eval(parameters["asc_dsc"])[eval(parameters["track"]).index(track)]

    return f"{base_folder}/{AoI_name}_{sensor.lower()}_{asc_dsc.lower()}_t{track:0>3d}{directory_appendix}"


def remove_incomplete_sentinel1_images(parameter_file: str) -> None:
    """Identify and remove incomplete Sentinel-1 image downloads to prevent Doris v5 crashing.

    The identified files are printed to a `bad_zips.txt`.

    Parameters
    ----------
    parameter_file: str
        Full path to the parameter file of the processing run where the images are to be filtered

    """
    search_parameters = ["track"]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])

    status = []

    doris_job_definition = get_config(
        f'{CONFIG_PARAMETERS["CAROLINE_INSTALL_DIRECTORY"]}/config/job-definitions.yaml', flatten=False
    )["jobs"]["doris"]

    for track in range(len(tracks)):
        base_folder = format_process_folder(
            parameter_file=parameter_file, job_description=doris_job_definition, track=tracks[track]
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


def generate_shapefile(parameter_file: str) -> None:
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
    log_folder_name = (
        f'{CONFIG_PARAMETERS["CAROLINE_PUBLIC_LOG_DIRECTORY"]}/'
        f'{"_".join(parameter_file.split("/")[-1].split("_")[2:]).split(".")[0]}'
    )

    os.makedirs(f"{log_folder_name}/parameter-file")
    os.system(f"cp -p {parameter_file} {log_folder_name}/parameter-file/{parameter_file.split('/')[-1]}")

    os.makedirs(f"{log_folder_name}/overview")

    status_checks = ""
    for job in jobs["jobs"].keys():
        if job_schedule_check(parameter_file, job, jobs["jobs"]):  # it has run
            job_id = find_slurm_job_id(parameter_file, job)
            check = proper_finish_check(parameter_file, job, job_id)

            os.makedirs(f"{log_folder_name}/{job}")
            os.system(f"sacct --jobs={job_id} >> {log_folder_name}/{job}/SACCT-STATUS.txt")  # dump sacct output

            if jobs["jobs"][job]["bash-file"] is not None:
                f = open(f"{log_folder_name}/{job}/STORAGE-DIRECTORY.txt", "w")
                f.write(format_process_folder(jobs["jobs"][job], parameter_file, tracks[0]))
                f.close()

            if check["successful_finish"]:
                f = open(f"{log_folder_name}/{job}/STATUS-job-finished.log", "w")
                f.close()
                os.system(f"cp -p {check['slurm_file']} {log_folder_name}/{job}/{check['slurm_file'].split('/')[-1]}")
                os.system(f"""echo "{job} finished properly\n" >> {log_folder_name}/overview/STATUS-overview.txt""")
                if check["status_file"] is not None:
                    os.system(
                        f"cp -p {check['status_file']} {log_folder_name}/{job}/{check['status_file'].split('/')[-1]};"
                    )
            elif check["successful_start"]:
                if job != "email":  # since this one cannot be finished (it is calling this function), ignore it
                    f = open(f"{log_folder_name}/{job}/STATUS-job-did-not-finish.log", "w")
                    f.close()
                    os.system(
                        f"""echo "{job} did not finish properly" >> {log_folder_name}/overview/STATUS-overview.txt"""
                    )
                os.system(f"cp -p {check['slurm_file']} {log_folder_name}/{job}/{check['slurm_file'].split('/')[-1]}")
                if check["status_file"] is not None:
                    os.system(
                        f"cp -p {check['status_file']} {log_folder_name}/{job}/{check['status_file'].split('/')[-1]}"
                    )
            else:
                f = open(f"{log_folder_name}/{job}/STATUS-job-did-not-start.log", "w")
                f.close()
                os.system(f"""echo "{job} did not start" >> {log_folder_name}/overview/STATUS-overview.txt""")

            if jobs["jobs"][job]["email"]["include-in-email"]:
                if jobs["jobs"][job]["bash-file"] is not None:
                    directory = read_parameter_file(
                        parameter_file, [f"{jobs['jobs'][job]['bash-file']['bash-file-base-directory']}_directory"]
                    )[f"{jobs['jobs'][job]['bash-file']['bash-file-base-directory']}_directory"]
                else:
                    directory = CONFIG_PARAMETERS["SLURM_OUTPUT_DIRECTORY"]
                if check["successful_finish"]:
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
                    status_checks += (
                        f"!!! {job}: {tracks_formatted} did not finish properly! " f"(located in {directory} )\n\n"
                    )
                else:
                    status_checks += (
                        f"!!! {job}: {tracks_formatted} did not start properly! " f"(located in {directory} )\n\n"
                    )

    os.system(f"chmod -R 777 {log_folder_name}")  # to make everything downloadable by everyone

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
All debug logs, SLURM output and the parameter file can be accessed at 
https://public.spider.surfsara.nl{log_folder_name.replace("Public/", "")} .

"""

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
        parameters = read_parameter_file(parameter_file, ["track"])
        track = eval(parameters["track"])[0]  # as there is only one

        base_directory = format_process_folder(parameter_file=parameter_file, job_description=data, track=track)

        dir_file = f"{base_directory}/dir_contents{data['directory-contents-file-appendix']}.txt"
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
            elif status_data[1] == "matlab":  # Matlab can return a zero exit code while still experiencing an error
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


def convert_shp_to_wkt(shp_filename: str) -> str:
    """Convert a shapefile to a WKT string.

    Parameters
    ----------
    shp_filename: str
        Full path to the shapefile

    Returns
    -------
    str
        WKT string of the shape contained in the shapefile
    """
    shp = read_shp_extent(shp_filename, shp_type="AoI")["0"]
    wkt = f"POLYGON(({', '.join(f'{x[0]} {x[1]}' for x in shp)}))"
    return wkt


def identify_s1_orbits_in_aoi(shp_filename: str) -> tuple[list[str], dict]:
    """Identify the Sentinel-1 orbit numbers and directions crossing a AoI.

    Parameters
    ----------
    shp_filename: str
        Full path to the shapefile of the AoI

    Returns
    -------
    list
        The orbits overlapping with the AoI
    dict
        The footprints of the overlapping SLCs per track
    """
    wkt = convert_shp_to_wkt(shp_filename)
    slcs = None
    counter = 0
    while slcs is None:
        try:
            slcs = asf.geo_search(
                intersectsWith=wkt,
                platform=asf.PLATFORM.SENTINEL1,
                beamMode="IW",
                processingLevel="SLC",
                start="one month ago",
                end="now",
            )
        except (asf.exceptions.ASFSearch5xxError, asf.exceptions.ASFSearchError, TimeoutError):
            counter += 1
            os.system(f'''echo "ASF encountered an internal error. Retrying... (#{counter})"''')

    orbits = [
        f"s1_{slc.properties['flightDirection'].lower().replace('e', '')[:3]}_t{slc.properties['pathNumber']:0>3d}"
        for slc in slcs
    ]
    filtered_orbits = list(sorted(list(set(orbits))))

    extents = [slc.geojson()["geometry"]["coordinates"][0] for slc in slcs]
    footprints = {}
    for orbit in filtered_orbits:
        footprints[orbit] = []

    for extent in range(len(extents)):
        footprints[orbits[extent]].append(extents[extent])

    return filtered_orbits, footprints


def get_path_bytesize(path: str) -> int:
    """Retrieve the number of bytes in a file, or a folder and all its subdirectories.

    Parameters
    ----------
    path: str
        Absolute path to the file or folder of which the datasize is requested

    Returns
    -------
    int
        Filesize / folder size in bytes
    """
    data = os.popen(f"ls -ld {path}").read().split(" ")
    data = [d for d in data if d != ""]
    bytesize = int(data[4])
    return bytesize


def convert_bytesize_to_humanreadable(bytesize: int) -> str:
    """Convert a number of bytes into human-readable format.

    Parameters
    ----------
    bytesize: int
        Number of bytes

    Returns
    -------
    str
        Number of bytes in human-readable format
    """
    if bytesize == 0:
        level = 0
    else:
        level = int(log(bytesize, 1024))
    humanreadable = f"{round(bytesize/1024**level, 2)} {BYTE_PREFIX[level]}B"
    return humanreadable


def get_processing_time(job_id: int) -> int:
    """Retrieve the seconds of processing time of a job given its job_id.

    Parameters
    ----------
    job_id: int
        The SLURM job-ID of the job

    Returns
    -------
    int
        The processing time of the job in seconds
    """
    data = os.popen(f"sacct --format=Elapsed --jobs={job_id}").read()
    elapsed = data.split("\n")[2]
    total_time = 0
    if "-" in elapsed:  # number of days is included:
        total_time += eval(elapsed.split("-")[0].strip().lstrip("0")) * 24 * 60 * 60
        elapsed = elapsed.split("-")[1]
    elapsed = elapsed.split(":")
    for n, mult in enumerate([3600, 60, 1]):
        time_elapsed = elapsed[n].strip().lstrip("0")
        if time_elapsed != "":  # 0 will be stripped completely, but adds nothing anyways so we can ignore it
            total_time += mult * eval(time_elapsed)
    return total_time


def job_schedule_check(parameter_file: str | dict, job: str, job_definitions: dict) -> bool:
    """Check if a job should be scheduled based on the parameter file and the job definitions.

    Parameters
    ----------
    parameter_file: str | dict
        Full path to the parameter file, or dictionary readout of the parameter file
    job: str
        Name of the job to be scheduled
    job_definitions: dict
        Dictionary readout of `job-definitions.yaml`

    Returns
    -------
    bool
        Boolean indicating if the job should be scheduled or not.
    """
    if job_definitions[job]["parameter-file-step-key"] is None:  # always runs
        return True

    if isinstance(parameter_file, str):
        out_parameters = read_parameter_file(parameter_file, [job_definitions[job]["parameter-file-step-key"]])
    else:
        val = parameter_file
        for key in job_definitions[job]["parameter-file-step-key"].split(":"):
            val = val[key]
        out_parameters = {job_definitions[job]["parameter-file-step-key"]: val}

    if out_parameters[job_definitions[job]["parameter-file-step-key"]] == 0:  # it is not requested
        return False

    # if we make it here, the step is requested
    if job_definitions[job]["filters"] is not None:  # if there are filters, extract them and check against them
        filters = extract_all_values_and_paths_from_dictionary(job_definitions[job]["filters"])
        for filt in filters:
            if isinstance(parameter_file, str):  # extract the requested value from the parameter file
                value_check = read_parameter_file(parameter_file, [":".join(filt[1])])
            else:
                value_check = parameter_file  # or from the dictionary
                for key in filt[1]:
                    value_check = value_check[key]
            if isinstance(filt[0], str):  # it meets the filter
                if value_check.lower() != filt[0].lower():
                    return False
            elif isinstance(filt[0], list):  # it's a list, so we check if it exists in the list
                if value_check.lower() not in [s.lower() for s in filt[0]]:
                    return False

    # if it was not kicked out by the filters, we return True
    return True


def extract_all_values_and_paths_from_dictionary(dictionary: dict, cur_keys: tuple = ()) -> list:
    """Extract all values and the paths to get there from a dictionary.

    Parameters
    ----------
    dictionary: dict
        Dictionary of which all values should be extracted
    cur_keys: tuple, default ()
        Way to keep track of the keys through recursion

    Returns
    -------
    list
        List of [value, [list of keys to get there]]
    """
    all_values = []
    for key in dictionary.keys():
        cur_keys = cur_keys + (key,)
        if isinstance(dictionary[key], dict):
            part_values = extract_all_values_and_paths_from_dictionary(dictionary[key], cur_keys)
            all_values = [*all_values, *part_values]
        else:
            all_values.append([dictionary[key], cur_keys])
    return all_values
