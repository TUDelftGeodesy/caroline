import glob

from caroline.io import read_area_track_list, read_parameter_file

CONFIG_PARAMETERS = {
    "CAROLINE_WORK_DIRECTORY": "/project/caroline/Software/run/caroline/work",
    "SLC_BASE_DIRECTORY": "/project/caroline/Data/radar_data/sentinel1",
    "ORBIT_DIRECTORY": "/project/caroline/Data/orbits",
    "CAROLINE_INSTALL_DIRECTORY": "/project/caroline/Software/caroline",
    "CAROLINE_WATER_MASK_DIRECTORY": "/project/caroline/Software/config/caroline-water-masks",
}
STEP_KEYS = ["coregistration", "crop", "reslc", "depsi", "depsi_post"]
STEP_REQUIREMENTS = {
    "coregistration": None,
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


def scheduler(new_tracks: list) -> list:
    """Create a list of processes to be scheduled given a set of new tracks.

    Parameters
    ----------
    new_tracks:
        list of tracks with new images, formatted as `s1_dsc_t037`

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

            for step in out_parameters.keys():
                if out_parameters[step] == "1":
                    process_id = f"{data[0]}_{step[3:]}_{new_track}"

                    # we need to figure out the dependencies
                    requirement = STEP_REQUIREMENTS[step[3:]]
                    if STEP_REQUIREMENTS[step[3:]] is not None:
                        # if the step is a string, it is one option
                        if isinstance(requirement, str):
                            # if the step is run in the same parameter file, that is the dependency
                            if out_parameters[f"do_{requirement}"] == "1":
                                dependency_id = f"{data[0]}_{requirement}_{new_track}"
                            # if not, and there is a dependency parameter file, it is run there
                            elif data[1] is not None:
                                dependency_id = f"{data[1]}_{requirement}_{new_track}"
                            # if not either, the dependency will not run and we assume it already ran
                            else:
                                dependency_id = None
                        else:
                            # for the email, multiple dependency locations are possible. We select the latest one
                            # in the chain
                            dependency_id = None
                            for req in requirement:
                                if out_parameters[f"do_{req}"] == "1":
                                    dependency_id = f"{data[0]}_{req}_{new_track}"
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
