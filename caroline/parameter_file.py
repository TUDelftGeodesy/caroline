import glob
from typing import Literal

import yaml

from caroline.config import get_config
from caroline.io import write_parameter_file
from caroline.utils import extract_all_values_and_paths_from_dictionary

CONFIG_PARAMETERS = get_config()
# Only in the following list of keys, new keys in the configuration are allowed (as here tracks can be added)
# The ':' character is used as a split between keys to allow for going deeper into the dictionaries
NEW_CONFIG_KEYS_ALLOWED = ["deinsar:input:data-directories", "depsi:depsi-settings:general:ref-cn"]


def generate_full_parameter_file(
    user_parameter_file: str,
    track: int,
    asc_dsc: Literal["asc", "dsc"],
    output_file: str,
    mode: Literal["write", "test", "dict"] = "write",
) -> None | tuple[bool, list] | dict:
    """Generate the full parameter file based on a user-generated parameter file and the default settings.

    Parameters
    ----------
    user_parameter_file: str
        Full path to the .yaml user parameter file
    track: int
        Track number for which the parameter file is generated
    asc_dsc: Literal["asc", "dsc"]
        Corresponding ascending / descending of the track
    output_file: str
        Full path to the .yaml full parameter file
    mode: Literal["write", "test", "dict"], default "write"
        Whether to actually write the file to the output file, simply test if the user file works, or return the
        generated parameter file as dictionary

    Returns
    -------
    If mode = "test":
        bool: whether the test passed
        list: list of failed keys
    If mode = "write": (default)
        None
    If mode = "dict":
        Dictionary containing the generated parameter file
    """
    job_definitions = get_config(
        f'{CONFIG_PARAMETERS["CAROLINE_INSTALL_DIRECTORY"]}/config/job-definitions.yaml', flatten=False
    )

    # first build the default parameter file - the general section and the machine-readable part
    default_parameter_files = glob.glob(
        f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/parameter-files/default*.yaml"
    )
    default_settings = {}

    for default_parameter_file in default_parameter_files:
        if "default-job-param-file" not in default_parameter_file.split("/")[-1]:
            default_settings = _merge_user_settings(
                default_settings, default_parameter_file, nonexistent_keys_handling="Always-add"
            )

    general_user_settings = _merge_user_settings(
        default_settings, user_parameter_file, nonexistent_keys_handling="Ignore"
    )

    # set the correct step parameters:
    dependency = general_user_settings["general"]["workflow"]["dependency"]["input-step"]
    for output in general_user_settings["general"]["workflow"]["output-steps"]:
        general_user_settings["general"]["steps"][job_definitions["jobs"][output]["parameter-file-step-key"]] = 1
        requirement = job_definitions["jobs"][output]["requirement"]

        # trace back the requirements until the dependency is hit
        while requirement != dependency:
            if isinstance(requirement, str):
                general_user_settings["general"]["steps"][
                    job_definitions["jobs"][requirement]["parameter-file-step-key"]
                ] = 1
                requirement = job_definitions["jobs"][requirement]["requirement"]

            elif requirement is None:
                if dependency is not None:
                    raise ValueError(
                        "We have reached a point in the job dependency tree that should not exist. Please check "
                        f"job-definitions.yaml and the parameter file {user_parameter_file} thoroughly. The following "
                        f"input caused it to crash: requested output step: {output} "
                        f"({general_user_settings['general']['workflow']['output-steps']}),"
                        f"current user settings status: {general_user_settings}, current requirement is None, "
                        f"dependency step is {dependency}."
                    )

            elif isinstance(requirement, list):
                if dependency in requirement:
                    requirement = dependency
                else:  # if there are multiple options, only one of them should meet the filters. Let's check which one
                    # is not met
                    passed_requirements = []
                    for req in requirement:
                        if job_definitions["jobs"][req]["filters"] is not None:
                            filters = extract_all_values_and_paths_from_dictionary(
                                job_definitions["jobs"][req]["filters"]
                            )
                            passed = True
                            for filt in filters:
                                rec_val = general_user_settings
                                for key in filt[1]:
                                    rec_val = rec_val[key]
                                if isinstance(filt[0], str):
                                    if rec_val != filt[0]:
                                        passed = False
                                elif isinstance(filt[0], list):
                                    if rec_val not in filt[0]:
                                        passed = False
                            if passed:
                                passed_requirements.append(req)
                        else:  # there are no filters on this one
                            passed_requirements.append(req)
                        if len(passed_requirements) == 1:
                            requirement = req
                        else:
                            raise ValueError(
                                f"Cannot trace back AoI {user_parameter_file} to step {dependency}. "
                                f"Encountered {requirement} and {len(passed_requirements)} fit. Current "
                                f"status: {general_user_settings}"
                            )

    for job in job_definitions["jobs"].keys():
        if (
            f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/parameter-files/"
            f"default-job-param-file-{job}.yaml" in default_parameter_files
        ):
            with open(
                f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/parameter-files/"
                f"default-job-param-file-{job}.yaml"
            ) as f:
                general_user_settings.update(yaml.safe_load(f))

    # then we update the user settings of all sections once more
    user_settings = _merge_user_settings(general_user_settings, user_parameter_file)
    user_settings = _merge_user_settings(  # finally, merge in the track and asc_dsc for this parameter file
        user_settings, "", None, {"general": {"tracks": {"track": [track], "asc_dsc": [asc_dsc]}}}
    )

    # then we replace the default plugin directory with the one in the configuration and the AoI name
    user_settings = _replace_default_plugin_directory(user_settings)
    aoi_name = user_parameter_file.split("/")[-1].split(".yaml")[0].split("param-file-")[1].replace("-", "_")
    user_settings = _replace_default_aoi_name(user_settings, aoi_name)

    # check the shapefile settings --> only one is necessary, so we can remove the NEEDS_VALUE from the others
    if user_settings["general"]["shape-file"]["shape-file-link"] not in [None, "NEEDS_VALUE"]:  # takes precedent
        for key in user_settings["general"]["shape-file"]["rectangular-shape-file"].keys():
            user_settings["general"]["shape-file"]["rectangular-shape-file"][key] = None
    else:
        user_settings["general"]["shape-file"]["shape-file-link"] = None

    # finally we validate if the user has properly set all fields that need values
    validated, failed_keys = _validate_user_settings(user_settings)

    if mode == "test":
        return validated, list(failed_keys)

    if not validated:
        raise ValueError(f"The keys {failed_keys} are not specified in {user_parameter_file} but have to be!")

    if mode == "dict":
        return user_settings

    write_parameter_file(output_file, user_settings)


