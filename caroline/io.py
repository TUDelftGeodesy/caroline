import datetime as dt
import json
import os
import time
import xml.etree.ElementTree as ET
from math import cos, pi, radians
from typing import Literal

import fiona
import geopandas
import numpy as np
import yaml

from caroline.config import get_config

ALLOWED_S1_POLARISATIONS = ["IW_SLC__1SDV_VVVH"]  # allowed polarisations for S1 to trigger Caroline
CONFIG_PARAMETERS = get_config()
DELTA_T_SLC_LIMIT = 30  # maximum number of days an acquisition between acquisition date and Caroline trigger
EARTH_RADIUS = 6378136  # m


def read_area_track_list(area_track_list_file: str) -> tuple[str | None, list]:
    """Read the data in an area-track-list file.

    Parameters
    ----------
    area_track_list_file: str
        Full path to the area-track-list file

    Returns
    -------
    tuple[str | None, list]
        A tuple with as first element either the ID of the dependency, or None (if no dependency is found),
        as second element the list of tracks
    """
    if area_track_list_file.split("/")[-1].split("_")[0] == "INACTIVE":
        return None, []

    f = open(area_track_list_file)
    data = f.read().split("\n")
    f.close()

    # read the dependency
    dependency = data[0].split(":")[-1].strip()
    if dependency == "None":
        dependency = None

    # get the tracks
    tracks = [track for track in data[1:] if track != ""]

    return dependency, tracks


def read_parameter_file(
    parameter_file: str | dict, search_parameters: list, nonexistent_key_handling: Literal["Error", "Ignore"] = "Error"
) -> dict:
    """Read parameters from a CAROLINE parameter file into a dictionary.

    Parameters
    ----------
    parameter_file : str | dict
        Absolute path to the CAROLINE parameter file in .yaml format, or a dictionary readout of said file
    search_parameters: list
        Parameter names to be retrieved from the parameter file, as a list of strings. The `:` character can be used
        as separator to access variables in deeper layers (e.g. `general:shape-file:shape-file-link` will return the
        value for `parameter_file_dict["general"]["shape-file"]["shape-file-link"]`.
    nonexistent_key_handling: Literal["Error", "Ignore"], default "Error"
        Whether to throw an error or ignore keys that do not exist

    Returns
    -------
    dict
        Dictionary containing the values of the requested parameters.

    Raises
    ------
    AssertionError
        - When the parameter file does not exist
        - When the parameter file does not end in .yaml

    KeyError
        - When a requested parameter does not exist in the parameter file and `nonexistent_key_handling` = "Error"
    """
    if isinstance(parameter_file, str):
        assert os.path.exists(parameter_file), f"Specified parameter file {parameter_file} does not exist!"
        assert (
            parameter_file.split(".")[-1] == "yaml"
        ), f"Specified parameter file {parameter_file} is not a .yaml file!"
        with open(parameter_file) as f:
            data = yaml.safe_load(f)
    else:
        data = parameter_file

    out_parameters = {}

    for param in search_parameters:
        val = data
        encountered_error = False
        for key in param.split(":"):
            try:
                val = val[key]
            except KeyError as e:
                if nonexistent_key_handling == "Error":
                    raise KeyError(f"Key {param} requested but not found, nonexistent_key_handling set to Error") from e
                else:
                    encountered_error = True
        if not encountered_error:
            out_parameters[param] = val

    return out_parameters


def write_parameter_file(parameter_file: str, parameters: dict) -> None:
    """Write a parameter file to yaml.

    Parameters
    ----------
    parameter_file: str
        Full path to where the parameter file should be saved
    parameters: dict
        Dictionary readout of the parameters in the parameter file
    """
    with open(parameter_file, "w") as outfile:
        yaml.dump(parameters, outfile)


