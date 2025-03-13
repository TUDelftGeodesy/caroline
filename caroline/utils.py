import glob
import zipfile
from typing import Literal

from caroline.io import create_shapefile, link_shapefile, read_parameter_file


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


def identify_incomplete_sentinel1_images(parameter_file: str):
    """Identify incomplete Sentinel-1 image downloads to prevent Doris v5 crashing.

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
            asc_dsc,
            track,
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

        f = open(f"{base_folder}/good_images/bad_zips.txt", "w")
        for zipp in bad_zips:
            f.write(f"{zipp}\n")
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
