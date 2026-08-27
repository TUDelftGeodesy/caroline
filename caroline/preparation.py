import datetime as dt
import glob
import os
import sys
import zipfile

import numpy as np

from caroline.config import get_config
from caroline.io import create_shapefile, link_shapefile, read_parameter_file, read_shp_extent, write_run_file
from caroline.kml import KML
from caroline.parameter_file import generate_full_parameter_file
from caroline.utils import (
    convert_shp_to_wkt,
    detect_sensor_pixelsize,
    format_process_folder,
    generate_email,
    haversine,
    identify_s1_orbits_in_aoi,
    remove_incomplete_sentinel1_images,
    write_directory_contents,
)

CONFIG_PARAMETERS = get_config()
JOB_DEFINITIONS = get_config(
    f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False
)["jobs"]

S1_DOWNLOAD_CALL_REPEAT_LIMIT = 20  # the number of times Caroline restarts the call to caroline-download before
# reporting a failed process


def finish_installation() -> None:
    """Generate the shapefiles and `area-track-lists` during installation for all AoIs."""
    parameter_files = glob.glob(f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/parameter-files/param-file*")

    # create the directories
    os.makedirs(f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/area-track-lists", exist_ok=True)
    os.makedirs(f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/periodic", exist_ok=True)
    os.makedirs(f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/once", exist_ok=True)

    # create the generic download configuration
    write_run_file(
        save_path=f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/download-config.yaml",
        template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/download/download-config.yaml",
        track=None,
        asc_dsc=None,
        parameter_file=None,
        config_parameters=["slc_base_directory", "caroline_work_directory"],
    )

    # check which download configs exist, so we can remove the ones we don't need later on
    to_be_removed_download_configurations = glob.glob(
        f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/periodic/*"
    )

    # Retrieve the job definition keys
    job_definitions = get_config(
        f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False
    )["jobs"]
    job_keys = list(
        set(
            [
                job_definitions[job]["parameter-file-step-key"]
                for job in job_definitions.keys()
                if job_definitions[job]["parameter-file-step-key"] is not None
            ]
        )
    )

    for parameter_file in parameter_files:
        aoi_name = parameter_file.split("/")[-1].split("param-file-")[-1].split(".")[0].replace("-", "_")

        os.system('''echo ""''')
        os.system('''echo ""''')
        os.system(f'''echo "Processing AoI {aoi_name}..."''')

        # first generate the shapefile if it does not yet exist
        parameter_file_parameters = generate_full_parameter_file(parameter_file, 0, "asc", "dummy.yaml", "dict")

        # first create the directory
        os.makedirs(parameter_file_parameters["general"]["shape-file"]["directory"], exist_ok=True)

        shapefile_name = (
            f"{parameter_file_parameters['general']['shape-file']['directory']}/"
            f"{parameter_file_parameters['general']['shape-file']['aoi-name']}_shape.shp"
        )
        # then create or link the shapefile
        if not os.path.exists(shapefile_name):
            if parameter_file_parameters["general"]["shape-file"]["shape-file-link"] in [None, "", "None"]:
                create_shapefile(
                    parameter_file_parameters["general"]["shape-file"]["directory"],
                    parameter_file_parameters["general"]["shape-file"]["aoi-name"],
                    parameter_file_parameters["general"]["shape-file"]["rectangular-shape-file"]["center-AoI"],
                    parameter_file_parameters["general"]["shape-file"]["rectangular-shape-file"]["AoI-width"],
                    parameter_file_parameters["general"]["shape-file"]["rectangular-shape-file"]["AoI-length"],
                )
            else:
                link_shapefile(
                    parameter_file_parameters["general"]["shape-file"]["directory"],
                    parameter_file_parameters["general"]["shape-file"]["aoi-name"],
                    parameter_file_parameters["general"]["shape-file"]["shape-file-link"],
                )

        # determine if the parameter file is active or not, if not, we skip the area-track-list generation

        active_parameter_file = parameter_file_parameters["general"]["active"]

        if active_parameter_file == 0:
            continue

        # then check if the AoI is a Sentinel-1 AoI or something else

        sensor = parameter_file_parameters["general"]["input-data"]["sensor"]

        if sensor == "S1":
            # then determine the intersecting orbits
            orbits, footprints = identify_s1_orbits_in_aoi(shapefile_name)
            allowed_footprints = {}
            disallowed_footprints = {}
            disallowed_orbits = parameter_file_parameters["general"]["tracks"]["exclude-tracks"]
            forced_orbits = parameter_file_parameters["general"]["tracks"]["include-tracks"]
            for orbit in disallowed_orbits:
                if orbit in orbits:
                    orbits.pop(orbits.index(orbit))
                    disallowed_footprints[orbit] = footprints[orbit]
            for orbit in forced_orbits:
                if orbit not in orbits:
                    orbits.append(orbit)
                    allowed_footprints[orbit] = []
            for orbit in orbits:
                if orbit not in allowed_footprints.keys():
                    allowed_footprints[orbit] = footprints[orbit]
            orbits = list(sorted(orbits))

            os.system(f'''echo "Detected (and forced) orbits {orbits}"''')
            os.system(f'''echo "Rejected orbits {[k for k in disallowed_footprints.keys()]}"''')

            # generate the overlap KML
            now = dt.datetime.now()
            now_str = now.strftime("%Y%m%d")

            kml = KML(f"{CONFIG_PARAMETERS['AOI_OVERVIEW_DIRECTORY']}/SLC_overlap_{aoi_name}_{now_str}.kml")
            kml.open_folder("AoI", "Extent of the AoI")
            kml.add_polygon(read_shp_extent(shapefile_name, shp_type="AoI")["0"], f"{aoi_name}", "", "stack")
            kml.close_folder()

            kml.open_folder("Accepted tracks", "Extents of the original SLCs on the accepted tracks")
            for key in list(sorted(list(allowed_footprints.keys()))):
                if len(allowed_footprints[key]) == 0:
                    kml.open_folder(key, f"Track {key} was forced and has no footprints.")
                else:
                    kml.open_folder(key, "")
                    for n, footprint in enumerate(allowed_footprints[key]):
                        kml.add_polygon(
                            footprint, f"Track {key}, footprint {n+1}", f"Extent of detected original SLC {n+1}", "AoI"
                        )

                kml.close_folder()
            kml.close_folder()

            kml.open_folder("Rejected tracks", "Extents of the original SLCs on the rejected tracks")
            for key in list(sorted(list(disallowed_footprints.keys()))):
                kml.open_folder(key, "")
                for n, footprint in enumerate(disallowed_footprints[key]):
                    kml.add_polygon(
                        footprint, f"Track {key}, footprint {n + 1}", f"Extent of detected original SLC {n + 1}", "SLC"
                    )

                kml.close_folder()
            kml.close_folder()
            kml.save()

            jobs_to_do = {}
            # then figure out if this is a download-only job, a non-download job, or a mix job
            for job_key in job_keys:
                keys = job_key.split(":")
                value = parameter_file_parameters
                for key in keys:
                    value = value[key]
                jobs_to_do[job_key] = value

            if jobs_to_do[job_definitions["s1_download"]["parameter-file-step-key"]] == 1:
                # This is a download job -> we want a download configuration
                # first make sure it doesn't get removed if it already exists
                if (
                    f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/periodic/{aoi_name}"
                    in to_be_removed_download_configurations
                ):
                    to_be_removed_download_configurations.pop(
                        to_be_removed_download_configurations.index(
                            f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/periodic/{aoi_name}"
                        )
                    )

                # then add the download configuration
                os.makedirs(
                    f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/periodic/{aoi_name}",
                    exist_ok=True,
                )
                write_run_file(
                    save_path=(
                        f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/periodic/{aoi_name}/roi.wkt"
                    ),
                    template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/download/roi.wkt",
                    asc_dsc=None,
                    track=None,
                    parameter_file=None,
                    other_parameters={"wkt_string": convert_shp_to_wkt(shapefile_name)},
                )

                write_run_file(
                    save_path=(
                        f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/"
                        f"periodic/{aoi_name}/geosearch.yaml"
                    ),
                    template_path=(
                        f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/download/geosearch.yaml"
                    ),
                    asc_dsc=None,
                    track=None,
                    parameter_file=None,
                    other_parameters={
                        "general:timeframe:start": "one month ago",
                        "wkt_file": (
                            f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/"
                            f"periodic/{aoi_name}/roi.wkt"
                        ),
                        "orbits_csv": ", ".join([o.split("_t")[-1].lstrip("0") for o in orbits]),
                        "general:input-data:product-type": parameter_file_parameters["general"]["input-data"][
                            "product-type"
                        ],
                    },
                )

            if 1 in [
                jobs_to_do[job]
                for job in jobs_to_do.keys()
                if job != job_definitions["s1_download"]["parameter-file-step-key"]
            ]:
                # This runs something else besides download -> we want an area-track-list
                write_run_file(
                    save_path=(
                        f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/area-track-lists/{aoi_name}.dat"
                    ),
                    template_path=(
                        f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/"
                        "area-track-list/area-track-list.dat"
                    ),
                    asc_dsc=None,
                    track=None,
                    parameter_file=parameter_file,
                    parameter_file_parameters=["general:workflow:dependency:aoi-name"],
                    other_parameters={
                        "tracks": "\n".join(orbits),
                        "general:workflow:dependency:aoi-name": parameter_file_parameters["general"]["workflow"][
                            "dependency"
                        ]["aoi-name"],
                    },
                )

        else:
            include_tracks = parameter_file_parameters["general"]["tracks"]["include-tracks"]
            write_run_file(
                save_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/area-track-lists/{aoi_name}.dat",
                template_path=(
                    f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/area-track-list/area-track-list.dat"
                ),
                asc_dsc=None,
                track=None,
                parameter_file=parameter_file,
                parameter_file_parameters=["general:workflow:dependency:aoi-name"],
                other_parameters={
                    "tracks": "\n".join(include_tracks),
                    "general:workflow:dependency:aoi-name": parameter_file_parameters["general"]["workflow"][
                        "dependency"
                    ]["aoi-name"],
                },
            )
            os.system(f'''echo "Including tracks {include_tracks}"''')

    for download_config in to_be_removed_download_configurations:
        # remove the existing download configurations that still exist but are no longer requested
        if os.path.exists(download_config):
            os.system(f'''echo "Removing no longer requested download config {download_config}..."''')
            os.system(f"rm -rf {download_config}")


def prepare_reduce_slc_matlab(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for cropping.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        crop_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["reduce_slc_matlab"], track=tracks[track]
        )

        if out_parameters["general:input-data:sensor"] == "S1":
            coregistration_directory = format_process_folder(
                parameter_file=parameter_file, job_description=JOB_DEFINITIONS["doris_v5"], track=tracks[track]
            )

        else:
            coregistration_directory = format_process_folder(
                parameter_file=parameter_file, job_description=JOB_DEFINITIONS["doris_v4"], track=tracks[track]
            )

        os.makedirs(crop_directory, exist_ok=True)

        # soft-link the processing directory without job_id.txt, dir_contents.txt and queue.txt
        # Sentinel-1 has more files starting with d as Doris-v5 output, other sensors do not have that
        if out_parameters["general:input-data:sensor"] == "S1":
            link_keys = ["[bgiprs]*", "doris*", "dem"]
        else:
            link_keys = ["[bgiprs]*"]
        for key in link_keys:
            # run the soft-link command
            os.system(f"ln -sfn {coregistration_directory}/{key} {crop_directory}")

        # generate crop.sh
        write_run_file(
            save_path=f"{crop_directory}/crop-to-raw.sh",
            template_path=(
                f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/reduce-slc-matlab/reduce-slc-matlab.sh"
            ),
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["reduce_slc_matlab:general:AoI-name"],
            config_parameters=["caroline_work_directory", "matlab_module"],
            other_parameters={"track": tracks[track], "crop_base_directory": crop_directory},
        )

        # generate crop.m
        write_run_file(
            save_path=f"{crop_directory}/reduce_slc_matlab.m",
            template_path=(
                f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/reduce-slc-matlab/reduce_slc_matlab.m"
            ),
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "general:shape-file:aoi-name",
                "general:shape-file:directory",
                "general:input-data:sensor",
            ],
            config_parameters=["caroline_install_directory"],
        )

        write_directory_contents(
            crop_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["reduce_slc_matlab"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_reduce_slc_python(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for reduce_slc_python.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file

    Raises
    ------
    ValueError
        If the mother image cannot be detected from doris_input.xml (S1) or doris_v4.py (otherwise)
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]
    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        reduce_slc_python_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["reduce_slc_python"], track=tracks[track]
        )

        if out_parameters["general:input-data:sensor"] == "S1":
            coregistration_directory = format_process_folder(
                parameter_file=parameter_file, job_description=JOB_DEFINITIONS["doris_v5"], track=tracks[track]
            )

        else:
            coregistration_directory = format_process_folder(
                parameter_file=parameter_file, job_description=JOB_DEFINITIONS["doris_v4"], track=tracks[track]
            )

        os.makedirs(reduce_slc_python_directory, exist_ok=True)

        # detect the mother image
        if out_parameters["general:input-data:sensor"].lower() == "s1":
            f = open(f"{coregistration_directory}/doris_input.xml")
            data = f.read().split("\n")
            f.close()
            mother = None
            for line in data:
                if "<master_date>" in line:
                    mother = line.split(">")[1].split("<")[0].replace("-", "")
                    break

            if mother is None:
                raise ValueError(f"Failed to detect mother in {coregistration_directory}/doris_input.xml!")

        else:
            f = open(f"{coregistration_directory}/run_doris_v4.py")
            data = f.read().split("\n")
            f.close()
            mother = None
            for line in data:
                if "master = " in line:
                    mother = line.split('"')[1]
                    break

            if mother is None:
                raise ValueError(f"Failed to detect mother in {coregistration_directory}/run_doris_v4.py !")

        # generate crop-to-zarr.py
        reduce_slc_python_output_name = reduce_slc_python_directory.split("/")[-1]

        write_run_file(
            save_path=f"{reduce_slc_python_directory}/reduce-slc-python.py",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/reduce-slc-python/reduce-slc-python.py",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "general:shape-file:aoi-name",
                "general:input-data:sensor",
                "general:shape-file:directory",
            ],
            other_parameters={
                "coregistration_directory": coregistration_directory,
                "stack_folder_name": "stack" if out_parameters["general:input-data:sensor"] == "S1" else "process",
                "mother": mother,
                "mother_slc_name": "slave_rsmp_reramped.raw"
                if out_parameters["general:input-data:sensor"] == "S1"
                else "slave_rsmp.raw",
                "reduce_slc_python_output_filename": reduce_slc_python_output_name,
            },
        )

        # generate crop-to-zarr.sh
        write_run_file(
            save_path=f"{reduce_slc_python_directory}/reduce-slc-python.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/reduce-slc-python/reduce-slc-python.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "reduce_slc_python:general:AoI-name",
                "reduce_slc_python:general:depsi_group-code-directory",
            ],
            config_parameters=[
                "caroline_work_directory",
                "caroline_virtual_environment_directory",
                "python3_module",
                "gdal_module",
            ],
            other_parameters={"track": tracks[track]},
        )

        write_directory_contents(
            reduce_slc_python_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["reduce_slc_python"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_doris_v4(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for doris_v4.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file

    Raises
    ------
    AssertionError
        If one of the tracks is not provided in `di_data_directories`
    ValueError
        If an unknown sensor is provided in the parameter file
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
        "doris_v4:input:data-directories",
        "general:timeframe:start",
        "general:timeframe:end",
        "general:timeframe:mother",
        "general:dem:file",
        "general:dem:upperleft",
        "general:dem:delta",
        "general:shape-file:directory",
        "general:shape-file:aoi-name",
        "doris_v4:doris_v4-settings:finecoreg:finecoreg-mode",
        "default:input-data:polarisation",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]

    datadirs = out_parameters["doris_v4:input:data-directories"]

    start_date = eval(out_parameters["general:timeframe:start"].replace("-", ""))
    master_date = eval(out_parameters["general:timeframe:mother"].replace("-", ""))
    end_date = eval(out_parameters["general:timeframe:end"].replace("-", ""))

    polarisation = out_parameters["general:input-data:polarisation"]
    polarisation = [f"_{pol}" for pol in polarisation]
    if "_HH" in polarisation:
        polarisation[polarisation.index("_HH")] = ""

    dem_delta = out_parameters["general:dem:delta"]
    dem_size = out_parameters["general:dem:size"]
    dem_upperleft = out_parameters["general:dem:upperleft"]

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        assert (
            f"{out_parameters['general:input-data:sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}"
            in datadirs.keys()
        ), (
            f"{out_parameters['general:input-data:sensor'].lower()}_"
            f"{asc_dsc[track]}_t{tracks[track]:0>3d} is not in doris_v4:input:data-directories!"
        )

        coregistration_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["doris_v4"], track=tracks[track]
        )

        # we need a process folder in the coregistration directory, so we can combine that command
        os.makedirs(f"{coregistration_directory}/process", exist_ok=True)

        # generate doris_v4.sh
        write_run_file(
            save_path=f"{coregistration_directory}/run_doris_v4.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/doris_v4/run_doris_v4.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "doris_v4:general:deinsar-code-directory",
                "doris_v4:general:doris-v4-code-directory",
                "doris_v4:general:AoI-name",
            ],
            config_parameters=["caroline_work_directory", "orbit_directory", "python2_module", "gdal_module"],
            other_parameters={"track": tracks[track], "coregistration_base_directory": coregistration_directory},
        )

        # generate run_doris_v4.py

        # first search for the start, end, and master dates by parsing all data in the data directory,
        # which is different per sensor
        datadir = datadirs[
            f"{out_parameters['general:input-data:sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}"
        ]
        if out_parameters["general:input-data:sensor"] in ["ALOS2", "ERS"]:
            dirs = glob.glob(f"{datadir}/[12]*")
            images = list(sorted([eval(image.split("/")[-1]) for image in dirs]))
        elif out_parameters["general:input-data:sensor"] in ["RSAT2"]:
            dirs = glob.glob(f"{datadir}/RS2*")
            images = list(sorted([eval(image.split("/")[-1].split("FQ2_")[1].split("_")[0]) for image in dirs]))
        elif out_parameters["general:input-data:sensor"] in ["TSX"]:
            dirs = glob.glob(f"{datadir}/*/iif/*")
            images = list(sorted([eval(image.split("/")[-1].split("SRA_")[1].split("T")[0]) for image in dirs]))
        elif out_parameters["general:input-data:sensor"] in ["SAOCOM"]:
            dirs = glob.glob(f"{datadir}/*/*.xemt")
            images = list(sorted([eval(image.split("/")[-1].split("OLF_")[1].split("T")[0]) for image in dirs]))
        elif out_parameters["general:input-data:sensor"] in ["ENV"]:
            # 2 different formats for some reason
            dirs1 = glob.glob(f"{datadir}/*.N1")
            dirs2 = glob.glob(f"{datadir}/*/*.N1")
            dirs = []
            for d in dirs1:
                dirs.append(d)
            for d in dirs2:
                dirs.append(d)
            images = list(sorted([eval(image.split("/")[-1].split("PA")[1].split("_")[0]) for image in dirs]))
        else:
            raise ValueError(f'Unknown directory format for sensor {out_parameters["general:input-data:sensor"]}!')

        # then select the start, end, and master dates
        act_start_date = str(min([image for image in images if image >= start_date]))
        act_end_date = str(max([image for image in images if image <= end_date]))
        act_master_date = str(min([image for image in images if image >= master_date]))

        # finally, write run_doris_v4.py
        write_run_file(
            save_path=f"{coregistration_directory}/run_doris_v4.py",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/doris_v4/run_doris_v4.py",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                ["doris_v4:input:data-directories", "dictionary"],
                "general:input-data:sensor",
                "general:input-data:polarisation",
                "doris_v4:doris_v4-settings:do-orbit",
                "doris_v4:doris_v4-settings:do-crop",
                "doris_v4:doris_v4-settings:do-tsx-deramp",
                "doris_v4:doris_v4-settings:do-simamp",
                "doris_v4:doris_v4-settings:do-mtiming",
                "doris_v4:doris_v4-settings:do-ovs",
                "doris_v4:doris_v4-settings:do-choose-master",
                "doris_v4:doris_v4-settings:do-coarseorb",
                "doris_v4:doris_v4-settings:do-coarsecorr",
                "doris_v4:doris_v4-settings:finecoreg:do-finecoreg",
                "doris_v4:doris_v4-settings:do-reltiming",
                "doris_v4:doris_v4-settings:do-dembased",
                "doris_v4:doris_v4-settings:do-coregpm",
                "doris_v4:doris_v4-settings:do-comprefpha",
                "doris_v4:doris_v4-settings:do-comprefdem",
                "doris_v4:doris_v4-settings:do-resample",
                "doris_v4:doris_v4-settings:do-tsx-reramp",
                "doris_v4:doris_v4-settings:do-interferogram",
                "doris_v4:doris_v4-settings:do-subtrrefpha",
                "doris_v4:doris_v4-settings:do-subtrrefdem",
                "doris_v4:doris_v4-settings:do-coherence",
                "doris_v4:doris_v4-settings:do-geocoding",
            ],
            other_parameters={"master": act_master_date, "startdate": act_start_date, "enddate": act_end_date},
        )

        # finally, create the input files

        # these ones can be copied directly
        for file in [
            "input.baselines",
            "input.coarsecorr",
            "input.coarseorb",
            "input.comprefpha",
            "input.coregpm",
            "input.mtiming",
            "input.reltiming",
            "input.geocoding",
        ]:
            write_run_file(
                save_path=f"{coregistration_directory}/process/{file}",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/doris_v4/input_files/{file}",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
            )

        # these ones are polarisation-dependent
        for file in ["input.coherence", "input.interferogram", "input.subtrrefdem", "input.subtrrefpha", "input.ovs"]:
            for pol in polarisation:
                write_run_file(
                    save_path=f"{coregistration_directory}/process/{file}{pol}",
                    template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                    f"templates/doris_v4/input_files/{file}",
                    asc_dsc=asc_dsc[track],
                    track=tracks[track],
                    parameter_file=parameter_file,
                    other_parameters={"pol": pol},
                )

        # these ones need the DEM variables
        for file in ["input.comprefdem", "input.dembased", "input.simamp"]:
            write_run_file(
                save_path=f"{coregistration_directory}/process/{file}",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/doris_v4/input_files/{file}",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
                parameter_file_parameters=["general:dem:file", "general:dem:format", "general:dem:nodata"],
                other_parameters={
                    "dem_s1": dem_size[0],
                    "dem_s2": dem_size[1],
                    "dem_d1": dem_delta[0],
                    "dem_d2": dem_delta[1],
                    "dem_ul1": dem_upperleft[0],
                    "dem_ul2": dem_upperleft[1],
                },
            )

        # finecoreg changes based on the fine coregistration mode
        if out_parameters["doris_v4:doris_v4-settings:finecoreg:finecoreg-mode"] == "simple":
            write_run_file(
                save_path=f"{coregistration_directory}/process/input.finecoreg_simple",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                f"templates/doris_v4/input_files/input.finecoreg",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
                other_parameters={"nwin": 5000},
            )
        else:  # normal mode
            write_run_file(
                save_path=f"{coregistration_directory}/process/input.finecoreg",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                f"templates/doris_v4/input_files/input.finecoreg",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
                other_parameters={"nwin": 8000},
            )

        # porbit is only necessary for ERS and ENV
        if out_parameters["general:input-data:sensor"] == "ERS":
            # this one requires two copies
            for satellite in [1, 2]:
                write_run_file(
                    save_path=f"{coregistration_directory}/process/input.porbit_ERS{satellite}",
                    template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                    f"templates/doris_v4/input_files/input.porbit",
                    asc_dsc=asc_dsc[track],
                    track=tracks[track],
                    parameter_file=parameter_file,
                    other_parameters={"directory": f"ERS{satellite}"},
                )
        elif out_parameters["general:input-data:sensor"] == "ENV":
            write_run_file(
                save_path=f"{coregistration_directory}/process/input.porbit",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                f"templates/doris_v4/input_files/input.porbit",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
                other_parameters={"directory": "envisat/dor_vor_odr"},
            )

        # for input.crop and input.resample we need to read the shapefile extent and calculate the amount of pixels
        coordinates = np.array(
            read_shp_extent(
                f"{out_parameters['general:shape-file:directory']}/"
                f"{out_parameters['general:shape-file:aoi-name']}_shape.shp",
                shp_type="AoI",
            )["0"]
        )
        min_lat = min(coordinates[:, 1])
        max_lat = max(coordinates[:, 1])
        min_lon = min(coordinates[:, 0])
        max_lon = max(coordinates[:, 0])

        # get the central coordinates
        center_lon = (max_lon + min_lon) / 2
        center_lat = (max_lat + min_lat) / 2

        # get the latitude at which the crop is widest
        if min_lat < 0:
            if max_lat > 0:
                ref_lat = 0
            else:
                ref_lat = max_lat
        else:
            ref_lat = min_lat

        # calculate the extent of the AoI
        dist_lat = haversine(min_lat, max_lat, min_lon, min_lon)
        dist_lon = haversine(ref_lat, ref_lat, min_lon, max_lon)  # calculated at the widest part of the AoI

        # determine the number of pixels
        d_az, d_r = detect_sensor_pixelsize(out_parameters["general:input-data:sensor"])
        pix_dr = int(np.ceil(dist_lon / d_r * 1.05))
        pix_daz = int(np.ceil(dist_lat / d_az * 1.05))

        # for input.crop we will add 500 to eliminate edge effects
        if out_parameters["general:input-data:sensor"] == "ALOS2":
            img_name = "IMG.1"
        elif out_parameters["general:input-data:sensor"] == "Cosmo":
            img_name = "image.h5"
        elif out_parameters["general:input-data:sensor"] == "ENV":
            img_name = "image.N1"
        elif out_parameters["general:input-data:sensor"] == "ERS":
            img_name = "DAT_01.001"
        elif out_parameters["general:input-data:sensor"] == "RSAT2":
            img_name = "imagery{pol}.tif"
            # requires loop over polarisations to get additional crop files
        elif out_parameters["general:input-data:sensor"] == "TSX":
            img_name = "image.cos"
        else:
            raise ValueError(f'Unknown sensor {out_parameters["general:input-data:sensor"]}!')

        # write input.crop
        if (
            out_parameters["general:input-data:sensor"] == "RSAT2"
        ):  # for RSAT2 this is per polarisation, otherwise there just is one
            for pol in polarisation:
                write_run_file(
                    save_path=f"{coregistration_directory}/process/input.crop{pol}",
                    template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                    f"templates/doris_v4/input_files/input.crop",
                    asc_dsc=asc_dsc[track],
                    track=tracks[track],
                    parameter_file=parameter_file,
                    other_parameters={
                        "img_name": img_name.format(pol),
                        "pol": pol,
                        "center_lat": center_lat,
                        "center_lon": center_lon,
                        "pix_az": pix_daz + 500,
                        "pix_r": pix_dr + 500,
                    },
                )
        else:
            write_run_file(
                save_path=f"{coregistration_directory}/process/input.crop",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                f"templates/doris_v4/input_files/input.crop",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
                other_parameters={
                    "img_name": img_name,
                    "pol": "",
                    "center_lat": center_lat,
                    "center_lon": center_lon,
                    "pix_az": pix_daz + 500,
                    "pix_r": pix_dr + 500,
                },
            )

        # write input.resample
        for pol in polarisation:
            write_run_file(
                save_path=f"{coregistration_directory}/process/input.resample{pol}",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                f"templates/doris_v4/input_files/input.resample",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
                other_parameters={
                    "pol": pol,
                    "center_lat": center_lat,
                    "center_lon": center_lon,
                    "pix_az": pix_daz,
                    "pix_r": pix_dr,
                },
            )

        # finally, we need input.readfiles, which requires a data string composed of sensor-specific data
        if out_parameters["general:input-data:sensor"] == "ALOS2":
            data_string = """S_IN_METHOD     ALOS2
S_IN_DAT        IMG.1
S_IN_LEA        LED.1
S_IN_VOL        VOL.1"""

        elif out_parameters["general:input-data:sensor"] == "Cosmo":
            data_string = """S_IN_METHOD     CSK
S_IN_DAT        image.h5"""

        elif out_parameters["general:input-data:sensor"] == "ERS":
            data_string = """S_IN_METHOD     ERS
S_IN_VOL        VRD_DAT.001
S_IN_DAT        DAT_01.001
S_IN_LEA        LEA_01.001
S_IN_NULL       dummy"""

        elif out_parameters["general:input-data:sensor"] == "ENV":
            data_string = """S_IN_METHOD     ASAR
S_IN_DAT        image.N1"""

        elif out_parameters["general:input-data:sensor"] == "RSAT":
            data_string = """S_IN_METHOD     RSAT
S_IN_VOL        VDF_DAT.001
S_IN_DAT        DAT_01.001
S_IN_LEA        LEA_01.001
S_IN_NULL       dummy"""

        elif out_parameters["general:input-data:sensor"] == "RSAT2":
            data_string = """S_IN_METHOD     RADARSAT-2
S_IN_DAT        imagery_HH.tif
S_IN_LEA        product.xml"""

        elif out_parameters["general:input-data:sensor"] == "TSX":
            data_string = """S_IN_METHOD     TSX
S_IN_DAT        image.cos
S_IN_LEA        leader.xml"""

        else:
            raise ValueError(f'Unknown sensor {out_parameters["general:input-data:sensor"]} for input.readfiles!')

        write_run_file(
            save_path=f"{coregistration_directory}/process/input.readfiles",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
            f"templates/doris_v4/input_files/input.readfiles",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            other_parameters={"data_string": data_string},
        )

        write_directory_contents(
            coregistration_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["doris_v4"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_depsi_matlab(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and files for DePSI matlab.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file

    Raises
    ------
    AssertionError
        If a dictionary is passed to `ref_cn` in the parameter file, but the track key is missing
    ValueError
        If an invalid mode is passed to `ref_cn` in the parameter file
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
        "depsi_matlab:general:depsi_matlab-code-directory",
        "depsi_matlab:general:rdnaptrans-directory",
        "depsi_matlab:general:geocoding-directory",
        "general:timeframe:start",
        "general:timeframe:end",
        "depsi_matlab:depsi_matlab-settings:general:ref-cn",
        "depsi_matlab:depsi_matlab-settings:psc:do-water-mask",
        "depsi_matlab:general:AoI-name",
        "general:workflow:filters:coregistration-mode",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]
    start_date = out_parameters["general:timeframe:start"].replace("-", "")
    end_date = out_parameters["general:timeframe:end"].replace("-", "")

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        depsi_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["depsi_matlab"], track=tracks[track]
        )

        # determine if we came from reduce_slc_matlab or merge_to_stack_matlab
        if (
            out_parameters["general:workflow:filters:coregistration-mode"] == "doris"
            or out_parameters["general:input-data:sensor"].lower() != "s1"
        ):
            crop_directory = format_process_folder(
                parameter_file=parameter_file, job_description=JOB_DEFINITIONS["reduce_slc_matlab"], track=tracks[track]
            )
        else:
            crop_directory = format_process_folder(
                parameter_file=parameter_file,
                job_description=JOB_DEFINITIONS["merge_to_stack_matlab"],
                track=tracks[track],
            )

        # we need a psi and boxes folder in the depsi directory
        os.makedirs(f"{depsi_directory}", exist_ok=True)
        os.makedirs(f"{depsi_directory}/../boxes", exist_ok=True)

        # link the necessary boxes
        os.system(
            f"cp -Rp {out_parameters['depsi_matlab:general:depsi_matlab-code-directory']} {depsi_directory}/../boxes"
        )
        os.system(f"cp -Rp {out_parameters['depsi_matlab:general:rdnaptrans-directory']} {depsi_directory}/../boxes")
        os.system(f"cp -Rp {out_parameters['depsi_matlab:general:geocoding-directory']} {depsi_directory}/../boxes")

        # detect the mother and dem_radar from the mother
        mother = glob.glob(f"{crop_directory}/*cropped_stack/2*/master.res")[0]
        # cut off master.res, and add dem_radar.raw
        dem_radar = mother.replace("/master.res", "/dem_radar.raw")
        mother_date = mother.split("/")[-2]

        # link the mother resfile and dem_radar
        os.system(f"ln -sf {mother} {depsi_directory}/slave.res")
        os.system(f"ln -sf {dem_radar} {depsi_directory}/dem_radar.raw")

        # find the first and last valid dates within range
        if os.path.exists(f"{crop_directory}/cropped_stack/path_slcs.txt"):
            f = open(f"{crop_directory}/cropped_stack/path_slcs.txt")
            resfiles = f.read().split("\n")
            f.close()
            dates = [i.split("/")[-2] for i in resfiles if i != ""]
            valid_dates = [date for date in dates if start_date <= date <= end_date]
        else:
            valid_dates = []

        if len(valid_dates) == 0:
            # From #77 , not doing this will cause the following in multi-track starts:
            # Looping over A,B,C,D , if C has no valid_dates, the parameter file for D will not be generated
            # as the generation in C will throw an error with the min/max below
            print(
                "WARNING: Did not identify any properly cropped images! Cannot determine start and "
                "end date for DePSI, setting to None. This will crash DePSI."
            )
            act_start_date = None
            act_end_date = None
        else:
            act_start_date = min(valid_dates)
            act_end_date = max(valid_dates)

        # generate the water mask link
        if out_parameters["depsi_matlab:depsi_matlab-settings:psc:do-water-mask"] == "yes":
            filename_water_mask = (
                f"{CONFIG_PARAMETERS['CAROLINE_WATER_MASK_DIRECTORY']}/water_mask_"
                f"{out_parameters['depsi_matlab:general:AoI-name']}_"
                f"{out_parameters['general:input-data:sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}.raw"
            )
        else:
            filename_water_mask = "[]"

        # #62 -> figure out the reference point
        key = f"{out_parameters['general:input-data:sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}"

        if not isinstance(out_parameters["depsi_matlab:depsi_matlab-settings:general:ref-cn"], dict):
            print(
                "WARNING: Invalid value for ref-cn "
                f"({out_parameters['depsi_matlab:depsi_matlab-settings:general:ref-cn']}) "
                "encountered. Using mode 'constant'..."
            )
            mode = "constant"

        if key not in out_parameters["depsi_matlab:depsi_matlab-settings:general:ref-cn"]:
            if "all" not in out_parameters["depsi_matlab:depsi_matlab-settings:general:ref-cn"]:
                raise ValueError(
                    f"Cannot find {key} in ref-cn {out_parameters['depsi_matlab:depsi_matlab-settings:general:ref-cn']}"
                )
            else:
                mode = str(out_parameters["depsi_matlab:depsi_matlab-settings:general:ref-cn"]["all"])
        else:
            mode = str(out_parameters["depsi_matlab:depsi_matlab-settings:general:ref-cn"][key])

        if mode in ["independent", "[]"]:
            ref_cn = "[]"
        elif mode[0] == "[":  # hardcoded
            ref_cn = mode.replace(" ", "")  # remove spaces since Matlab doesn't like them
        elif mode == "constant":
            # find the old runs
            directories = glob.glob(f"{'-'.join(depsi_directory.split('-')[:-1])}-*")
            ref_cn = "[]"
            if len(directories) == 0:
                # no old runs are present, so we run on mode 'independent' for the initialization
                pass
            else:
                # sort and reverse them to find the most recent one
                rev_order_runs = list(sorted(directories))[::-1]
                for i in range(len(rev_order_runs)):  # loop in case one crashed. If all crashed,
                    # ref_cn is defined before the if/else, and we run on mode 'independent'
                    ref_file = (
                        f"{rev_order_runs[i]}/psi/{out_parameters['depsi_matlab:general:AoI-name']}_"
                        f"{out_parameters['general:input-data:sensor'].lower()}_"
                        f"{asc_dsc[track]}_t{tracks[track]:0>3d}_ref_sel1.raw"
                    )  # this file saves the selected reference
                    if os.path.exists(ref_file):
                        ref_data = np.memmap(ref_file, mode="r", shape=(3,), dtype="float64")
                        # this outputs the reference point in [index, az, r]. We need [az,r]
                        ref_cn = f"[{int(round(ref_data[1]))},{int(round(ref_data[2]))}]"
                        break  # we found one, so we can stop

        else:
            raise ValueError(
                f"Expected types are dictionary, 'independent', '[]', '[az, r]', or 'constant', got {mode}"
            )

        # write depsi.m
        write_run_file(
            save_path=f"{depsi_directory}/depsi.m",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/depsi_matlab/depsi.m",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            other_parameters={
                "geocoding_version": out_parameters["depsi_matlab:general:geocoding-directory"].split("/")[-1].rstrip(),
                "depsi_version": out_parameters["depsi_matlab:general:depsi_matlab-code-directory"]
                .split("/")[-1]
                .rstrip(),
            },
        )

        # write depsi.sh
        write_run_file(
            save_path=f"{depsi_directory}/depsi_matlab.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/depsi_matlab/depsi_matlab.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["depsi_matlab:general:AoI-name"],
            config_parameters=["caroline_work_directory", "matlab_module"],
            other_parameters={"depsi_base_directory": depsi_directory, "track": tracks[track]},
        )

        # create param_file_depsi.txt
        #
        write_run_file(
            save_path=f"{depsi_directory}/param_file_depsi.txt",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/depsi_matlab/param_file.txt",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "depsi_matlab:general:AoI-name",
                "depsi_matlab:depsi_matlab-settings:general:max-mem-buffer",
                "depsi_matlab:depsi_matlab-settings:general:visible-plots",
                "depsi_matlab:depsi_matlab-settings:general:detail-plots",
                "depsi_matlab:depsi_matlab-settings:general:processing-groups",
                "depsi_matlab:depsi_matlab-settings:general:run-mode",
                ["general:input-data:sensor", "lowercase"],
                "depsi_matlab:depsi_matlab-settings:general:exclude-date",
                "depsi_matlab:depsi_matlab-settings:general:az-spacing",
                "depsi_matlab:depsi_matlab-settings:general:r-spacing",
                "depsi_matlab:depsi_matlab-settings:general:slc-selection-input",
                "depsi_matlab:depsi_matlab-settings:general:ifg-selection-input",
                "depsi_matlab:depsi_matlab-settings:general:Ncv",
                "depsi_matlab:depsi_matlab-settings:general:ps-method",
                "depsi_matlab:depsi_matlab-settings:general:psc-model",
                "depsi_matlab:depsi_matlab-settings:general:ps-model",
                "depsi_matlab:depsi_matlab-settings:general:final-model",
                "depsi_matlab:depsi_matlab-settings:general:breakpoint",
                "depsi_matlab:depsi_matlab-settings:general:breakpoint2",
                "depsi_matlab:depsi_matlab-settings:general:ens-coh-threshold",
                "depsi_matlab:depsi_matlab-settings:general:varfac-threshold",
                "depsi_matlab:depsi_matlab-settings:general:detrend-method",
                "depsi_matlab:depsi_matlab-settings:general:output-format",
                "depsi_matlab:depsi_matlab-settings:general:do-apriori-sidelobe-mask",
                "depsi_matlab:depsi_matlab-settings:general:do-aposteriori-sidelobe-mask",
                "depsi_matlab:depsi_matlab-settings:geocoding:ref-height",
                "depsi_matlab:depsi_matlab-settings:psc:amplitude-calibration",
                "depsi_matlab:depsi_matlab-settings:psc:psc-selection-method",
                "depsi_matlab:depsi_matlab-settings:psc:psc-selection-gridsize",
                "depsi_matlab:depsi_matlab-settings:psc:psc-threshold",
                "depsi_matlab:depsi_matlab-settings:psc:max-arc-length",
                "depsi_matlab:depsi_matlab-settings:psc:network-method",
                "depsi_matlab:depsi_matlab-settings:psc:Ncon",
                "depsi_matlab:depsi_matlab-settings:psc:Nparts",
                "depsi_matlab:depsi_matlab-settings:psc:Npsc-selections",
                "depsi_matlab:depsi_matlab-settings:psc:gamma-threshold",
                "depsi_matlab:depsi_matlab-settings:psc:psc-distribution",
                "depsi_matlab:depsi_matlab-settings:psc:weighted-unwrap",
                "depsi_matlab:depsi_matlab-settings:psc:livetime-threshold",
                "depsi_matlab:depsi_matlab-settings:psc:peak-tolerance",
                "depsi_matlab:depsi_matlab-settings:psp:psp-selection-method",
                "depsi_matlab:depsi_matlab-settings:psp:psp-threshold1",
                "depsi_matlab:depsi_matlab-settings:psp:psp-threshold2",
                "depsi_matlab:depsi_matlab-settings:psp:ps-eval-method",
                "depsi_matlab:depsi_matlab-settings:psp:Namp-disp-bins",
                "depsi_matlab:depsi_matlab-settings:psp:Ndens-iterations",
                "depsi_matlab:depsi_matlab-settings:psp:densification-flag",
                "depsi_matlab:depsi_matlab-settings:psp:ps-area-of-interest",
                "depsi_matlab:depsi_matlab-settings:psp:dens-method",
                "depsi_matlab:depsi_matlab-settings:psp:dens-check",
                "depsi_matlab:depsi_matlab-settings:psp:Nest",
                "depsi_matlab:depsi_matlab-settings:stochastic-model:defo-range",
                "depsi_matlab:depsi_matlab-settings:stochastic-model:weighting",
                "depsi_matlab:depsi_matlab-settings:stochastic-model:ts-atmo-filter",
                "depsi_matlab:depsi_matlab-settings:stochastic-model:ts-atmo-filter-length",
                "depsi_matlab:depsi_matlab-settings:stochastic-model:ts-noise-filter",
                "depsi_matlab:depsi_matlab-settings:stochastic-model:ts-noise-filter-length",
                "depsi_matlab:depsi_matlab-settings:bowl:defo-method",
                "depsi_matlab:depsi_matlab-settings:bowl:xc0",
                "depsi_matlab:depsi_matlab-settings:bowl:yc0",
                "depsi_matlab:depsi_matlab-settings:bowl:zc0",
                "depsi_matlab:depsi_matlab-settings:bowl:r0",
                "depsi_matlab:depsi_matlab-settings:bowl:r10",
                "depsi_matlab:depsi_matlab-settings:bowl:epoch",
                ["depsi_matlab:depsi_matlab-settings:general:stc-min-max", "strip", "[] "],
                ["depsi_matlab:depsi_matlab-settings:stochastic-model:std-param", "strip", "[] "],
            ],
            other_parameters={
                "crop_base_directory": crop_directory,
                "track": f"{tracks[track]:0>3d}",
                "asc_dsc": asc_dsc[track],
                "asc_dsc_fmt": "desc" if asc_dsc[track] == "dsc" else asc_dsc[track],
                "start_date": act_start_date,
                "stop_date": act_end_date,
                "master_date": mother_date,
                "ref_cn": ref_cn,
                "filename_water_mask": filename_water_mask,
            },
        )

        write_directory_contents(
            depsi_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["depsi_matlab"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_depsi_post(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and files for DePSI-post.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file

    Raises
    ------
    ValueError
        If `depsi_post_mode` is not 'tarball' or 'csv'
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
        "depsi_post:general:depsi_post-code-directory",
        "depsi_post:depsi_post-settings:defo-clim",
        "depsi_post:depsi_post-settings:height-clim",
        "depsi_matlab:general:rdnaptrans-directory",
        "depsi_matlab:general:geocoding-directory",
        "general:workflow:filters:depsi_post-output",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]

    defo_clim_raw = out_parameters["depsi_post:depsi_post-settings:defo-clim"]
    defo_clim_min = defo_clim_raw[0]
    defo_clim_max = defo_clim_raw[1]

    height_clim_raw = out_parameters["depsi_post:depsi_post-settings:height-clim"]
    height_clim_min = height_clim_raw[0]
    height_clim_max = height_clim_raw[1]

    if out_parameters["general:workflow:filters:depsi_post-output"] == "tarball":
        do_csv = 0
    elif out_parameters["general:workflow:filters:depsi_post-output"] == "csv":
        do_csv = 1
    else:
        raise ValueError(
            "general:workflow:filters:depsi_post-output is set to "
            f"{out_parameters['general:workflow:filters:depsi_post-output']}, only know 'tarball' and 'csv'!"
        )

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        depsi_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["depsi_post"], track=tracks[track]
        )

        # link the DePSI-post box
        os.system(f"cp -Rp {out_parameters['depsi_post:general:depsi_post-code-directory']} {depsi_directory}/../boxes")

        # write depsi_post.m
        write_run_file(
            save_path=f"{depsi_directory}/depsi_post.m",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/depsi_post/depsi_post.m",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "depsi_post:depsi_post-settings:dlat",
                "depsi_post:depsi_post-settings:dlon",
                "depsi_post:depsi_post-settings:drdx",
                "depsi_post:depsi_post-settings:drdy",
                "general:input-data:sensor",
                "depsi_matlab:general:AoI-name",
                "depsi_post:depsi_post-settings:proj",
                "depsi_post:depsi_post-settings:ref-dheight",
                "depsi_post:depsi_post-settings:posteriori-scale-factor",
                ["depsi_post:depsi_post-settings:pred-model", "strip", " "],
                "depsi_post:depsi_post-settings:plot-mode",
                ["depsi_post:depsi_post-settings:do-plots", "strip", "{} "],
                ["depsi_post:depsi_post-settings:output", "strip", "{} "],
                "depsi_post:depsi_post-settings:fontsize",
                "depsi_post:depsi_post-settings:markersize",
                "depsi_post:depsi_post-settings:do-print",
                "depsi_post:depsi_post-settings:output-format",
                "depsi_post:depsi_post-settings:az0",
                "depsi_post:depsi_post-settings:azN",
                "depsi_post:depsi_post-settings:r0",
                "depsi_post:depsi_post-settings:rN",
                "depsi_post:depsi_post-settings:result",
                "depsi_post:depsi_post-settings:psc-selection",
                "depsi_post:depsi_post-settings:do-remove-filtered",
                "depsi_post:depsi_post-settings:which-sl-mask",
                "depsi_post:depsi_post-settings:shift-to-mean",
                "depsi_post:depsi_post-settings:new-ref-cn",
                "depsi_post:depsi_post-settings:map-to-vert",
                "depsi_post:depsi_post-settings:defo-lim",
                "depsi_post:depsi_post-settings:height-lim",
                "depsi_post:depsi_post-settings:ens-coh-lim",
                "depsi_post:depsi_post-settings:ens-coh-local-lim",
                "depsi_post:depsi_post-settings:stc-lim",
                "depsi_post:depsi_post-settings:ens-coh-clim",
                "depsi_post:depsi_post-settings:ens-coh-local-clim",
                "depsi_post:depsi_post-settings:stc-clim",
            ],
            other_parameters={
                "geocoding_version": out_parameters["depsi_matlab:general:geocoding-directory"].split("/")[-1].rstrip(),
                "depsi_post_version": out_parameters["depsi_post:general:depsi_post-code-directory"]
                .split("/")[-1]
                .rstrip(),
                "rdnaptrans_version": out_parameters["depsi_matlab:general:rdnaptrans-directory"]
                .split("/")[-1]
                .rstrip(),
                "do_csv": do_csv,
                "asc_dsc": asc_dsc[track],
                "track": tracks[track],
                "fill_track": f"{tracks[track]:0>3d}",
                "dp_defo_clim_min": defo_clim_min,
                "dp_defo_clim_max": defo_clim_max,
                "dp_height_clim_min": height_clim_min,
                "dp_height_clim_max": height_clim_max,
            },
        )

        # write depsi_post.sh
        write_run_file(
            save_path=f"{depsi_directory}/depsi_post.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/depsi_post/depsi_post.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["depsi_matlab:general:AoI-name"],
            config_parameters=["caroline_work_directory", "matlab_module"],
            other_parameters={"track": tracks[track], "depsi_base_directory": depsi_directory},
        )

        write_directory_contents(
            depsi_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["depsi_post"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_doris_v5(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for Doris v5.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
        "general:dem:delta",
        "general:dem:upperleft",
        "general:dem:size",
        "general:dem:file",
        "general:timeframe:start",
        "general:timeframe:end",
        "general:timeframe:mother",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]

    dem_delta = out_parameters["general:dem:delta"]
    dem_size = out_parameters["general:dem:size"]
    dem_upperleft = out_parameters["general:dem:upperleft"]

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        coregistration_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["doris_v5"], track=tracks[track]
        )

        # we need a process folder in the coregistration directory, so we can combine that command
        os.makedirs(f"{coregistration_directory}/bad_images", exist_ok=True)
        os.makedirs(f"{coregistration_directory}/good_images", exist_ok=True)
        os.makedirs(f"{coregistration_directory}/input_files", exist_ok=True)

        # link the S1 data in good_images, first remove the current ones, then link the new ones
        os.system(f"rm -rf {coregistration_directory}/good_images/2*")
        os.system(
            f"ln -sfn {CONFIG_PARAMETERS['SLC_BASE_DIRECTORY']}/s1_{asc_dsc[track]}_t{tracks[track]:0>3d}/"
            f"IW_SLC__1SDV_VVVH/* {coregistration_directory}/good_images"
        )

        # dump the zipfiles with their size into a text file, necessary for utils/identify_incomplete_sentinel1_images
        os.system(
            f"ls -l {coregistration_directory}/good_images/2*/*.zip > "
            f"{coregistration_directory}/good_images/zip_files.txt"
        )

        # move the invalid images to the bad_images
        remove_incomplete_sentinel1_images(parameter_file)

        # link the DEM
        dem_directory = "/".join(out_parameters["general:dem:file"].split("/")[:-1])
        os.system(f"ln -sfn {dem_directory} {coregistration_directory}/dem")

        # generate the input files
        input_files = glob.glob(
            f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/doris_v5/input_files/input.*"
        )
        for file in input_files:
            if file.split("/")[-1] in ["input.comprefdem", "input.dembased"]:
                # these ones need the DEM variables
                write_run_file(
                    save_path=f"{coregistration_directory}/input_files/{file.split('/')[-1]}",
                    template_path=file,
                    asc_dsc=asc_dsc[track],
                    track=tracks[track],
                    parameter_file=parameter_file,
                    parameter_file_parameters=["general:dem:file", "general:dem:format", "general:dem:nodata"],
                    other_parameters={
                        "dem_s1": dem_size[0],
                        "dem_s2": dem_size[1],
                        "dem_d1": dem_delta[0],
                        "dem_d2": dem_delta[1],
                        "dem_ul1": dem_upperleft[0],
                        "dem_ul2": dem_upperleft[1],
                    },
                )
            else:
                # copy it directly
                write_run_file(
                    save_path=f"{coregistration_directory}/input_files/{file.split('/')[-1]}",
                    template_path=file,
                    asc_dsc=asc_dsc[track],
                    track=tracks[track],
                    parameter_file=parameter_file,
                )

        # create doris_input.xml
        # we need to transform all the 1/0 from the parameter file into Yes/No
        other_parameters = {}
        for parameter in [
            "doris_v5:doris_v5-settings:do-coarse-orbits",
            "doris_v5:doris_v5-settings:do-deramp",
            "doris_v5:doris_v5-settings:do-reramp",
            "doris_v5:doris_v5-settings:do-fake-fine-coreg-bursts",
            "doris_v5:doris_v5-settings:do-dac-bursts",
            "doris_v5:doris_v5-settings:do-fake-coreg-bursts",
            "doris_v5:doris_v5-settings:do-fake-master-resample",
            "doris_v5:doris_v5-settings:do-resample",
            "doris_v5:doris_v5-settings:do-reramp2",
            "doris_v5:doris_v5-settings:do-interferogram",
            "doris_v5:doris_v5-settings:do-compref-phase",
            "doris_v5:doris_v5-settings:do-compref-dem",
            "doris_v5:doris_v5-settings:do-coherence",
            "doris_v5:doris_v5-settings:do-esd",
            "doris_v5:doris_v5-settings:do-network-esd",
            "doris_v5:doris_v5-settings:do-ESD-correct",
            "doris_v5:doris_v5-settings:do-combine-master",
            "doris_v5:doris_v5-settings:do-combine-slave",
            "doris_v5:doris_v5-settings:do-ref-phase",
            "doris_v5:doris_v5-settings:do-ref-dem",
            "doris_v5:doris_v5-settings:do-phasefilt",
            "doris_v5:doris_v5-settings:do-calc-coordinates",
            "doris_v5:doris_v5-settings:do-multilooking",
            "doris_v5:doris_v5-settings:do-unwrap",
        ]:
            value = read_parameter_file(parameter_file, [parameter])[parameter]
            if value == 1:
                other_parameters[parameter] = "Yes"
            else:
                other_parameters[parameter] = "No"

        # we also need the track and orbit direction
        other_parameters["track"] = tracks[track]
        other_parameters["asc_dsc"] = asc_dsc[track]

        # and the start, end, and mother dates
        images = glob.glob(f"{coregistration_directory}/good_images/2*")
        images = [eval(image.split("/")[-1]) for image in images]

        start_date = eval(out_parameters["general:timeframe:start"].replace("-", ""))
        end_date = eval(out_parameters["general:timeframe:end"].replace("-", ""))
        master_date = eval(out_parameters["general:timeframe:mother"].replace("-", ""))

        # then select and format the start, end, and master dates
        other_parameters["start_date"] = str(min([image for image in images if image >= start_date]))
        other_parameters["start_date"] = (
            f"{other_parameters['start_date'][:4]}-"
            f"{other_parameters['start_date'][4:6]}-"
            f"{other_parameters['start_date'][6:]}"
        )
        other_parameters["end_date"] = str(max([image for image in images if image <= end_date]))
        other_parameters["end_date"] = (
            f"{other_parameters['end_date'][:4]}-"
            f"{other_parameters['end_date'][4:6]}-"
            f"{other_parameters['end_date'][6:]}"
        )
        other_parameters["master_date"] = str(min([image for image in images if image >= master_date]))
        other_parameters["master_date"] = (
            f"{other_parameters['master_date'][:4]}-"
            f"{other_parameters['master_date'][4:6]}-"
            f"{other_parameters['master_date'][6:]}"
        )

        # finally, add the coregistration directory
        other_parameters["coregistration_directory"] = coregistration_directory

        # write doris_input.xml
        write_run_file(
            save_path=f"{coregistration_directory}/doris_input.xml",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/doris_v5/doris_input.xml",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["general:shape-file:aoi-name", "general:shape-file:directory"],
            config_parameters=["orbit_directory"],
            other_parameters=other_parameters,
        )

        # write doris_stack.sh
        write_run_file(
            save_path=f"{coregistration_directory}/doris_stack.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/doris_v5/doris_stack.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["doris_v5:general:AoI-name", "doris_v5:general:code-directory"],
            config_parameters=[
                "caroline_work_directory",
                "caroline_virtual_environment_directory",
                "python3_module",
                "gdal_module",
            ],
            other_parameters={"track": tracks[track], "coregistration_directory": coregistration_directory},
        )

        write_directory_contents(
            coregistration_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["doris_v5"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_doris_v5_cleanup(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the cleanup script to clean the directories produced by Doris v5.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        coregistration_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["doris_v5_cleanup"], track=tracks[track]
        )

        write_run_file(
            save_path=f"{coregistration_directory}/cleanup.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/"
            "doris_v5/cleanup-doris-s1-stack.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            other_parameters={"coregistration_directory": coregistration_directory},
        )


def prepare_email(parameter_file: str, do_track: int | list | None = None) -> None:
    """Create and send the completion email.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    body = generate_email(parameter_file)

    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
        "general:email:recipients",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    area_name = parameter_file.split("/")[-1].split(".")[0].split("param_file_")[-1]

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]
    track_csv = ""
    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if do_track == tracks[track]:
                track_csv += f"{out_parameters['general:input-data:sensor']}_{asc_dsc[track]}_t{tracks[track]:0>3d},"
        elif isinstance(do_track, list):
            if tracks[track] in do_track:
                track_csv += f"{out_parameters['general:input-data:sensor']}_{asc_dsc[track]}_t{tracks[track]:0>3d},"
        else:
            track_csv += f"{out_parameters['general:input-data:sensor']}_{asc_dsc[track]}_t{tracks[track]:0>3d},"

    track_csv = track_csv.strip(",")
    header = f"CAROLINE: {out_parameters['general:input-data:sensor']}/{area_name}/{track_csv}"
    os.system(f"""echo "Subject: {header}
from:noreply@spider.surfsara.nl

{body}" | {CONFIG_PARAMETERS['SENDMAIL_EXECUTABLE']} {out_parameters['general:email:recipients']}""")


def prepare_create_mrm(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and files for mrm creation, part of DePSI-post.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
        "depsi_post:general:cpxfiddle-directory",
        "general:workflow:filters:coregistration-mode",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        # determine if we came from reduce_slc_matlab or merge_to_stack_matlab
        if (
            out_parameters["general:workflow:filters:coregistration-mode"] == "doris"
            or out_parameters["general:input-data:sensor"].lower() != "s1"
        ):
            crop_directory = format_process_folder(
                parameter_file=parameter_file, job_description=JOB_DEFINITIONS["reduce_slc_matlab"], track=tracks[track]
            )
        else:
            crop_directory = format_process_folder(
                parameter_file=parameter_file,
                job_description=JOB_DEFINITIONS["merge_to_stack_matlab"],
                track=tracks[track],
            )

        depsi_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["depsi_matlab"], track=tracks[track]
        )

        # we need to run cpxfiddle first. This requires two parameters: n_lines, and the project ID
        fr = open(f"{crop_directory}/cropped_stack/nlines_crp.txt")
        data = fr.read().split("\n")
        fr.close()
        n_lines = data[0]

        project_id = depsi_directory.split("/")[-2].split("-")[0]

        # format the arguments in the correct order
        command_args = (
            f"{project_id} {n_lines} 1 1 {out_parameters['depsi_post:general:cpxfiddle-directory']} {depsi_directory}"
        )
        os.system(
            f"bash {CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/scripts/create_mrm_ras_header.sh "
            f"{command_args}"
        )

        write_run_file(
            save_path=f"{depsi_directory}/create_mrm.m",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/create_mrm/create_mrm.m",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "depsi_matlab:general:AoI-name",
                ["general:input-data:sensor", "lowercase"],
            ],
            other_parameters={
                "fill_track": f"{tracks[track]:0>3d}",
                "asc_dsc": asc_dsc[track],
            },
        )

        write_run_file(
            save_path=f"{depsi_directory}/create_mrm.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/create_mrm/create_mrm.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["depsi_matlab:general:AoI-name"],
            config_parameters=["caroline_work_directory", "matlab_module"],
            other_parameters={
                "track": tracks[track],
                "depsi_base_directory": depsi_directory,
            },
        )

        write_directory_contents(
            depsi_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["create_mrm"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_set_portal_upload_flag(parameter_file: str, do_track: int | list | None = None) -> None:
    """Create the indication for a portal upload.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "general:tracks:track",
        "general:portal:skygeo-customer",
        "general:portal:skygeo-viewer",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        depsi_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["depsi_matlab"], track=tracks[track]
        )

        # The parameter file already contains a datestamp so we don't need to redo that
        portal_upload_file = (
            f"{CONFIG_PARAMETERS['PORTAL_UPLOAD_FLAG_DIRECTORY']}/"
            f"{parameter_file.split('/')[-1].split('.')[0]}_t{tracks[track]:0>3d}_upload.txt"
        )
        f = open(portal_upload_file, "w")
        f.write(
            f"Status: TBD\n"
            f"Directory: {depsi_directory}\n"
            f"Viewer: {out_parameters['general:portal:skygeo-viewer']}\n"
            f"Customer: {out_parameters['general:portal:skygeo-customer']}"
        )
        f.close()


def prepare_s1_download(parameter_file: str, do_track: int | list | None = None) -> None:
    """Prepare the scripts for the download.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    aoi_name = parameter_file.split("/")[-1].split("param_file_")[-1].split(".")[0]

    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:shape-file:directory",
        "general:shape-file:aoi-name",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    shapefile_name = (
        f"{out_parameters['general:shape-file:directory']}/{out_parameters['general:shape-file:aoi-name']}_shape.shp"
    )

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]

    date = dt.datetime.now().strftime("%Y%m%d-%H%M%S")

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        os.makedirs(
            f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/once/"
            f"{aoi_name}_{asc_dsc[track]}_t{tracks[track]:0>3d}-{date}",
            exist_ok=True,
        )
        write_run_file(
            save_path=(
                f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/once/"
                f"{aoi_name}_{asc_dsc[track]}_t{tracks[track]:0>3d}-{date}/roi.wkt"
            ),
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/download/roi.wkt",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            other_parameters={"wkt_string": convert_shp_to_wkt(shapefile_name)},
        )

        write_run_file(
            save_path=(
                f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/once/"
                f"{aoi_name}_{asc_dsc[track]}_t{tracks[track]:0>3d}-{date}/geosearch.yaml"
            ),
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/download/geosearch.yaml",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["general:input-data:product-type", "general:timeframe:start"],
            other_parameters={
                "wkt_file": (
                    f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/once/"
                    f"{aoi_name}_{asc_dsc[track]}_t{tracks[track]:0>3d}-{date}/roi.wkt"
                ),
                "orbits_csv": tracks[track],
            },
        )

        download_completed = False
        repeat_counter = 0  # to keep track of how many times the download call is performed
        while not download_completed:
            # actually perform the download (first load the virtual environment, then run the caroline-download command)
            os.system(
                f"source {CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/scripts/imports.sh; "
                f"source {CONFIG_PARAMETERS['CAROLINE_VIRTUAL_ENVIRONMENT_DIRECTORY']}/bin/activate; "
                "caroline-download --config "
                f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/download-config.yaml "
                "--geo-search "
                f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/once/"
                f"{aoi_name}_{asc_dsc[track]}_t{tracks[track]:0>3d}-{date}/geosearch.yaml"
            )
            os.system('''echo "\n\n\nDownload finished. Starting ZIP file integrity check...\n"''')

            zip_files = glob.glob(
                f"{CONFIG_PARAMETERS['SLC_BASE_DIRECTORY']}/s1_{asc_dsc[track]}_t{tracks[track]:0>3d}/"
                f"IW_SLC__1SDV_VVVH/*/*.zip"
            )
            bad_zip_files = []
            for zip_file in zip_files:
                try:
                    _ = zipfile.ZipFile(zip_file)
                except zipfile.BadZipFile:  # zip file cannot be opened --> incomplete download
                    bad_zip_files.append(zip_file)

            if len(bad_zip_files) == 0:  # download is complete
                os.system('''echo "ZIP File Integrity Check Passed!\n"''')
                download_completed = True
            else:  # download failed early. Remove the bad zips and try again
                os.system('''echo "ZIP File Integrity Check Failed!\n"''')
                os.system(f'''echo "Failed on {str(bad_zip_files).replace('"', "'")}. Removing and restarting...\n"''')
                for zip_file in bad_zip_files:
                    os.system(f"rm -f {zip_file}")
                repeat_counter += 1
                if repeat_counter > S1_DOWNLOAD_CALL_REPEAT_LIMIT:
                    os.system('''echo "Download failed over 20 times. Please check logs. Killing process...\n"''')
                    exit(5)

    # final integrity check on all tracks (in case the loop above somehow exited early)
    bad_zip_files = []
    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        zip_files = glob.glob(
            f"{CONFIG_PARAMETERS['SLC_BASE_DIRECTORY']}/s1_{asc_dsc[track]}_t{tracks[track]:0>3d}/"
            f"IW_SLC__1SDV_VVVH/*/*.zip"
        )

        for zip_file in zip_files:
            try:
                _ = zipfile.ZipFile(zip_file)
            except zipfile.BadZipFile:  # zip file cannot be opened --> incomplete download
                bad_zip_files.append(zip_file)

    if len(bad_zip_files) > 0:
        os.system('''echo "\n\n\nZIP File Integrity Check Failed!\n"''')
        os.system(f'''echo "Failed on zip file(s) {str(bad_zip_files).replace('"', "'")}. Exiting with code 5...\n"''')
        exit(5)  # Make the code exit with a non-zero exit code so the next steps won't run


def prepare_snap_fix_permissions(parameter_file: str, do_track: int | list | None = None) -> None:
    """Change all the permissions for the SNAP output to 775.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        snap_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["snap"], track=tracks[track]
        )

        znaps = glob.glob(f"{snap_directory}/*-coreg.znap")
        for zf in znaps:
            os.system(f"chmod 775 {zf}; chmod 775 {zf}/*; chmod 775 {zf}/*/*; chmod 775 {zf}/*/*/*")


def prepare_snap_preparation(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for SNAP preparation.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "snap:general:AoI-name",
        "snap:general:directory",
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
        "general:shape-file:aoi-name",
        "general:shape-file:directory",
        "general:timeframe:start",
        "general:timeframe:end",
        "general:timeframe:mother",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]

    shapefile_name = (
        f"{out_parameters['general:shape-file:directory']}/{out_parameters['general:shape-file:aoi-name']}_shape.shp"
    )

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        snap_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["snap_preparation"], track=tracks[track]
        )

        os.makedirs(snap_directory, exist_ok=True)

        track_fmt = f"{out_parameters['general:input-data:sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}"

        other_parameters = {
            "track": tracks[track],
            "snap-output-path": snap_directory,
            "dry_run": "0",
            "track_formatted": track_fmt,
        }

        # and the start, end, and mother dates
        images = glob.glob(f"{CONFIG_PARAMETERS['SLC_BASE_DIRECTORY']}/{track_fmt}/IW_SLC__1SDV_VVVH/2*")
        images = [eval(image.split("/")[-1]) for image in images]

        start_date = eval(out_parameters["general:timeframe:start"].replace("-", ""))
        end_date = eval(out_parameters["general:timeframe:end"].replace("-", ""))
        mother_date = eval(out_parameters["general:timeframe:mother"].replace("-", ""))

        # then select and format the start, end, and master dates
        other_parameters["start_date"] = str(min([image for image in images if image >= start_date]))
        other_parameters["start_date"] = (
            f"{other_parameters['start_date'][:4]}-"
            f"{other_parameters['start_date'][4:6]}-"
            f"{other_parameters['start_date'][6:]}"
        )
        other_parameters["end_date"] = str(max([image for image in images if image <= end_date]))
        other_parameters["end_date"] = (
            f"{other_parameters['end_date'][:4]}-"
            f"{other_parameters['end_date'][4:6]}-"
            f"{other_parameters['end_date'][6:]}"
        )
        other_parameters["mother_date"] = str(min([image for image in images if image >= mother_date]))
        other_parameters["mother_date"] = (
            f"{other_parameters['mother_date'][:4]}-"
            f"{other_parameters['mother_date'][4:6]}-"
            f"{other_parameters['mother_date'][6:]}"
        )

        # generate the WKT file
        write_run_file(
            save_path=f"{snap_directory}/aoi.wkt",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/snap/aoi.wkt",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            other_parameters={"wkt_string": convert_shp_to_wkt(shapefile_name)},
        )

        # generate generate-snap-graphs.sh
        write_run_file(
            save_path=f"{snap_directory}/generate-snap-graphs.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/snap/generate-snap-graphs.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "snap:general:AoI-name",
            ],
            config_parameters=[
                "caroline_work_directory",
                "caroline_virtual_environment_directory",
                "caroline_install_directory",
                "slc_base_directory",
                "python3_module",
                "gdal_module",
                "snap_module",
            ],
            other_parameters=other_parameters,
        )

        write_directory_contents(
            snap_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["snap_preparation"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_snap(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for SNAP run.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "snap:general:AoI-name",
        "snap:general:directory",
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        snap_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["snap"], track=tracks[track]
        )

        if "--constraint=rome" in JOB_DEFINITIONS["snap"]["sbatch-args"]:
            rome_constrained = "1"
        else:
            rome_constrained = "0"

        os.makedirs(snap_directory, exist_ok=True)

        # generate run-snap-graph.sh
        write_run_file(
            save_path=f"{snap_directory}/run-snap-graph.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/snap/run-snap-graph.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["snap:general:AoI-name"],
            config_parameters=[
                "caroline_work_directory",
                "caroline_virtual_environment_directory",
                "python3_module",
                "gdal_module",
                "snap_module",
            ],
            other_parameters={
                "track": tracks[track],
                "snap-output-path": snap_directory,
                "rome-constrained": rome_constrained,
            },
        )

        write_directory_contents(
            snap_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["snap"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_generate_partitioned_stm(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for STM generation.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "generate_partitioned_stm:general:AoI-name",
        "generate_partitioned_stm:general:directory",
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
        "general:workflow:filters:coregistration-mode",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        stm_directory = format_process_folder(
            parameter_file=parameter_file,
            job_description=JOB_DEFINITIONS["generate_partitioned_stm"],
            track=tracks[track],
        )

        # determine if we came from reduce_slc_python or merge_to_stack_python
        if (
            out_parameters["general:workflow:filters:coregistration-mode"] == "doris"
            or out_parameters["general:input-data:sensor"].lower() != "s1"
        ):
            reduce_slc_python_directory = format_process_folder(
                parameter_file=parameter_file, job_description=JOB_DEFINITIONS["reduce_slc_python"], track=tracks[track]
            )
        else:
            reduce_slc_python_directory = format_process_folder(
                parameter_file=parameter_file,
                job_description=JOB_DEFINITIONS["merge_to_stack_python"],
                track=tracks[track],
            )

        os.makedirs(stm_directory, exist_ok=True)

        # generate stm-generation.py
        stm_output_name = stm_directory.split("/")[-1]
        reduce_slc_python_output_name = reduce_slc_python_directory.split("/")[-1]

        write_run_file(
            save_path=f"{stm_directory}/generate-partitioned-stm.py",
            template_path=(
                f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/"
                "generate-partitioned-stm/generate-partitioned-stm.py"
            ),
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "generate_partitioned_stm:generate_partitioned_stm-settings:ps-selection:mode",
                "generate_partitioned_stm:generate_partitioned_stm-settings:ps-selection:init-settings:start-date",
                "generate_partitioned_stm:generate_partitioned_stm-settings:ps-selection:initsettings:init-length",
                "generate_partitioned_stm:generate_partitioned_stm-settings:incremental-statistics:increment-mode",
                "generate_partitioned_stm:generate_partitioned_stm-settings:incremental-statistics:recal-jump-size",
                "generate_partitioned_stm:generate_partitioned_stm-settings:ps-selection:method",
                "generate_partitioned_stm:generate_partitioned_stm-settings:ps-selection:threshold",
                "generate_partitioned_stm:generate_partitioned_stm-settings:outlier-detection:do-outlier-detection",
                "generate_partitioned_stm:generate_partitioned_stm-settings:outlier-detection:window-size",
                "generate_partitioned_stm:generate_partitioned_stm-settings:outlier-detection:db-mode",
                "generate_partitioned_stm:generate_partitioned_stm-settings:outlier-detection:n-sigma",
                "generate_partitioned_stm:generate_partitioned_stm-settings:partitioning:do-partitioning",
                "generate_partitioned_stm:generate_partitioned_stm-settings:partitioning:search-method",
                "generate_partitioned_stm:generate_partitioned_stm-settings:partitioning:cost-function",
                "generate_partitioned_stm:generate_partitioned_stm-settings:partitioning:db-mode",
                "generate_partitioned_stm:generate_partitioned_stm-settings:partitioning:min-partition-length",
                "generate_partitioned_stm:generate_partitioned_stm-settings:single-differences:mother",
                "generate_partitioned_stm:generate_partitioned_stm-settings:extra-projection",
                "generate_partitioned_stm:generate_partitioned_stm-settings:partitioning:undifferenced-output-lyrs",
                "generate_partitioned_stm:generate_partitioned_stm-settings:partitioning:single-difference-output-lyrs",
            ],
            other_parameters={
                "reduce_slc_python_directory": reduce_slc_python_directory,
                "reduce_slc_python_output_name": reduce_slc_python_output_name,
                "stm_output_directory": stm_directory,
                "stm_output_name": stm_output_name,
            },
        )

        # generate stm-generation.sh
        write_run_file(
            save_path=f"{stm_directory}/generate-partitioned-stm.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/generate-partitioned-stm/generate-partitioned-stm.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "generate_partitioned_stm:general:AoI-name",
                "reduce_slc_python:general:depsi_group-code-directory",
            ],
            config_parameters=[
                "caroline_work_directory",
                "caroline_virtual_environment_directory",
                "python3_module",
                "gdal_module",
            ],
            other_parameters={"track": tracks[track]},
        )

        write_directory_contents(
            stm_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["generate_partitioned_stm"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_create_tarball(parameter_file: str, do_track: int | list | None = None) -> None:
    """Create the tarball after DePSI-post.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = ["track"]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["track"]

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        depsi_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["depsi_matlab"], track=tracks[track]
        )

        project_id = depsi_directory.split("/")[-2].split("-")[0]
        os.system(
            f"cd {depsi_directory}; "
            f"bash {CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/scripts/create_post_project_tar.sh {project_id}"
        )


def prepare_merge_to_stack_matlab(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for merge_to_stack_matlab.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]
    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        merge_to_stack_matlab_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["merge_to_stack_matlab"], track=tracks[track]
        )

        coregistration_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["snap"], track=tracks[track]
        )

        os.makedirs(merge_to_stack_matlab_directory, exist_ok=True)

        # generate znap-to-raw.py
        write_run_file(
            save_path=f"{merge_to_stack_matlab_directory}/merge-to-stack-matlab.py",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/merge-to-stack-matlab/merge-to-stack-matlab.py",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "general:shape-file:aoi-name",
                "general:shape-file:directory",
            ],
            other_parameters={
                "snap-output-path": coregistration_directory,
                "raw-output-path": merge_to_stack_matlab_directory,
            },
        )

        # generate znap-to-raw.sh
        write_run_file(
            save_path=f"{merge_to_stack_matlab_directory}/merge-to-stack-matlab.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/merge-to-stack-matlab/merge-to-stack-matlab.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "merge_to_stack_matlab:general:AoI-name",
                "merge_to_stack_matlab:general:depsi_group-code-directory",
            ],
            config_parameters=[
                "caroline_work_directory",
                "caroline_virtual_environment_directory",
                "python3_module",
                "gdal_module",
            ],
            other_parameters={"track": tracks[track]},
        )

        write_directory_contents(
            merge_to_stack_matlab_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["merge_to_stack_matlab"]["directory-contents-file-appendix"]}.txt',
        )


