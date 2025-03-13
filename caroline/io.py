import json
import os
import xml.etree.ElementTree as ET

import geopandas


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
    shp_type: str
        Switch to check for specific shapefiles. In mode "swath", a name layer is expected in the shapefile. Otherwise,
        polygons are simply numbered.

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