def write_run_file(
    save_path: str,
    template_path: str,
    asc_dsc: Literal["asc", "dsc"] | None,
    track: int | None,
    parameter_file: str | None,
    parameter_file_parameters: list = None,
    config_parameters: list = None,
    other_parameters: dict = None,
) -> None:
    """Fill a template from the templates directory, and write it to a specified location.

    This function replaces `**parameter_name**` in the templates with the parameter values, either read directly
    from the parameter file, from the configuration, or as specified by the user.

    Parameters
    ----------
    save_path: str
        Path where the file should be written to
    template_path: str
        Path to the template that should be used
    asc_dsc: Literal["asc", "dsc"] | None
        Whether the file is generated for an ascending or descending track. If `None`, using a dictionary parameter file
        parameter will throw an AssertionError
    track: int | None
        Which track the file is generated for. If `None`, using a dictionary parameter file
        parameter will throw an AssertionError
    parameter_file: str | None
        Full path to the parameter file. If `None`, calling `parameter_file_parameters` will throw an AssertionError
    parameter_file_parameters: list
        List of parameters to be read from the parameter file. Two options are available for each element in the list:
        - "parameter_name" - outputs the value of the parameter directly into the template
        - ["parameter_name", "mode"] - formats the parameter value before pasting it into the template. Three options
          are available:
          - "lowercase" - formats the parameter value into lowercase symbols.
          - "uppercase" - formats the parameter value into uppercase symbols.
          - "dictionary" - signals the parameter value is a dictionary. The key `sensor`_`asc_dsc`_t`track:0>3d` is
            expected. The value is the argument of this key.
          - "strip" - formatted as ["parameter_name", "strip", "chars"], removes all characters in the `chars` string
            from the parameter. E.g. `{"output", "csv"}` with `chars="{} "` becomes `"output","csv"`.
    config_parameters: list
        List of configuration parameters to be pasted into the template, directly from the configuration yaml
        (e.g. config/spider-config.yaml).
    other_parameters: dict
        Dictionary with as keys the parameter name in the template, as argument the value it should be replaced by

    Raises
    ------
    ValueError
        - If an object that is not `str` or `list` is encountered in `parameter_file_parameters`
        - If an unknown mode of parameter formatting is encountered
    AssertionError
        - If an unknown configuration parameter is requested
        - If strip mode is requested, but no characters to strip are provided
        - If strip mode is requested, but the characters to strip field is not a string
        - If `asc_dsc` is `None` or `track` is `None` and dictionary mode is requested

    """
    if config_parameters is not None:
        assert np.all(
            [config_parameter.upper() in CONFIG_PARAMETERS.keys() for config_parameter in config_parameters]
        ), f"Not all config parameters in {config_parameters} are known! Known are {CONFIG_PARAMETERS.keys()}."

    ft = open(template_path)
    template_data = ft.read()
    ft.close()

    if parameter_file_parameters is not None:
        assert parameter_file is not None, "parameter_file_parameters is not None but parameter_file is None!"
        for parameter_file_parameter in parameter_file_parameters:
            if isinstance(parameter_file_parameter, str):
                value = read_parameter_file(parameter_file, [parameter_file_parameter])[parameter_file_parameter]
                template_data = template_data.replace(f"**{parameter_file_parameter}**", str(value))
            elif isinstance(parameter_file_parameter, list):
                value = read_parameter_file(parameter_file, [parameter_file_parameter[0]])[parameter_file_parameter[0]]
                if parameter_file_parameter[1] == "lowercase":
                    value = str(value).lower()
                elif parameter_file_parameter[1] == "uppercase":
                    value = str(value).upper()
                elif parameter_file_parameter[1] == "dictionary":
                    sensor = read_parameter_file(parameter_file, ["general:input-data:sensor"])[
                        "general:input-data:sensor"
                    ].lower()
                    assert (
                        asc_dsc is not None
                    ), f"Dictionary mode requested for {parameter_file_parameter} but asc_dsc is None!"
                    assert (
                        track is not None
                    ), f"Dictionary mode requested for {parameter_file_parameter} but track is None!"
                    key = f"{sensor}_{asc_dsc}_t{track:0>3d}"
                    value = eval(str(value))[key]
                elif parameter_file_parameter[1] == "strip":
                    assert len(parameter_file_parameter) > 2, (
                        f"Strip mode for parameter {parameter_file_parameter} "
                        "requested but no string of characters to strip provided!"
                    )
                    assert isinstance(parameter_file_parameter[2], str), (
                        "Characters to strip from " f"{parameter_file_parameter} is not a string!"
                    )
                    value = str(value)
                    for strip_key in parameter_file_parameter[2]:
                        value = value.replace(strip_key, "")
                else:
                    raise ValueError(
                        f"Unknown parameter mode {parameter_file_parameter[1]}! Known are lowercase, "
                        "uppercase, dictionary, strip."
                    )
                template_data = template_data.replace(f"**{parameter_file_parameter[0]}**", str(value))
            else:
                raise ValueError(
                    f"Allowed types are str and list, got {type(parameter_file_parameter)} as parameter file"
                    "parameter instead!"
                )

    if config_parameters is not None:
        for config_parameter in config_parameters:
            template_data = template_data.replace(
                f"**{config_parameter.lower()}**", str(CONFIG_PARAMETERS[config_parameter.upper()])
            )

    if other_parameters is not None:
        for other_parameter in other_parameters.keys():
            template_data = template_data.replace(f"**{other_parameter}**", str(other_parameters[other_parameter]))

    fw = open(save_path, "w")
    fw.write(template_data)
    fw.close()