def _replace_default_plugin_directory(parameter_file: dict) -> dict:
    """Replace the plugins directory placeholder in the default parameter files with the actual plugins directory.

    Parameters
    ----------
    parameter_file: dict
        Dictionary readout of the combined default parameter files

    Returns
    -------
    dict
        Dictionary readout of the combined default parameter files with the plugins directory placeholder replaced
    """
    for key in parameter_file.keys():
        if isinstance(parameter_file[key], dict):
            parameter_file[key] = _replace_default_plugin_directory(parameter_file[key])
        elif isinstance(parameter_file[key], str):
            parameter_file[key] = parameter_file[key].replace(
                "**CAROLINE_PLUGINS_DIRECTORY**", CONFIG_PARAMETERS["CAROLINE_PLUGINS_DIRECTORY"]
            )
    return parameter_file


def _replace_default_aoi_name(parameter_file: dict, aoi_name: str) -> dict:
    """Replace the AoI name placeholder in the default parameter files with the actual AoI name.

    Parameters
    ----------
    parameter_file: dict
        Dictionary readout of the combined default parameter files
    aoi_name: str
        AoI name, generally formatted `<country_2_letter_id>_<region_of_interest>`

    Returns
    -------
    dict
        Dictionary readout of the combined default parameter files with the AoI name placeholder replaced
    """
    for key in parameter_file.keys():
        if isinstance(parameter_file[key], dict):
            parameter_file[key] = _replace_default_aoi_name(parameter_file[key], aoi_name)
        elif isinstance(parameter_file[key], str):
            parameter_file[key] = parameter_file[key].replace("**AoI_name**", aoi_name)
    return parameter_file