def prepare_merge_to_stack_python(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for merge_to_stack_python.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "general:tracks:track",
        "general:tracks:asc_dsc",
        "general:input-data:sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = out_parameters["general:tracks:track"]
    asc_dsc = out_parameters["general:tracks:asc_dsc"]
    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        merge_to_stack_python_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["merge_to_stack_python"], track=tracks[track]
        )

        coregistration_directory = format_process_folder(
            parameter_file=parameter_file, job_description=JOB_DEFINITIONS["snap"], track=tracks[track]
        )

        os.makedirs(merge_to_stack_python_directory, exist_ok=True)

        # generate crop-to-zarr.py
        merge_to_stack_python_output_name = merge_to_stack_python_directory.split("/")[-1]

        write_run_file(
            save_path=f"{merge_to_stack_python_directory}/merge-to-stack-python.py",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/merge-to-stack-python/merge-to-stack-python.py",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "general:shape-file:aoi-name",
                "general:shape-file:directory",
            ],
            other_parameters={
                "snap-output-path": coregistration_directory,
                "merge_to_stack_python_output_filename": merge_to_stack_python_output_name,
            },
        )

        # generate crop-to-zarr.sh
        write_run_file(
            save_path=f"{merge_to_stack_python_directory}/znap-to-zarr.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/merge-to-stack-python/merge-to-stack-python.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "merge_to_stack_python:general:AoI-name",
                "merge_to_stack_python:general:depsi_group-code-directory",
            ],
            config_parameters=[
                "caroline_work_directory",
                "caroline_virtual_environment_directory",
                "python3_module",
                "gdal_module",
            ],
            other_parameters={"track": tracks[track]},
        )

        write_directory_contents(
            merge_to_stack_python_directory,
            filename=f'dir_contents{JOB_DEFINITIONS["merge_to_stack_python"]["directory-contents-file-appendix"]}.txt',
        )


if __name__ == "__main__":
    if len(sys.argv) == 4:
        _, parameter_file, track, job = sys.argv
        track_number = int(track)

        eval(f"prepare_{job}('{parameter_file}', do_track={track_number})")

    elif len(sys.argv) == 2:
        _, job = sys.argv
        assert job == "installation", f"Missing parameter file and track for job {job}!"
        finish_installation()

    else:
        raise NotImplementedError(f"Usage: preparation.py [parameter_file] [track] job, got {sys.argv}")