def read_SLC_json(filename: str) -> list:
    """Read the json dump from an SLC zip file and extract the bounding box.

    Parameters
    ----------
    filename: str
        Full path to the json file

    Returns
    -------
    list
        List with the coordinates of the bounding box

    Raises
    ------
    AssertionError
        - When the filename does not exist
        - When the filename does not end in .json
    """
    assert os.path.exists(filename), f"Specified parameter file {filename} does not exist!"
    assert filename.split(".")[-1] == "json", f"Specified parameter file {filename} is not a .json file!"

    f = open(filename)
    data = json.load(f)
    f.close()

    return data["geometry"]["coordinates"][0]


def read_SLC_xml(filename: str) -> list:
    """Read the XML dump from an SLC zip file and extract the bounding box.

    Parameters
    ----------
    filename: str
        Name of the json file

    Returns
    -------
    list
        List with the coordinates of the bounding box

    Raises
    ------
    AssertionError
        - When the filename does not exist
        - When the filename does not end in .xml
    ValueError
        If the footprint attribute cannot be found in the XML
    """
    assert os.path.exists(filename), f"Specified parameter file {filename} does not exist!"
    assert filename.split(".")[-1] == "xml", f"Specified parameter file {filename} is not a .xml file!"

    tree = ET.parse(filename)
    root = tree.getroot()
    for idx in range(len(root)):
        if "name" in root[idx].attrib.keys():
            if root[idx].attrib["name"] == "footprint":
                data = root[idx].text.split("(")[-1].split(")")[0]
                coordinates = data.split(",")
                coordinates = [coordinate.strip().split(" ") for coordinate in coordinates]
                return coordinates

    raise ValueError(f"Cannot find footprint in {filename}!")


def read_shp_extent(filename: str, shp_type: str = "swath") -> dict:
    """Read the extent of the polygons in a shapefile.

    Parameters
    ----------
    filename: str
        Full path to the shapefile
    shp_type: str, optional
        Switch to check for specific shapefiles. In mode "swath", a name layer is expected in the shapefile. Otherwise,
        polygons are simply numbered. Default "swath"

    Returns
    -------
    dict
        Dictionary with as keys the names / numbers of the polygons, as value the list of bounding box coordinates

    Raises
    ------
    AssertionError
        - When the filename does not exist
        - When the filename does not end in .shp
    NotImplementedError
        - When a geometry that is not a Polygon or MultiPolygon is encountered
    """
    assert os.path.exists(filename), f"Specified parameter file {filename} does not exist!"
    assert filename.split(".")[-1] == "shp", f"Specified parameter file {filename} is not a .shp file!"

    shape = geopandas.read_file(filename)

    coordinate_dict = {}

    for i in range(len(shape)):
        if shp_type == "swath":
            name = shape["name"].get(i)
        else:
            name = str(i)
        geom = shape["geometry"].get(i)
        if geom.geom_type == "Polygon":
            boundary = geom.boundary.xy
            coordinates = [[boundary[0][i], boundary[1][i]] for i in range(len(boundary[0]))]
            coordinate_dict[name] = coordinates[:]
        elif geom.geom_type == "MultiPolygon":
            for n, sub_geom in enumerate(geom.geoms):  # these are polygons
                boundary = sub_geom.boundary.xy
                coordinates = [[boundary[0][i], boundary[1][i]] for i in range(len(boundary[0]))]
                coordinate_dict[f"{name}_part{n+1}"] = coordinates[:]
        else:
            raise NotImplementedError(f"Cannot read the extent of a {geom.geom_type}!")
    return coordinate_dict