def _merge_user_settings(
    default_parameter_file: dict,
    user_settings_file: str,
    trace_keys: list | None = None,
    user_settings: dict | None = None,
    nonexistent_keys_handling: Literal["Error", "Ignore", "Always-add"] = "Error",
) -> dict:
    """Replace the default parameters with user definitions.

    Parameters
    ----------
    default_parameter_file: dict
        Dictionary readout of the combined default parameter files
    user_settings_file: str
        Full path to the user settings file (a .yaml)
    trace_keys: list | None, default None
        As this function recursively goes through the layers of the yaml, this variable allows it to keep track of
        the layers it has passed through. When calling this function, it should be left to `None`.
    user_settings: dict | None, default None
        As this function recursively goes through the layers of the yaml, this variable allows it to keep track of
        the settings at the current layer. When calling this function, it should be left to `None` so that
        `user_settings_file` is read out.
    nonexistent_keys_handling: Literal["Error", "Ignore", "Always-add], default "Error"
        Whether or not nonexistent keys should throw an error (except when present in `NEW_CONFIG_KEYS_ALLOWED`, or
        should be ignored (simply not added), or added anyways (Always-add)

    Returns
    -------
    dict
        Dictionary readout of the default parameter file with all user-defined parameters substituted.

    Raises
    ------
    ValueError
        When a setting is attempted to be set that does not exist in any parameter file and `nonexistent_keys_handling`
        equals "Error". Notable exception: it is allowed to add keys in the specific key structures defined in the
        global `NEW_CONFIG_KEYS_ALLOWED`.
    """
    if user_settings is None:
        with open(user_settings_file) as f:
            user_settings = yaml.safe_load(f)

    for key in user_settings.keys():
        if key not in default_parameter_file.keys():
            if trace_keys is None:
                check_traceback = ""
            else:
                check_traceback = ":".join(trace_keys)

            if check_traceback not in NEW_CONFIG_KEYS_ALLOWED:
                if nonexistent_keys_handling == "Error":
                    raise ValueError(
                        f"Attempting to locate key {check_traceback} : "
                        f"{key} from parameter file {user_settings_file}, but it is not in the default parameter file, "
                        f"and adding new keys is only allowed at the keys {NEW_CONFIG_KEYS_ALLOWED}!"
                    )
                elif nonexistent_keys_handling == "Ignore":
                    # we ignore this key --> used in the first part of the parameter file building when only the
                    # general section is to be built
                    continue
                elif nonexistent_keys_handling == "Always-add":
                    # override the NEW_CONFIG_KEYS_ALLOWED section (only for the default parameter files)
                    default_parameter_file[key] = user_settings[key]
            else:
                default_parameter_file[key] = user_settings[key]

        elif isinstance(user_settings[key], dict):
            if trace_keys is None:
                trace_keys = []
            trace_keys.append(key)
            default_parameter_file[key] = _merge_user_settings(
                default_parameter_file[key],
                user_settings_file,
                trace_keys,
                user_settings[key],
                nonexistent_keys_handling,
            )
        else:
            default_parameter_file[key] = user_settings[key]
    return default_parameter_file


def _validate_user_settings(user_settings: dict, trace_keys: list | None = None) -> tuple[bool, list]:
    """Validate that all fields that should be user-defined are user-defined.

    Parameters
    ----------
    user_settings: dict | None, default None
        Full settings
    trace_keys: list | None, default None
        As this function recursively goes through the layers of the yaml, this variable allows it to keep track of
        the layers it has passed through. When calling this function, it should be left to `None`.

    Returns
    -------
    bool
        True/False whether the check has passed
    list
        Traceback of the keys on which the check failed
    """
    failed_key_list = []

    for key in user_settings.keys():
        if isinstance(user_settings[key], dict):
            if trace_keys is None:
                trace_keys = []
            trace_keys.append(key)
            _, part_failed_key_list = _validate_user_settings(user_settings[key], trace_keys)
            failed_key_list = [*failed_key_list, *part_failed_key_list]

        elif user_settings[key] == "NEEDS_VALUE":
            failed_key_list.append(f"{':'.join(trace_keys) + ':' if trace_keys is not None else ''}{key}")

    return True if len(failed_key_list) == 0 else False, failed_key_list
