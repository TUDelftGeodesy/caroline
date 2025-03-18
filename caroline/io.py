import json
import os
import xml.etree.ElementTree as ET
from math import cos, pi, radians
from typing import Literal

import fiona
import geopandas
import numpy as np

CONFIG_PARAMETERS = {
    "CAROLINE_WORK_DIRECTORY": "/project/caroline/Software/run/caroline/work",
    "SLC_BASE_DIRECTORY": "/project/caroline/Data/radar_data/sentinel1",
    "CAROLINE_INSTALL_DIRECTORY": "/project/caroline/Software/caroline",
}
EARTH_RADIUS = 6378136  # m


def read_parameter_file(parameter_file: str, search_parameters: list) -> dict:
    """Read parameters from a CAROLINE parameter file into a dictionary.

    Parameters
    ----------
    parameter_file : str
        Absolute path to the CAROLINE parameter file in .txt format
    search_parameters: list
        Parameter names to be retrieved from the parameter file, as a list of strings

    Returns
    -------
    dict
        Dictionary containing the values of the requested parameters. If an invalid parameter is requested,
        `None` is returned for that parameter.

    Raises
    ------
    AssertionError
        - When the parameter file does not exist
        - When the parameter file does not end in .txt

    ValueError
        - When a requested parameter does not exist in the parameter file
    """
    assert os.path.exists(parameter_file), f"Specified parameter file {parameter_file} does not exist!"
    assert parameter_file.split(".")[-1] == "txt", f"Specified parameter file {parameter_file} is not a .txt file!"

    fp = open(parameter_file)
    parameters = fp.read().split("\n")
    fp.close()

    out_parameters = {}

    for param in search_parameters:
        found = False
        for p in parameters:
            if p.split("=")[0].strip() == param:
                do = p.split("=")[1]
                if "#" in do:
                    do = do.split("#")[0]
                do = do.strip().strip("'").strip('"')
                out_parameters[param] = do
                found = True
                break
        if not found:
            raise ValueError(f"Parameter {param} requested but not in {parameter_file}!")

    return out_parameters


def write_run_file(
    save_path: str,
    template_path: str,
    asc_dsc: Literal["asc", "dsc"],
    track: int,
    parameter_file: str,
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
    asc_dsc: Literal["asc", "dsc"]
        Whether the file is generated for an ascending or descending track
    track: int
        Which track the file is generated for
    parameter_file: str
        Full path to the parameter file
    parameter_file_parameters: list
        List of parameters to be read from the parameter file. Two options are available for each element in the list:
        - "parameter_name" - outputs the value of the parameter directly into the template
        - ["parameter_name", "mode"] - formats the parameter value before pasting it into the template. Three options
          are available:
          - "lowercase" - formats the parameter value into lowercase symbols.
          - "uppercase" - formats the parameter value into uppercase symbols.
          - "dictionary" - signals the parameter value is a dictionary. The key `sensor`_`asc_dsc`_t`track:0>3d` is
            expected. The value is the argument of this key.
    config_parameters: list
        List of configuration parameters to be pasted into the template. Currently avalailable are
        - `SLC_BASE_DIRECTORY`
        - `CAROLINE_WORK_DIRECTORY`
        - `CAROLINE_INSTALL_DIRECTORY`
    other_parameters: dict
        Dictionary with as keys the parameter name in the template, as argument the value it should be replaced by

    Raises
    ------
    ValueError
        - If an object that is not `str` or `list` is encountered in `parameter_file_parameters`
        - If an unknown mode of parameter formatting is encountered
    AssertionError
        - If an unknown configuration parameter is requested

    """
    if config_parameters is not None:
        assert np.all(
            [config_parameter.upper() in CONFIG_PARAMETERS.keys() for config_parameter in config_parameters]
        ), f"Not all config parameters in {config_parameters} are known! Known are {CONFIG_PARAMETERS.keys()}."

    ft = open(template_path)
    template_data = ft.read()
    ft.close()

    if parameter_file_parameters is not None:
        for parameter_file_parameter in parameter_file_parameters:
            if isinstance(parameter_file_parameter, str):
                value = read_parameter_file(parameter_file, [parameter_file_parameter])[parameter_file_parameter]
                template_data.replace(f"**{parameter_file_parameter}**", value)
            elif isinstance(parameter_file_parameter, list):
                value = read_parameter_file(parameter_file, [parameter_file_parameter[0]])[parameter_file_parameter[0]]
                if parameter_file_parameter[1] == "force_lowercase":
                    value = value.lower()
                elif parameter_file_parameter[1] == "force_uppercase":
                    value = value.upper()
                elif parameter_file_parameter[1] == "dictionary":
                    sensor = read_parameter_file(parameter_file, ["sensor"])["sensor"].lower()
                    key = f"{sensor}_{asc_dsc}_t{track:0>3d}"
                    value = eval(value)[key]
                else:
                    raise ValueError(
                        f"Unknown parameter mode {parameter_file_parameter[1]}! Known are force_lowercase, "
                        "force_uppercase, dictionary."
                    )
                template_data.replace(f"**{parameter_file_parameter[0]}", value)
            else:
                raise ValueError(
                    f"Allowed types are str and list, got {type(parameter_file_parameter)} as parameter file"
                    "parameter instead!"
                )

    if config_parameters is not None:
        for config_parameter in config_parameters:
            template_data.replace(f"**{config_parameter.lower()}**", CONFIG_PARAMETERS[config_parameter.upper()])

    if other_parameters is not None:
        for other_parameter in other_parameters.keys():
            template_data.replace(f"**{other_parameter}**", other_parameters[other_parameter])

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

    AssertionError
        - When the filename does not exist
        - When the filename does not end in .shp
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
        boundary = geom.boundary.xy
        coordinates = [[boundary[0][i], boundary[1][i]] for i in range(len(boundary[0]))]

        coordinate_dict[name] = coordinates[:]

    return coordinate_dict


def link_shapefile(parameter_file: str):
    """Link a shapefile based on provided parameters in the CAROLINE parameter file.

    Parameters
    ----------
    parameter_file: str
        Full path to the CAROLINE parameter file.

    """
    search_parameters = ["shape_file", "shape_directory", "shape_AoI_name"]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    assert (
        out_parameters["shape_file"].split(".")[-1] == "shp"
    ), f"Provided shapefile {out_parameters['shape_file']} does not end in .shp!"

    export_shp = f"{out_parameters['shape_directory']}/{out_parameters['shape_AoI_name']}_shape.shp"

    for appendix in ["shp", "prj", "shx", "dbf"]:
        os.system(f"ln -s {out_parameters['shape_file'][:-4]}.{appendix} {export_shp[:-4]}.{appendix}")


def create_shapefile(parameter_file: str):
    """Create a square shapefile from scratch based on provided parameters in the CAROLINE parameter file.

    Parameters
    ----------
    parameter_file: str
        Full path to the CAROLINE parameter file.

    """
    search_parameters = ["center_AoI", "AoI_length", "AoI_width", "shape_directory", "shape_AoI_name"]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    export_shp = f"{out_parameters['shape_directory']}/{out_parameters['shape_AoI_name']}_shape.shp"

    central_coord = eval(out_parameters["center_AoI"])
    crop_length = eval(out_parameters["AoI_length"])
    crop_width = eval(out_parameters["AoI_width"])

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