def link_shapefile(output_directory: str, output_aoi_name: str, shape_file_path: str) -> None:
    """Link a shapefile based on provided parameters in the CAROLINE parameter file.

    Parameters
    ----------
    output_directory: str
        Directory where to link the shapefile in
    output_aoi_name: str
        Name of the output shapefile
    shape_file_path: str
        Location of the shapefile

    Raises
    ------
    AssertionError
        When the provided shape_file_path does not end in '.shp'

    """
    assert shape_file_path.split(".")[-1] == "shp", f"Provided shapefile {shape_file_path} does not end in .shp!"

    export_shp = f"{output_directory}/{output_aoi_name}_shape.shp"

    for appendix in ["shp", "prj", "shx", "dbf"]:
        os.system(f"ln -s {shape_file_path[:-4]}.{appendix} {export_shp[:-4]}.{appendix}")


def create_shapefile(
    output_directory: str,
    output_aoi_name: str,
    central_coord: list,
    crop_width: float | int,
    crop_length: float | int,
) -> None:
    """Create a square shapefile from scratch based on provided parameters in the CAROLINE parameter file.

    Parameters
    ----------
    output_directory: str
        Directory where to link the shapefile in
    output_aoi_name: str
        Name of the output shapefile
    central_coord: list
        List of the coordinates of the central AoI in [latitude, longitude]
    crop_width: float | int
        Width (east-west) of the AoI to be generated in km
    crop_length: float | int
        Length (north-south) of the AoI to be generated in km
    """
    export_shp = f"{output_directory}/{output_aoi_name}_shape.shp"

    # Calculate the limits of the AoI
    Dlat_m = 2 * pi * EARTH_RADIUS / 360  # m per degree of latitude

    N_limit = central_coord[0] + crop_length * 1000 / 2 / Dlat_m
    S_limit = central_coord[0] - crop_length * 1000 / 2 / Dlat_m

    # Set to the maximum width (in the northern hemisphere this is the south, in the southern it is the north
    W_limit = min(
        central_coord[1] - crop_width * 1000 / 2 / (Dlat_m * cos(radians(N_limit))),
        central_coord[1] - crop_width * 1000 / 2 / (Dlat_m * cos(radians(S_limit))),
    )
    E_limit = max(
        central_coord[1] + crop_width * 1000 / 2 / (Dlat_m * cos(radians(N_limit))),
        central_coord[1] + crop_width * 1000 / 2 / (Dlat_m * cos(radians(S_limit))),
    )

    # make a square
    coords = [[W_limit, N_limit], [E_limit, N_limit], [E_limit, S_limit], [W_limit, S_limit], [W_limit, N_limit]]

    # create the shapefile
    schema = {"geometry": "Polygon"}

    shapefile = fiona.open(export_shp, mode="w", driver="ESRI Shapefile", schema=schema, crs="EPSG:4326")

    rows = {"geometry": {"type": "Polygon", "coordinates": [coords]}}

    shapefile.write(rows)
    shapefile.close()


