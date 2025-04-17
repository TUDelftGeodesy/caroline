import datetime as dt
import glob
import os
import re
from sys import argv

from caroline.config import get_config
from caroline.io import create_shapefile, link_shapefile, parse_start_files, read_area_track_list, read_parameter_file
from caroline.utils import format_process_folder

CONFIG_PARAMETERS = get_config()
TIME_LIMITS = {
    "short": "10:00:00",
    "normal": "5-00:00:00",
    "infinite": "12-00:00:00",
}  # the true max is 30 days but this will cause interference with new images


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
    job_definitions = get_config(
        f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False
    )["jobs"]
    parameter_file_step_keys = list(
        set(
            [
                job_definitions[job]["parameter-file-step-key"]
                for job in job_definitions.keys()
                if job_definitions[job]["parameter-file-step-key"] is not None
            ]
        )
    )
    for new_track in track_dict.keys():
        for data in track_dict[new_track]:
            out_parameters_raw = read_parameter_file(f"{parameter_file_base}_{data[0]}.txt", parameter_file_step_keys)

            out_parameters = {}

            for job in job_definitions.keys():
                if job_definitions[job]["parameter-file-step-key"] is None:
                    out_parameters[f"do_{job}"] = "1"  # always runs
                elif out_parameters_raw[job_definitions[job]["parameter-file-step-key"]] == "0":
                    out_parameters[f"do_{job}"] = "0"
                else:  # the step is to be run
                    if job_definitions[job]["filters"] is not None:  # we need to filter on the sensor
                        for key in job_definitions[job]["filters"].keys():
                            value_check = read_parameter_file(f"{parameter_file_base}_{data[0]}.txt", [key])[key]
                            if isinstance(job_definitions[job]["filters"][key], str):
                                if value_check.lower() == job_definitions[job]["filters"][key].lower():
                                    out_parameters[f"do_{job}"] = "1"
                                else:
                                    out_parameters[f"do_{job}"] = "0"
                            else:  # it's a list, so we check if it exists in the list
                                if value_check.lower() in [s.lower() for s in job_definitions[job]["filters"][key]]:
                                    out_parameters[f"do_{job}"] = "1"
                                else:
                                    out_parameters[f"do_{job}"] = "0"
                    else:
                        out_parameters[f"do_{job}"] = "1"

            for step in out_parameters.keys():
                if out_parameters[step] == "1":
                    process_id = f"{data[0]}-{step[3:]}-{new_track}"

                    # we need to figure out the dependencies
                    requirement = job_definitions[step[3:]]["requirement"]
                    if requirement is not None:
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
                            # if multiple dependencies are possible, we want all of them
                            dependency_id = []
                            for req in requirement:
                                if out_parameters[f"do_{req}"] == "1":
                                    dependency_id.append(f"{data[0]}-{req}-{new_track}")
                            if len(dependency_id) == 0:
                                dependency_id = None
                            elif len(dependency_id) == 1:
                                dependency_id = dependency_id[0]
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
                if isinstance(process[1], str):
                    if process[1] in [proc[0] for proc in sorted_processes]:  # the dependency is there
                        sorted_processes.append(process)
                        modified = True
                else:  # it's a list since the Nones cannot be here
                    all_dependencies_present = True
                    for process_ in process[1]:
                        if process_ not in [proc[0] for proc in sorted_processes]:
                            all_dependencies_present = False

                    if all_dependencies_present:
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

    job_definitions = get_config(
        f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False
    )["jobs"]

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
                f"{parameter_file.split('/')[-1].split('.')[0]}_{track}_{run_timestamp}.txt"
            )
            frozen_parameter_files[f"{parameter_file}_{track}"] = frozen_parameter_file

            # fill in the correct track
            f = open(parameter_file)
            parameter_file_data = f.read()
            f.close()
            track_number = track.split("_")[-1][1:].lstrip("0")  # 1: to cut off the t
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
            dependency_job_id = job_ids[process[1]]

        # Generate the necessary SBATCH arguments
        # first the partition
        partition = job_definitions[job]["partition"]
        if partition not in TIME_LIMITS.keys():  # assume it needs to be read from the parameter file
            partition = read_parameter_file(frozen_parameter_file, [job_definitions[job]["partition"]])[
                job_definitions[job]["partition"]
            ]

        # then the dependency
        if dependency_job_id is None:
            dependency_string = " "
        elif isinstance(dependency_job_id, str):
            if job == "email":  # we always want to send an email
                dependency_string = f" --dependency=afterany:{dependency_job_id} "
            else:  # we want to kill the other dependencies if its predecessor crashed
                dependency_string = f" --dependency=afterok:{dependency_job_id} --kill-on-invalid-dep=yes "
        else:  # it's a list
            if job == "email":  # we always want to send an email
                dependency_string = f" --dependency=afterany:{':'.join(dependency_job_id)} "
            else:  # we want to kill the other dependencies if its predecessor crashed
                dependency_string = f" --dependency=afterok:{':'.join(dependency_job_id)} --kill-on-invalid-dep=yes "

        # then the job name
        three_letter_id = read_parameter_file(frozen_parameter_file, ["three_letter_id"])["three_letter_id"]

        # e.g. D5088NVE for Doris v5, track 88, AoI nl_veenweiden
        job_name = f"{job_definitions[job]['two-letter-id']}{track.split('_')[-1][1:]}{three_letter_id}"

        # finally, combine everything
        sbatch_arguments = (
            f"--partition={partition} --job-name={job_name} "
            f"--time={TIME_LIMITS[partition]}{dependency_string}{job_definitions[job]['sbatch-args']}"
        )

        # generate the arguments necessary to start the job
        if job_definitions[job]["bash-file"] is None:  # no bash job is necessary
            start_job_arguments = (
                f"{frozen_parameter_file} {track.split('_')[-1][1:].lstrip('0')} {job} "
                f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']} "
                f"{CONFIG_PARAMETERS['CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY']}"
            )
        else:  # generate the path to the bash file, then add it as the sixth argument
            parameters = read_parameter_file(
                frozen_parameter_file,
                [
                    f"{job_definitions[job]['bash-file']['bash-file-base-directory']}_directory",
                    f"{job_definitions[job]['bash-file']['bash-file-base-directory']}_AoI_name",
                ],
            )
            base_directory = format_process_folder(
                base_folder=parameters[f"{job_definitions[job]['bash-file']['bash-file-base-directory']}_directory"],
                AoI_name=parameters[f"{job_definitions[job]['bash-file']['bash-file-base-directory']}_AoI_name"],
                sensor=track.split("_")[0],
                asc_dsc=track.split("_")[1],
                track=eval(track.split("_")[2][1:].lstrip("0")),
            )
            base_directory += job_definitions[job]["bash-file"]["bash-file-directory-appendix"]

            job_id_file = (
                f"{base_directory}/{frozen_parameter_file.split('/')[-1].split('.')[0]}_"
                f"job_id{job_definitions[job]['bash-file']['job-id-file-appendix']}.txt"
            )

            start_job_arguments = (
                f"{frozen_parameter_file} {track.split('_')[2][1:].lstrip('0')} {job} "
                f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']} "
                f"{CONFIG_PARAMETERS['CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY']} "
                f"{base_directory} {job_definitions[job]['bash-file']['bash-file-name']} {job_id_file}"
            )

        # finally, submit the job and save the job id in the dictionary and in a file in the output directory
        job_id = os.popen(
            f"cd {CONFIG_PARAMETERS['SLURM_OUTPUT_DIRECTORY']}; "
            f"sbatch {sbatch_arguments} start_job.sh {start_job_arguments}"
        ).read()

        job_id = job_id.strip().split(" ")[-1]
        job_ids[process[0]] = job_id
        # Finally, log that this job was submitted
        if dependency_string == " ":
            os.system(
                """echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) """
                f"""submitted job {job} """
                f"""(AoI {process[0].split("-")[0]}, track {track.split("_")[-1][1:].lstrip("0")}) with """
                f"""slurm-ID {job_id}" """
                f""">> {CONFIG_PARAMETERS["CAROLINE_WORK_DIRECTORY"]}/submitted_jobs.log"""
            )
        else:
            os.system(
                """echo "$(date '+%Y-%m-%dT%H:%M:%S'): $(whoami) """
                f"""submitted job {job} """
                f"""(AoI {process[0].split("-")[0]}, track {track.split("_")[-1][1:].lstrip("0")}) with """
                f"""slurm-ID {job_id} """
                f"""as dependency to slurm-ID {dependency_job_id}" """
                f""">> {CONFIG_PARAMETERS["CAROLINE_WORK_DIRECTORY"]}/submitted_jobs.log"""
            )


if __name__ == "__main__":
    filename, new_insar_files_file, force_start_file = argv

    new_tracks, force_start_tracks = parse_start_files(new_insar_files_file, force_start_file)

    processes_to_submit = scheduler(new_tracks, force_start_tracks)

    submit_processes(list(processes_to_submit))
