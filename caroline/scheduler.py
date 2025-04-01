import datetime as dt
import glob
import os
import re
from sys import argv

from caroline.config import get_config
from caroline.io import create_shapefile, link_shapefile, parse_start_files, read_area_track_list, read_parameter_file
from caroline.utils import format_process_folder

CONFIG_PARAMETERS = get_config()
STEP_KEYS = ["coregistration", "crop", "reslc", "depsi", "depsi_post"]
STEP_REQUIREMENTS = {
    "coregistration": None,
    "doris_cleanup": "coregistration",
    "crop": "coregistration",
    "reslc": "coregistration",
    "depsi": "crop",
    "mrm": "depsi",
    "depsi_post": "mrm",
    "portal_upload": "depsi_post",
    "tarball": "depsi_post",
    # dependency is the first one that has run out of this ordered list
    "email": ["depsi_post", "depsi", "reslc", "crop", "coregistration"],
}
TIME_LIMITS = {
    "short": "10:00:00",
    "normal": "5-00:00:00",
    "infinite": "12-00:00:00",
}  # the true max is 30 days but this will cause interference with new images
SBATCH_ARGS = {
    "doris": "--qos=long --ntasks=1 --cpus-per-task=8 --mem-per-cpu=8000",
    "doris_cleanup": "--qos=long --ntasks=1 --cpus-per-task=1",
    "deinsar": "--qos=long --ntasks=1 --cpus-per-task=8 --mem-per-cpu=8000",
    "crop": "--qos=long --ntasks=1 --cpus-per-task=2",
    "depsi": "--qos=long --ntasks=1 --cpus-per-task=1 --mem-per-cpu=8000",
    "depsi_post": "--qos=long --ntasks=1 --cpus-per-task=4 --mem-per-cpu=8000",
    "mrm": "--qos=long --ntasks=1 --cpus-per-task=1 --mem-per-cpu=8000",
    "reslc": "--qos=long --ntasks=1 --cpus-per-task=4 --nodes=1",
    "email": "--qos=long --ntasks=1 --cpus-per-task=1",
    "portal_upload": "--qos=long --ntasks=1 --cpus-per-task=1",
    "tarball": "--qos=long --ntasks=1 --cpus-per-task=1",
}
SBATCH_BASH_FILE = {
    "doris": "doris_stack.sh",
    "doris_cleanup": "cleanup.sh",
    "deinsar": "run_deinsar.sh",
    "crop": "crop.sh",
    "depsi": "depsi.sh",
    "depsi_post": "depsi_post.sh",
    "mrm": "read_mrm.sh",
    "reslc": "reslc.sh",
    "email": None,
    "portal_upload": None,
    "tarball": None,
}
SBATCH_TWO_LETTER_ID = {
    "doris": "D5",  # these will show up in the squeue
    "doris_cleanup": "DC",
    "deinsar": "D4",
    "crop": "CR",
    "depsi": "DE",
    "depsi_post": "DP",
    "mrm": "MR",
    "reslc": "RE",
    "email": "EM",
    "portal_upload": "PU",
    "tarball": "TB",
}