def parse_start_files(new_insar_files_file: str, force_start_file: str) -> tuple[dict, list]:
    """Read the two start files to start jobs.

    Parameters
    ----------
    new_insar_files_file: str
        Full path to the file containing newly detected InSAR files (output from `find-new-insar-files.sh`
    force_start_file: str
        Full path to the file containing AoIs that should be force-started

    Returns
    -------
    tuple[dict, list]
        The dictionary contains the tracks detected with new images, with the tracks as keys and the extent(s) of the
        new images as a list as argument, the list contains the track/AoI combinations that should be force-started
    """
    f = open(new_insar_files_file)
    data = f.read()
    f.close()
    if "No new complete downloads found" in data:
        new_tracks_dict = {}
    else:
        # first find SLCs we already have started on to prevent double starts
        f = open(f"{CONFIG_PARAMETERS['CAROLINE_WORK_DIRECTORY']}/slcs-detected.csv")
        detected_slcs = f.read()
        f.close()

        new_tracks_dict = {}
        lines = data.split("\n")
        for line in lines:
            if CONFIG_PARAMETERS["SLC_BASE_DIRECTORY"] in line:
                track = line.split(CONFIG_PARAMETERS["SLC_BASE_DIRECTORY"])[1].split("/")[1]

                # check if the image was acquired in the last 30 days: if not, we do not want to start
                date = line.split(CONFIG_PARAMETERS["SLC_BASE_DIRECTORY"])[1].split("/")[3]
                today = dt.datetime.now().strftime("%Y%m%d")
                delta_t = dt.datetime.strptime(today, "%Y%m%d") - dt.datetime.strptime(date, "%Y%m%d")
                if delta_t.days <= DELTA_T_SLC_LIMIT:
                    polarisation = line.split(CONFIG_PARAMETERS["SLC_BASE_DIRECTORY"])[1].split("/")[2]
                    if polarisation in ALLOWED_S1_POLARISATIONS:
                        # date and polarisation are okay, let's check if this track has not been previously started
                        json_file = line.split(".")[0] + ".json"
                        json_timestamp = time.ctime(os.path.getmtime(json_file))
                        search_key = f"{line};{json_timestamp}"
                        if search_key not in detected_slcs:  # we have not already triggered on this one, so let's start
                            if track not in new_tracks_dict.keys():
                                new_tracks_dict[track] = []

                            new_tracks_dict[track].append(
                                [
                                    line.split(CONFIG_PARAMETERS["SLC_BASE_DIRECTORY"])[1].split("/")[4],
                                    read_SLC_json(json_file),
                                ]
                            )

                            os.system(
                                """echo "$(date '+%Y-%m-%dT%H:%M:%S');"""
                                """$(whoami);"""
                                f"""{line};"""
                                f"""{json_timestamp}" """
                                f""">> {CONFIG_PARAMETERS["CAROLINE_WORK_DIRECTORY"]}/slcs-detected.csv"""
                            )
                            os.system(
                                """echo "$(date '+%Y-%m-%dT%H:%M:%S'): SCHEDULER """
                                f"""detected original SLC {line} """
                                """and has accepted it as a new original SLC, """
                                """so its overlapping AoIs will start." """
                                f""">> {CONFIG_PARAMETERS["CAROLINE_WORK_DIRECTORY"]}/submitted_jobs.log"""
                            )
                        else:
                            os.system(
                                """echo "$(date '+%Y-%m-%dT%H:%M:%S'): SCHEDULER """
                                f"""detected original SLC {line} """
                                """but this original SLC has already been logged as detected, """
                                """so original SLC is ignored." """
                                f""">> {CONFIG_PARAMETERS["CAROLINE_WORK_DIRECTORY"]}/submitted_jobs.log"""
                            )
                    else:
                        os.system(
                            """echo "$(date '+%Y-%m-%dT%H:%M:%S'): SCHEDULER """
                            f"""detected original SLC {line} """
                            f"""but polarisation of {polarisation} is not in {ALLOWED_S1_POLARISATIONS}, """
                            """so original SLC is ignored." """
                            f""">> {CONFIG_PARAMETERS["CAROLINE_WORK_DIRECTORY"]}/submitted_jobs.log"""
                        )
                else:
                    os.system(
                        """echo "$(date '+%Y-%m-%dT%H:%M:%S'): SCHEDULER """
                        f"""detected original SLC {line} """
                        f"""but Delta T of {delta_t} exceeds limit of {DELTA_T_SLC_LIMIT}, """
                        """so original SLC is ignored." """
                        f""">> {CONFIG_PARAMETERS["CAROLINE_WORK_DIRECTORY"]}/submitted_jobs.log"""
                    )

    f = open(force_start_file)
    data = f.read().split("\n")
    f.close()
    new_force_starts = []
    for line in data:
        if line != "":
            aoi = line.split(";")[0]
            tracks = line.split(";")[1].split(",")
            for track in tracks:
                new_force_starts.append([track, aoi])

    return new_tracks_dict, new_force_starts
