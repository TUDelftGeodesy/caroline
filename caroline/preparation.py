import glob
import os
import sys

import numpy as np

from caroline.config import get_config
from caroline.io import read_parameter_file, read_shp_extent, write_run_file
from caroline.utils import (
    detect_sensor_pixelsize,
    format_process_folder,
    generate_email,
    haversine,
    remove_incomplete_sentinel1_images,
    write_directory_contents,
)

CONFIG_PARAMETERS = get_config()


def prepare_crop(parameter_file: str, do_track: int | list | None = None) -> None:
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
        "coregistration_directory",
        "coregistration_AoI_name",
        "track",
        "asc_dsc",
        "crop_directory",
        "crop_AoI_name",
        "sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        crop_directory = format_process_folder(
            base_folder=out_parameters["crop_directory"],
            AoI_name=out_parameters["crop_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )
        coregistration_directory = format_process_folder(
            base_folder=out_parameters["coregistration_directory"],
            AoI_name=out_parameters["coregistration_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        os.makedirs(crop_directory, exist_ok=True)

        # soft-link the processing directory without job_id.txt, dir_contents.txt and queue.txt
        # Sentinel-1 has more files starting with d as Doris-v5 output, other sensors do not have that
        if out_parameters["sensor"] == "S1":
            link_keys = ["[bgiprs]*", "doris*", "dem"]
        else:
            link_keys = ["[bgiprs]*"]
        for key in link_keys:
            # run the soft-link command
            os.system(f"ln -sfn {coregistration_directory}/{key} {crop_directory}")

        # generate crop.sh
        write_run_file(
            save_path=f"{crop_directory}/crop.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/crop/crop.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["crop_AoI_name"],
            config_parameters=["caroline_work_directory"],
            other_parameters={"track": tracks[track], "crop_base_directory": crop_directory},
        )

        # generate crop.m
        write_run_file(
            save_path=f"{crop_directory}/crop.m",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/crop/crop.m",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["shape_AoI_name", "shape_directory", "sensor"],
            config_parameters=["caroline_install_directory"],
        )

        write_directory_contents(crop_directory)


def prepare_deinsar(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for DeInSAR.

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
        "coregistration_directory",
        "coregistration_AoI_name",
        "track",
        "asc_dsc",
        "sensor",
        "di_data_directories",
        "start_date",
        "end_date",
        "master_date",
        "dem_size",
        "dem_upperleft",
        "dem_delta",
        "shape_directory",
        "shape_AoI_name",
        "di_finecoreg_mode",
        "polarisation",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    datadirs = eval(out_parameters["di_data_directories"])

    start_date = eval(out_parameters["start_date"].replace("-", ""))
    master_date = eval(out_parameters["master_date"].replace("-", ""))
    end_date = eval(out_parameters["end_date"].replace("-", ""))

    polarisation = eval(out_parameters["polarisation"])
    polarisation = [f"_{pol}" for pol in polarisation]
    if "_HH" in polarisation:
        polarisation[polarisation.index("_HH")] = ""

    dem_delta = eval(out_parameters["dem_delta"])
    dem_size = eval(out_parameters["dem_size"])
    dem_upperleft = eval(out_parameters["dem_upperleft"])

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        assert (
            f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}" in datadirs.keys()
        ), f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d} is not in di_data_directories!"

        coregistration_directory = format_process_folder(
            base_folder=out_parameters["coregistration_directory"],
            AoI_name=out_parameters["coregistration_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        # we need a process folder in the coregistration directory, so we can combine that command
        os.makedirs(f"{coregistration_directory}/process", exist_ok=True)

        # generate deinsar.sh
        write_run_file(
            save_path=f"{coregistration_directory}/run_deinsar.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/deinsar/run_deinsar.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["deinsar_code_directory", "doris_v4_code_directory", "coregistration_AoI_name"],
            config_parameters=["caroline_work_directory", "orbit_directory"],
            other_parameters={"track": tracks[track], "crop_base_directory": coregistration_directory},
        )

        # generate run_deinsar.py

        # first search for the start, end, and master dates by parsing all data in the data directory,
        # which is different per sensor
        datadir = datadirs[f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}"]
        if out_parameters["sensor"] in ["ALOS2", "ERS"]:
            dirs = glob.glob(f"{datadir}/[12]*")
            images = list(sorted([eval(image.split("/")[-1]) for image in dirs]))
        elif out_parameters["sensor"] in ["RSAT2"]:
            dirs = glob.glob(f"{datadir}/RS2*")
            images = list(sorted([eval(image.split("/")[-1].split("FQ2_")[1].split("_")[0]) for image in dirs]))
        elif out_parameters["sensor"] in ["TSX"]:
            dirs = glob.glob(f"{datadir}/*/iif/*")
            images = list(sorted([eval(image.split("/")[-1].split("SRA_")[1].split("T")[0]) for image in dirs]))
        elif out_parameters["sensor"] in ["SAOCOM"]:
            dirs = glob.glob(f"{datadir}/*/*.xemt")
            images = list(sorted([eval(image.split("/")[-1].split("OLF_")[1].split("T")[0]) for image in dirs]))
        elif out_parameters["sensor"] in ["ENV"]:
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
            raise ValueError(f'Unknown directory format for sensor {out_parameters["sensor"]}!')

        # then select the start, end, and master dates
        act_start_date = str(min([image for image in images if image >= start_date]))
        act_end_date = str(max([image for image in images if image <= end_date]))
        act_master_date = str(min([image for image in images if image >= master_date]))

        # finally, write run_deinsar.py
        write_run_file(
            save_path=f"{coregistration_directory}/run_deinsar.py",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/deinsar/run_deinsar.py",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                ["di_data_directories", "dictionary"],
                "sensor",
                "polarisation",
                "di_do_orbit",
                "di_do_crop",
                "di_do_tsx_deramp",
                "di_do_simamp",
                "di_do_mtiming",
                "di_do_ovs",
                "di_do_choose_master",
                "di_do_coarseorb",
                "di_do_coarsecorr",
                "di_do_finecoreg",
                "di_do_reltiming",
                "di_do_dembased",
                "di_do_coregpm",
                "di_do_comprefpha",
                "di_do_comprefdem",
                "di_do_resample",
                "di_do_tsx_reramp",
                "di_do_interferogram",
                "di_do_subtrrefpha",
                "di_do_subtrrefdem",
                "di_do_coherence",
                "di_do_geocoding",
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
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/deinsar/input_files/{file}",
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
                    f"templates/deinsar/input_files/{file}",
                    asc_dsc=asc_dsc[track],
                    track=tracks[track],
                    parameter_file=parameter_file,
                    other_parameters={"pol": pol},
                )

        # these ones need the DEM variables
        for file in ["input.comprefdem", "input.dembased", "input.simamp"]:
            write_run_file(
                save_path=f"{coregistration_directory}/process/{file}",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/deinsar/input_files/{file}",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
                parameter_file_parameters=["dem_file", "dem_format", "dem_nodata"],
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
        if out_parameters["di_finecoreg_mode"] == "simple":
            write_run_file(
                save_path=f"{coregistration_directory}/process/input.finecoreg_simple",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                f"templates/deinsar/input_files/input.finecoreg",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
                other_parameters={"nwin": 5000},
            )
        else:  # normal mode
            write_run_file(
                save_path=f"{coregistration_directory}/process/input.finecoreg",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                f"templates/deinsar/input_files/input.finecoreg",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
                other_parameters={"nwin": 8000},
            )

        # porbit is only necessary for ERS and ENV
        if out_parameters["sensor"] == "ERS":
            # this one requires two copies
            for satellite in [1, 2]:
                write_run_file(
                    save_path=f"{coregistration_directory}/process/input.porbit_ERS{satellite}",
                    template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                    f"templates/deinsar/input_files/input.porbit",
                    asc_dsc=asc_dsc[track],
                    track=tracks[track],
                    parameter_file=parameter_file,
                    other_parameters={"directory": f"ERS{satellite}"},
                )
        elif out_parameters["sensor"] == "ENV":
            write_run_file(
                save_path=f"{coregistration_directory}/process/input.porbit",
                template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                f"templates/deinsar/input_files/input.porbit",
                asc_dsc=asc_dsc[track],
                track=tracks[track],
                parameter_file=parameter_file,
                other_parameters={"directory": "envisat/dor_vor_odr"},
            )

        # for input.crop and input.resample we need to read the shapefile extent and calculate the amount of pixels
        coordinates = np.array(
            read_shp_extent(
                f"{out_parameters['shape_directory']}/" f"{out_parameters['shape_AoI_name']}_shape.shp", mode="AoI"
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
        d_az, d_r = detect_sensor_pixelsize(out_parameters["sensor"])
        pix_dr = int(np.ceil(dist_lon / d_r * 1.05))
        pix_daz = int(np.ceil(dist_lat / d_az * 1.05))

        # for input.crop we will add 500 to eliminate edge effects
        if out_parameters["sensor"] == "ALOS2":
            img_name = "IMG.1"
        elif out_parameters["sensor"] == "Cosmo":
            img_name = "image.h5"
        elif out_parameters["sensor"] == "ENV":
            img_name = "image.N1"
        elif out_parameters["sensor"] == "ERS":
            img_name = "DAT_01.001"
        elif out_parameters["sensor"] == "RSAT2":
            img_name = "imagery{pol}.tif"
            # requires loop over polarisations to get additional crop files
        elif out_parameters["sensor"] == "TSX":
            img_name = "image.cos"
        else:
            raise ValueError(f'Unknown sensor {out_parameters["sensor"]}!')

        # write input.crop
        if out_parameters["sensor"] == "RSAT2":  # for RSAT2 this is per polarisation, otherwise there just is one
            for pol in polarisation:
                write_run_file(
                    save_path=f"{coregistration_directory}/process/input.crop{pol}",
                    template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
                    f"templates/deinsar/input_files/input.crop",
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
                f"templates/deinsar/input_files/input.crop",
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
                f"templates/deinsar/input_files/input.resample",
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
        if out_parameters["sensor"] == "ALOS2":
            data_string = """S_IN_METHOD     ALOS2
S_IN_DAT        IMG.1
S_IN_LEA        LED.1
S_IN_VOL        VOL.1"""

        elif out_parameters["sensor"] == "Cosmo":
            data_string = """S_IN_METHOD     CSK
S_IN_DAT        image.h5"""

        elif out_parameters["sensor"] == "ERS":
            data_string = """S_IN_METHOD     ERS
S_IN_VOL        VRD_DAT.001
S_IN_DAT        DAT_01.001
S_IN_LEA        LEA_01.001
S_IN_NULL       dummy"""

        elif out_parameters["sensor"] == "ENV":
            data_string = """S_IN_METHOD     ASAR
S_IN_DAT        image.N1"""

        elif out_parameters["sensor"] == "RSAT":
            data_string = """S_IN_METHOD     RSAT
S_IN_VOL        VDF_DAT.001
S_IN_DAT        DAT_01.001
S_IN_LEA        LEA_01.001
S_IN_NULL       dummy"""

        elif out_parameters["sensor"] == "RSAT2":
            data_string = """S_IN_METHOD     RADARSAT-2
S_IN_DAT        imagery_HH.tif
S_IN_LEA        product.xml"""

        elif out_parameters["sensor"] == "TSX":
            data_string = """S_IN_METHOD     TSX
S_IN_DAT        image.cos
S_IN_LEA        leader.xml"""

        else:
            raise ValueError(f'Unknown sensor {out_parameters["sensor"]}!')

        write_run_file(
            save_path=f"{coregistration_directory}/process/input.readfiles",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/"
            f"templates/deinsar/input_files/input.readfiles",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            other_parameters={"data_string": data_string},
        )

        write_directory_contents(coregistration_directory)


def prepare_depsi(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and files for DePSI.

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
        "depsi_directory",
        "depsi_AoI_name",
        "track",
        "asc_dsc",
        "sensor",
        "crop_directory",
        "crop_AoI_name",
        "depsi_code_dir",
        "rdnaptrans_dir",
        "geocoding_dir",
        "start_date",
        "end_date",
        "ref_cn",
        "do_water_mask",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])
    start_date = out_parameters["start_date"].replace("-", "")
    end_date = out_parameters["end_date"].replace("-", "")

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        depsi_directory = format_process_folder(
            base_folder=out_parameters["depsi_directory"],
            AoI_name=out_parameters["depsi_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        crop_directory = format_process_folder(
            base_folder=out_parameters["crop_directory"],
            AoI_name=out_parameters["crop_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        # if a previous run exists, first move it out of the way
        if os.path.exists(depsi_directory):
            os.system(f'''mv "{depsi_directory}" "{depsi_directory}-$(date +%Y%m%dT%H%M%S)"''')

        # we need a psi and boxes folder in the depsi directory
        os.makedirs(f"{depsi_directory}/psi", exist_ok=True)
        os.makedirs(f"{depsi_directory}/boxes", exist_ok=True)

        # link the necessary boxes
        os.system(f"cp -Rp {out_parameters['depsi_code_dir']} {depsi_directory}/boxes")
        os.system(f"cp -Rp {out_parameters['rdnaptrans_dir']} {depsi_directory}/boxes")
        os.system(f"cp -Rp {out_parameters['geocoding_dir']} {depsi_directory}/boxes")

        # detect the mother and dem_radar from the mother
        mother = glob.glob(f"{crop_directory}/*cropped_stack/2*/master.res")[0]
        # cut off master.res, and add dem_radar.raw
        dem_radar = mother.replace("/master.res", "/dem_radar.raw")
        mother_date = mother.split("/")[-2]

        # link the mother resfile and dem_radar
        os.system(f"ln -sf {mother} {depsi_directory}/psi/slave.res")
        os.system(f"ln -sf {dem_radar} {depsi_directory}/psi/dem_radar.raw")

        # find the first and last valid dates within range
        if os.path.exists(f"{crop_directory}/cropped_stack/path_res_files.txt"):
            f = open(f"{crop_directory}/cropped_stack/path_res_files.txt")
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
        if out_parameters["do_water_mask"] == "yes":
            filename_water_mask = (
                f"{CONFIG_PARAMETERS['CAROLINE_WATER_MASK_DIRECTORY']}/water_mask_{out_parameters['depsi_AoI_name']}_"
                f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}.raw"
            )
        else:
            filename_water_mask = "[]"

        # #62 -> figure out the reference point
        if out_parameters["ref_cn"][0] == "{":  # it's a dictionary
            data = eval(out_parameters["ref_cn"])
            assert f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}" in data.keys(), (
                f"Cannot find {out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d} "
                f"in ref_cn {data}!"
            )
            mode = str(data[f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}"])
        else:
            mode = str(out_parameters["ref_cn"])

        if mode in ["independent", "[]"]:
            ref_cn = "[]"
        elif mode[0] == "[":  # hardcoded
            ref_cn = mode.replace(" ", "")  # remove spaces since Matlab doesn't like them
        elif mode == "constant":
            # find the old runs
            directories = glob.glob(f"{depsi_directory}-*")
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
                        f"{rev_order_runs[i]}/psi/{out_parameters['depsi_AoI_name']}_"
                        f"{out_parameters['sensor'].lower()}_"
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
            save_path=f"{depsi_directory}/psi/depsi.m",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/depsi/depsi.m",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            other_parameters={
                "geocoding_version": out_parameters["geocoding_dir"].split("/")[-1].rstrip(),
                "depsi_version": out_parameters["depsi_code_dir"].split("/")[-1].rstrip(),
            },
        )

        # write depsi.sh
        write_run_file(
            save_path=f"{depsi_directory}/psi/depsi.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/depsi/depsi.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["depsi_AoI_name"],
            config_parameters=["caroline_work_directory"],
            other_parameters={"depsi_base_directory": depsi_directory, "track": tracks[track]},
        )

        # create param_file_depsi.txt
        #
        write_run_file(
            save_path=f"{depsi_directory}/psi/param_file_depsi.txt",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/depsi/param_file.txt",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "depsi_AoI_name",
                "max_mem_buffer",
                "visible_plots",
                "detail_plots",
                "processing_groups",
                "run_mode",
                ["sensor", "lowercase"],
                "exclude_date",
                "az_spacing",
                "r_spacing",
                "slc_selection_input",
                "ifg_selection_input",
                "Ncv",
                "ps_method",
                "psc_model",
                "ps_model",
                "final_model",
                "breakpoint",
                "breakpoint2",
                "ens_coh_threshold",
                "varfac_threshold",
                "detrend_method",
                "output_format",
                "do_apriori_sidelobe_mask",
                "do_aposteriori_sidelobe_mask",
                "ref_height",
                "amplitude_calibration",
                "psc_selection_method",
                "psc_selection_gridsize",
                "psc_threshold",
                "max_arc_length",
                "network_method",
                "Ncon",
                "Nparts",
                "Npsc_selections",
                "gamma_threshold",
                "psc_distribution",
                "weighted_unwrap",
                "livetime_threshold",
                "peak_tolerance",
                "psp_selection_method",
                "psp_threshold1",
                "psp_threshold2",
                "ps_eval_method",
                "Namp_disp_bins",
                "Ndens_iterations",
                "densification_flag",
                "ps_area_of_interest",
                "dens_method",
                "dens_check",
                "Nest",
                "defo_range",
                "weighting",
                "ts_atmo_filter",
                "ts_atmo_filter_length",
                "ts_noise_filter",
                "ts_noise_filter_length",
                "defo_method",
                "xc0",
                "yc0",
                "zc0",
                "r0",
                "r10",
                "epoch",
                ["stc_min_max", "strip", "[] "],
                ["std_param", "strip", "[] "],
            ],
            other_parameters={
                "crop_base_directory": crop_directory,
                "track": f"{tracks[track]:0>3d}",
                "asc_dsc": asc_dsc[track],
                "start_date": act_start_date,
                "stop_date": act_end_date,
                "master_date": mother_date,
                "ref_cn": ref_cn,
                "filename_water_mask": filename_water_mask,
            },
        )

        write_directory_contents(f"{depsi_directory}/psi")


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
        "depsi_directory",
        "depsi_AoI_name",
        "track",
        "asc_dsc",
        "sensor",
        "depsi_post_dir",
        "geocoding_dir",
        "rdnaptrans_dir",
        "dp_defo_clim",
        "dp_height_clim",
        "depsi_post_mode",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    defo_clim_raw = out_parameters["dp_defo_clim"]
    defo_clim_min = defo_clim_raw.split(",")[0][1:].strip()
    defo_clim_max = defo_clim_raw.split(",")[1][:-1].strip()

    height_clim_raw = out_parameters["dp_height_clim"]
    height_clim_min = height_clim_raw.split(",")[0][1:].strip()
    height_clim_max = height_clim_raw.split(",")[1][:-1].strip()

    if out_parameters["depsi_post_mode"] == "tarball":
        do_csv = 0
    elif out_parameters["depsi_post_mode"] == "csv":
        do_csv = 1
    else:
        raise ValueError(
            f"depsi_post_mode is set to {out_parameters['depsi_post_mode']}, only know 'tarball' and 'csv'!"
        )

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        depsi_directory = format_process_folder(
            base_folder=out_parameters["depsi_directory"],
            AoI_name=out_parameters["depsi_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        # link the DePSI-post box
        os.system(f"cp -Rp {out_parameters['depsi_post_dir']} {depsi_directory}/boxes")

        # write depsi_post.m
        write_run_file(
            save_path=f"{depsi_directory}/psi/depsi_post.m",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/depsi_post/depsi_post.m",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "dp_dlat",
                "dp_dlon",
                "dp_drdx",
                "dp_drdy",
                "sensor",
                "depsi_AoI_name",
                "dp_proj",
                "dp_ref_dheight",
                "dp_posteriori_scale_factor",
                ["dp_pred_model", "strip", " "],
                "dp_plot_mode",
                ["dp_do_plots", "strip", "{} "],
                ["dp_output", "strip", "{} "],
                "dp_fontsize",
                "dp_markersize",
                "dp_do_print",
                "dp_output_format",
                "dp_az0",
                "dp_azN",
                "dp_r0",
                "dp_rN",
                "dp_result",
                "dp_psc_selection",
                "dp_do_remove_filtered",
                "dp_which_sl_mask",
                "dp_shift_to_mean",
                "dp_new_ref_cn",
                "dp_map_to_vert",
                "dp_defo_lim",
                "dp_height_lim",
                "dp_ens_coh_lim",
                "dp_ens_coh_local_lim",
                "dp_stc_lim",
                "dp_ens_coh_clim",
                "dp_ens_coh_local_clim",
                "dp_stc_clim",
            ],
            other_parameters={
                "geocoding_version": out_parameters["geocoding_dir"].split("/")[-1].rstrip(),
                "depsi_post_version": out_parameters["depsi_post_dir"].split("/")[-1].rstrip(),
                "rdnaptrans_version": out_parameters["rdnaptrans_dir"].split("/")[-1].rstrip(),
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
            save_path=f"{depsi_directory}/psi/depsi_post.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/depsi_post/depsi_post.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["depsi_AoI_name"],
            config_parameters=["caroline_work_directory"],
            other_parameters={"track": tracks[track], "depsi_base_directory": depsi_directory},
        )

        write_directory_contents(f"{depsi_directory}/psi", filename="dir_contents_depsi_post.txt")


def prepare_doris(parameter_file: str, do_track: int | list | None = None) -> None:
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
        "coregistration_directory",
        "coregistration_AoI_name",
        "track",
        "asc_dsc",
        "sensor",
        "dem_delta",
        "dem_upperleft",
        "dem_size",
        "dem_file",
        "start_date",
        "end_date",
        "master_date",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    dem_delta = eval(out_parameters["dem_delta"])
    dem_size = eval(out_parameters["dem_size"])
    dem_upperleft = eval(out_parameters["dem_upperleft"])

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        coregistration_directory = format_process_folder(
            base_folder=out_parameters["coregistration_directory"],
            AoI_name=out_parameters["coregistration_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
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
        dem_directory = "/".join(out_parameters["dem_file"].split("/")[:-1])
        os.system(f"ln -sfn {dem_directory} {coregistration_directory}/dem")

        # generate the input files
        input_files = glob.glob(
            f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/" "doris/input_files/input.*"
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
                    parameter_file_parameters=["dem_file", "dem_format", "dem_nodata"],
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
            "do_coarse_orbits",
            "do_deramp",
            "do_reramp",
            "do_fake_fine_coreg_bursts",
            "do_dac_bursts",
            "do_fake_coreg_bursts",
            "do_fake_master_resample",
            "do_resample",
            "do_reramp2",
            "do_interferogram",
            "do_compref_phase",
            "do_compref_dem",
            "do_coherence",
            "do_esd",
            "do_network_esd",
            "do_ESD_correct",
            "do_combine_master",
            "do_combine_slave",
            "do_ref_phase",
            "do_ref_dem",
            "do_phasefilt",
            "do_calc_coordinates",
            "do_multilooking",
            "do_unwrap",
        ]:
            value = read_parameter_file(parameter_file, [parameter])[parameter]
            if value == "1":
                other_parameters[parameter] = "Yes"
            else:
                other_parameters[parameter] = "No"

        # we also need the track and orbit direction
        other_parameters["track"] = tracks[track]
        other_parameters["asc_dsc"] = asc_dsc[track]

        # and the start, end, and mother dates
        images = glob.glob(f"{coregistration_directory}/good_images/2*")
        images = [eval(image.split("/")[-1]) for image in images]

        start_date = eval(out_parameters["start_date"].replace("-", ""))
        end_date = eval(out_parameters["end_date"].replace("-", ""))
        master_date = eval(out_parameters["master_date"].replace("-", ""))

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
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/doris/doris_input.xml",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["shape_directory", "shape_AoI_name"],
            config_parameters=["orbit_directory"],
            other_parameters=other_parameters,
        )

        # write doris_stack.sh
        write_run_file(
            save_path=f"{coregistration_directory}/doris_stack.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/doris/doris_stack.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["coregistration_AoI_name", "doris_code_directory"],
            config_parameters=["caroline_work_directory", "caroline_virtual_environment_directory"],
            other_parameters={"track": tracks[track], "coregistration_directory": coregistration_directory},
        )

        write_directory_contents(coregistration_directory)


def prepare_doris_cleanup(parameter_file: str, do_track: int | list | None = None) -> None:
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
        "coregistration_directory",
        "coregistration_AoI_name",
        "track",
        "asc_dsc",
        "sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        coregistration_directory = format_process_folder(
            base_folder=out_parameters["coregistration_directory"],
            AoI_name=out_parameters["coregistration_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        write_run_file(
            save_path=f"{coregistration_directory}/cleanup.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/"
            "doris/cleanup-doris-s1-stack.sh",
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
    parameters = read_parameter_file(parameter_file, ["send_completion_email", "sensor", "track", "asc_dsc"])
    area_name = parameter_file.split("/")[-1].split(".")[0].split("param_file_")[-1]

    tracks = eval(parameters["track"])
    asc_dsc = eval(parameters["asc_dsc"])
    track_csv = ""
    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if do_track == tracks[track]:
                track_csv += f"{parameters['sensor']}_{asc_dsc[track]}_t{tracks[track]:0>3d},"
        elif isinstance(do_track, list):
            if tracks[track] in do_track:
                track_csv += f"{parameters['sensor']}_{asc_dsc[track]}_t{tracks[track]:0>3d},"
        else:
            track_csv += f"{parameters['sensor']}_{asc_dsc[track]}_t{tracks[track]:0>3d},"

    track_csv = track_csv.strip(",")
    header = f"CAROLINE: {parameters['sensor']}/{area_name}/{track_csv}"
    os.system(f"""echo "Subject: {header}

{body}" | {CONFIG_PARAMETERS['SENDMAIL_DIRECTORY']} {parameters['send_completion_email']}""")


def prepare_mrm(parameter_file: str, do_track: int | list | None = None) -> None:
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
        "crop_directory",
        "crop_AoI_name",
        "depsi_directory",
        "depsi_AoI_name",
        "track",
        "asc_dsc",
        "sensor",
        "cpxfiddle_dir",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        crop_directory = format_process_folder(
            base_folder=out_parameters["crop_directory"],
            AoI_name=out_parameters["crop_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )
        depsi_directory = format_process_folder(
            base_folder=out_parameters["depsi_directory"],
            AoI_name=out_parameters["depsi_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        # we need to run cpxfiddle first. This requires two parameters: n_lines, and the project ID
        fr = open(f"{crop_directory}/cropped_stack/nlines_crp.txt")
        data = fr.read().split("\n")
        fr.close()
        n_lines = data[0]

        project_id = depsi_directory.split("/")[-1]

        # format the arguments in the correct order
        command_args = f"{project_id} {n_lines} 1 1 {out_parameters['cpxfiddle_dir']} {depsi_directory}/psi"
        os.system(
            f"bash {CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/scripts/create_mrm_ras_header.sh "
            f"{command_args}"
        )

        write_run_file(
            save_path=f"{depsi_directory}/psi/read_mrm.m",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/mrm/read_mrm.m",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "depsi_AoI_name",
                ["sensor", "lowercase"],
            ],
            other_parameters={
                "fill_track": f"{tracks[track]:0>3d}",
                "asc_dsc": asc_dsc[track],
            },
        )

        write_run_file(
            save_path=f"{depsi_directory}/psi/read_mrm.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/mrm/read_mrm.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["depsi_AoI_name"],
            config_parameters=["caroline_work_directory"],
            other_parameters={
                "track": tracks[track],
                "depsi_base_directory": depsi_directory,
            },
        )

        write_directory_contents(f"{depsi_directory}/psi", filename="dir_contents_read_mrm.txt")


def prepare_portal_upload(parameter_file: str, do_track: int | list | None = None) -> None:
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
        "depsi_directory",
        "depsi_AoI_name",
        "track",
        "asc_dsc",
        "sensor",
        "skygeo_customer",
        "skygeo_viewer",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        depsi_directory = format_process_folder(
            base_folder=out_parameters["depsi_directory"],
            AoI_name=out_parameters["depsi_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        # The parameter file already contains a datestamp so we don't need to redo that
        portal_upload_file = (
            f"{CONFIG_PARAMETERS['PORTAL_UPLOAD_FLAG_DIRECTORY']}/"
            f"{parameter_file.split('/')[-1].split('.')[0]}_t{tracks[track]:0>3d}_upload.txt"
        )
        f = open(portal_upload_file, "w")
        f.write(
            f"Status: TBD\n"
            f"Directory: {depsi_directory}/psi\n"
            f"Viewer: {out_parameters['skygeo_viewer']}\n"
            f"Customer: {out_parameters['skygeo_customer']}"
        )
        f.close()


def prepare_reslc(parameter_file: str, do_track: int | list | None = None) -> None:
    """Set up the directories and run files for re-SLC.

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
        If the mother image cannot be detected from doris_input.xml (S1) or deinsar.py (otherwise)
    """
    search_parameters = [
        "reslc_directory",
        "reslc_AoI_name",
        "coregistration_directory",
        "coregistration_AoI_name",
        "track",
        "asc_dsc",
        "sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        reslc_directory = format_process_folder(
            base_folder=out_parameters["reslc_directory"],
            AoI_name=out_parameters["reslc_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        coregistration_directory = format_process_folder(
            base_folder=out_parameters["coregistration_directory"],
            AoI_name=out_parameters["coregistration_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        os.makedirs(reslc_directory, exist_ok=True)

        # detect the mother image
        if out_parameters["sensor"].lower() == "s1":
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
            f = open(f"{coregistration_directory}/run_deinsar.py")
            data = f.read().split("\n")
            f.close()
            mother = None
            for line in data:
                if "master = " in line:
                    mother = line.split("'")[1]
                    break

            if mother is None:
                raise ValueError(f"Failed to detect mother in {coregistration_directory}/run_deinsar.py !")

        # generate reslc.py
        reslc_output_name = reslc_directory.split("/")[-1]

        write_run_file(
            save_path=f"{reslc_directory}/reslc.py",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/reslc/reslc.py",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=["shape_AoI_name", "sensor", "shape_directory"],
            other_parameters={
                "coregistration_directory": coregistration_directory,
                "stack_folder_name": "stack" if out_parameters["sensor"] == "S1" else "process",
                "mother": mother,
                "mother_slc_name": "slave_rsmp_reramped.raw" if out_parameters["sensor"] == "S1" else "slave_rsmp.raw",
                "reslc_output_filename": reslc_output_name,
            },
        )

        # generate reslc.sh
        write_run_file(
            save_path=f"{reslc_directory}/reslc.sh",
            template_path=f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/templates/reslc/reslc.sh",
            asc_dsc=asc_dsc[track],
            track=tracks[track],
            parameter_file=parameter_file,
            parameter_file_parameters=[
                "reslc_AoI_name",
                "reslc_code_dir",
            ],
            config_parameters=["caroline_work_directory", "caroline_virtual_environment_directory"],
            other_parameters={"track": tracks[track]},
        )

        write_directory_contents(reslc_directory)


def prepare_tarball(parameter_file: str, do_track: int | list | None = None) -> None:
    """Create the tarball after DePSI-post.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    do_track: int | list | None, optional
        Track number, or list of track numbers, of the track(s) to prepare. `None` (default) prepares all tracks in
        the parameter file
    """
    search_parameters = [
        "depsi_directory",
        "depsi_AoI_name",
        "track",
        "asc_dsc",
        "sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    for track in range(len(tracks)):
        if isinstance(do_track, int):
            if tracks[track] != do_track:
                continue
        elif isinstance(do_track, list):
            if tracks[track] not in do_track:
                continue

        depsi_directory = format_process_folder(
            base_folder=out_parameters["depsi_directory"],
            AoI_name=out_parameters["depsi_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        project_id = depsi_directory.split("/")[-1]
        os.system(
            f"cd {depsi_directory}; "
            f"bash {CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/scripts/create_post_project_tar.sh {project_id}"
        )


if __name__ == "__main__":
    _, parameter_file, track, job = sys.argv
    track_number = int(track)
    if job == "coregistration":
        sensor = read_parameter_file(parameter_file, ["sensor"])["sensor"]
        if sensor == "S1":
            prepare_doris(parameter_file, do_track=track_number)
        else:
            prepare_deinsar(parameter_file, do_track=track_number)
    else:
        eval(f"prepare_{job}('{parameter_file}', do_track={track_number})")