def scheduler(new_tracks: list, force_tracks: list) -> list:
    """Create a list of processes to be scheduled given a set of new tracks.

    Parameters
    ----------
    new_tracks: list
        list of tracks with new images, formatted as `s1_dsc_t037`
    force_tracks: list
        list of tracks formatted as `[`s1_dsc_t037`, 'nl_grijpskerk']` for specific AoIs

    Returns
    -------
    list
        The processes to be scheduled with their dependencies, formatted as entries [process_id, dependency_id].
        The list is sorted in such a way that if process x depends on process y, process y will be earlier in the list.
    """
    area_track_files = glob.glob(f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/area-track-lists/*.dat")

    track_dict = {}
    for new_track in new_tracks:
        track_dict[new_track] = []

    # figure out which parameter files should be triggered
    for area_track_file in area_track_files:
        dependency, tracks = read_area_track_list(area_track_file)
        for new_track in new_tracks:
            if new_track in tracks:
                track_dict[new_track].append([area_track_file.split("/")[-1].split(".")[0], dependency])

    # add the forced parameter files
    for track in force_tracks:
        if track[0] in track_dict.keys():
            if track[1] in [i[0] for i in track_dict[track[0]]]:  # it is already being submitted
                pass
            else:
                track_dict[track[0]].append([track[1], None])
        else:
            track_dict[track[0]] = [[track[1], None]]

    parameter_file_base = f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/parameter-files/param_file"

    processes = []
    for new_track in track_dict.keys():
        for data in track_dict[new_track]:
            out_parameters = read_parameter_file(
                f"{parameter_file_base}_{data[0]}.txt", [f"do_{step}" for step in STEP_KEYS]
            )

            # depsi_post has 4 steps: read_mrm, depsi_post, portal_upload and tarball
            if out_parameters["do_depsi_post"] == "1":
                out_parameters["do_mrm"] = "1"
                portal_upload = read_parameter_file(f"{parameter_file_base}_{data[0]}.txt", ["depsi_post_mode"])[
                    "depsi_post_mode"
                ]
                if portal_upload == "csv":
                    out_parameters["do_portal_upload"] = "1"
                    out_parameters["do_tarball"] = "0"
                else:
                    out_parameters["do_portal_upload"] = "0"
                    out_parameters["do_tarball"] = "1"
            else:
                out_parameters["do_mrm"] = "0"
                out_parameters["do_portal_upload"] = "0"
                out_parameters["do_tarball"] = "0"

            # email always has to be sent
            out_parameters["do_email"] = "1"

            # check if the cleanup script needs to be run
            out_parameters["do_doris_cleanup"] = "0"
            if out_parameters["do_coregistration"] == "1":
                sensor = read_parameter_file(f"{parameter_file_base}_{data[0]}.txt", ["sensor"])["sensor"]
                if sensor.upper() == "S1":
                    out_parameters["do_doris_cleanup"] = "1"

            for step in out_parameters.keys():
                if out_parameters[step] == "1":
                    process_id = f"{data[0]}-{step[3:]}-{new_track}"

                    # we need to figure out the dependencies
                    requirement = STEP_REQUIREMENTS[step[3:]]
                    if STEP_REQUIREMENTS[step[3:]] is not None:
                        # if the step is a string, it is one option
                        if isinstance(requirement, str):
                            # if the step is run in the same parameter file, that is the dependency
                            if out_parameters[f"do_{requirement}"] == "1":
                                dependency_id = f"{data[0]}-{requirement}-{new_track}"
                            # if not, and there is a dependency parameter file, it is run there
                            elif data[1] is not None:
                                dependency_id = f"{data[1]}-{requirement}-{new_track}"
                            # if not either, the dependency will not run and we assume it already ran
                            else:
                                dependency_id = None
                        else:
                            # for the email, multiple dependency locations are possible. We select the latest one
                            # in the chain
                            dependency_id = None
                            for req in requirement:
                                if out_parameters[f"do_{req}"] == "1":
                                    dependency_id = f"{data[0]}-{req}-{new_track}"
                                    break
                    else:
                        dependency_id = None

                    processes.append([process_id, dependency_id])

    # check if all dependencies exist, and sort
    sorted_processes = []
    # first all processes without dependencies
    for process in processes:
        if process[1] is None:
            sorted_processes.append(process)

    # then all others
    modified = True
    while modified:
        modified = False
        for process in processes:
            if process not in sorted_processes:
                if process[1] in [proc[0] for proc in sorted_processes]:  # the dependency is there
                    sorted_processes.append(process)
                    modified = True

    if len(processes) != len(sorted_processes):
        for process in processes:
            if process not in sorted_processes:
                print(f"Warning: dependency of {process} has not been scheduled! Continuing without dependency.")
                sorted_processes.append([process[0], None])

    return sorted_processes


def _generate_all_shapefiles(sorted_processes: list) -> None:
    """Generate the shapefiles of all processes that are being scheduled.

    Parameters
    ----------
    sorted_processes: list
        All processes to be scheduled.
    """
    for process in sorted_processes:
        parameter_file = (
            f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/"
            f"parameter-files/param_file_{process[0].split('-')[0]}.txt"
        )
        parameter_file_parameters = read_parameter_file(
            parameter_file, ["shape_directory", "shape_AoI_name", "shape_file"]
        )

        # first create the directory
        os.makedirs(parameter_file_parameters["shape_directory"], exist_ok=True)

        # then create or link the shapefile
        if not os.path.exists(
            f"{parameter_file_parameters['shape_directory']}/"
            f"{parameter_file_parameters['shape_AoI_name']}_shape.shp"
        ):
            if parameter_file_parameters["shape_file"] == "":
                create_shapefile(parameter_file)
            else:
                link_shapefile(parameter_file)


def submit_processes(sorted_processes: list) -> None:
    """Submit all processes to the SLURM scheduler.

    Parameters
    ----------
    sorted_processes: list
        All processes to be scheduled.
    """
    # first generate all the shapefiles
    _generate_all_shapefiles(sorted_processes)

    run_timestamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")

    # then start looping over the list, freezing the current configuration files
    frozen_parameter_files = {}
    job_ids = {}
    for process in sorted_processes:
        parameter_file = (
            f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/"
            f"parameter-files/param_file_{process[0].split('-')[0]}.txt"
        )
        job = process[0].split("-")[1]
        track = process[0].split("-")[2]
        if f"{parameter_file}_{track}" not in frozen_parameter_files.keys():
            # freeze the configuration
            frozen_parameter_file = (
                f"{CONFIG_PARAMETERS['FROZEN_PARAMETER_FILE_DIRECTORY']}/"
                f"{parameter_file.split('.')[0]}_{track}_{run_timestamp}.txt"
            )
            frozen_parameter_files[parameter_file] = frozen_parameter_file

            # fill in the correct track
            f = open(parameter_file)
            parameter_file_data = f.read()
            f.close()
            track_number = track.split("_")[-1].lstrip("0")
            track_direction = track.split("_")[1]

            parameter_file_data = re.sub(
                r"track = \[[0123456789, ]*]", f"track = [{track_number}]", parameter_file_data
            )
            parameter_file_data = re.sub(
                r"asc_dsc = \[['adsc, ]*]", f"asc_dsc = ['{track_direction}']", parameter_file_data
            )

            # and write the frozen file
            f = open(frozen_parameter_file, "w")
            f.write(parameter_file_data)
            f.close()

        frozen_parameter_file = frozen_parameter_files[f"{parameter_file}_{track}"]

        if process[1] is None:
            dependency_job_id = None
        else:
            # because the list is ordered, the dependency has to be there already
            dependency_job_id = job_ids[f"{process[1].split('-')[0]}_{process[1].split('-')[2]}"]

        # Generate the necessary SBATCH arguments
        # first the partition
        if job in ["coregistration", "crop", "reslc", "depsi", "depsi_post"]:
            partition = read_parameter_file(frozen_parameter_file, [f"{job}_partition"])[f"{job}_partition"]
        elif job in ["email", "tarball", "portal_upload", "doris_cleanup"]:
            partition = "short"
        else:  # mrm
            partition = "normal"

        # then the dependency
        if dependency_job_id is None:
            dependency_string = " "
        else:
            if job == "email":  # we alwayw want to send an email
                dependency_string = f" --dependency=after:{dependency_job_id} "
            else:  # we want to kill the other dependencies if its predecessor crashed
                dependency_string = f" --dependency=afterok:{dependency_job_id} --kill-on-invalid-dep=yes "

        # then the job name
        three_letter_id = read_parameter_file(frozen_parameter_file, ["three_letter_id"])["three_letter_id"]
        sensor = track.split("_")[0]
        if job == "coregistration":
            if sensor.lower() == "s1":  # e.g. D5088NVE for Doris v5, track 88, AoI nl_veenweiden
                job_name = f"{SBATCH_TWO_LETTER_ID['doris']}{track.split('_')[-1]}{three_letter_id}"
            else:
                job_name = f"{SBATCH_TWO_LETTER_ID['deinsar']}{track.split('_')[-1]}{three_letter_id}"
        else:
            job_name = f"{SBATCH_TWO_LETTER_ID[job]}{track.split('_')[-1]}{three_letter_id}"

        # finally, combine everything
        sbatch_arguments = (
            f"--partition={partition} --job_name={job_name} "
            f"--time={TIME_LIMITS[partition]}{dependency_string}{SBATCH_ARGS[job]}"
        )

        # generate the arguments necessary to start the job
        if SBATCH_BASH_FILE[job] is None:  # no bash job is necessary
            start_job_arguments = (
                f"{frozen_parameter_file} {eval(track.split('_')[2].lstrip('0'))} {job} "
                f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']} "
                f"{CONFIG_PARAMETERS['CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY']}"
            )
            base_directory = None
        else:  # generate the path to the bash file, then add it as the fourth argument
            if job in ["mrm", "depsi_post", "depsi"]:  # these all run in the depsi folder, which has one extra layer
                parameters = read_parameter_file(frozen_parameter_file, ["depsi_directory", "depsi_AoI_name"])
                base_directory = format_process_folder(
                    base_folder=parameters["depsi_directory"],
                    AoI_name=parameters["depsi_AoI_name"],
                    sensor=track.split("_")[0],
                    asc_dsc=track.split("_")[1],
                    track=eval(track.split("_")[2].lstrip("0")),
                )
                base_directory += "/psi"
            elif job == "doris_cleanup":  # this one runs in the coregistration folder
                parameters = read_parameter_file(
                    frozen_parameter_file, ["coregistration_directory", "coregistration_AoI_name"]
                )
                base_directory = format_process_folder(
                    base_folder=parameters["coregistration_directory"],
                    AoI_name=parameters["coregistration_AoI_name"],
                    sensor=track.split("_")[0],
                    asc_dsc=track.split("_")[1],
                    track=eval(track.split("_")[2].lstrip("0")),
                )
            else:
                parameters = read_parameter_file(frozen_parameter_file, [f"{job}_directory", f"{job}_AoI_name"])
                base_directory = format_process_folder(
                    base_folder=parameters[f"{job}_directory"],
                    AoI_name=parameters[f"{job}_AoI_name"],
                    sensor=track.split("_")[0],
                    asc_dsc=track.split("_")[1],
                    track=eval(track.split("_")[2].lstrip("0")),
                )
            start_job_arguments = (
                f"{frozen_parameter_file} {eval(track.split('_')[2].lstrip('0'))} {job} "
                f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']} "
                f"{CONFIG_PARAMETERS['CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY']} "
                f"{base_directory} {SBATCH_BASH_FILE[job]}"
            )

        # finally, submit the job and save the job id in the dictionary and in a file in the output directory
        job_id = os.popen(
            f"cd {CONFIG_PARAMETERS['SLURM_OUTPUT_DIRECTORY']}; sbatch {sbatch_arguments} start_job.sh "
            f"{start_job_arguments}"
        ).read()

        job_id = job_id.strip().split(" ")[-1]
        job_ids[f"{process[0].split('-')[0]}_{process[0].split('-')[2]}"] = job_id
        # Finally, log that this job was submitted
        if dependency_string == " ":
            os.system(
                f"""echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) submitted job {job} """
                f"""(AoI {process[0].split("-")[0]}, track {track.split("_")[-1]}) with slurm-ID ${job_id}" """
                f'''>> ${CONFIG_PARAMETERS["CAROLINE_WORK_DIRECTORY"]}/submitted_jobs.log"'''
            )
        else:
            os.system(
                f"""echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) in $(pwd) submitted job {job} """
                f"""(AoI {process[0].split("-")[0]}, track {track.split("_")[-1]}) with slurm-ID ${job_id} """
                f"""as dependency to slurm-ID ${dependency_job_id}" """
                f'''>> ${CONFIG_PARAMETERS["CAROLINE_WORK_DIRECTORY"]}/submitted_jobs.log"'''
            )

        if job in ["doris_cleanup", "depsi_post", "mrm"]:  # to split out the individual job ids in the same directory
            appendix = f"_{job}"
        else:
            appendix = ""

        if base_directory is not None:
            f = open(f"{frozen_parameter_file.split('/')[-1].split('.')[0]}_job_id{appendix}.txt")
            f.write(str(job_id))
            f.close()


if __name__ == "__main__":
    filename, new_insar_files_file, force_start_file = argv

    new_tracks, force_start_tracks = parse_start_files(new_insar_files_file, force_start_file)

    processes_to_submit = scheduler(new_tracks, force_start_tracks)

    submit_processes(list(processes_to_submit))
