import glob
import os

import numpy as np

from caroline.io import read_parameter_file, read_shp_extent, write_run_file
from caroline.utils import detect_sensor_pixelsize, format_process_folder, haversine, remove_incomplete_sentinel1_images

CONFIG_PARAMETERS = {
    "CAROLINE_WORK_DIRECTORY": "/project/caroline/Software/run/caroline/work",
    "SLC_BASE_DIRECTORY": "/project/caroline/Data/radar_data/sentinel1",
    "ORBIT_DIRECTORY": "/project/caroline/Data/orbits",
    "CAROLINE_INSTALL_DIRECTORY": "/project/caroline/Software/caroline",
}


def prepare_crop(parameter_file: str) -> None:
    """Set up the directories and run files for cropping.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
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


def prepare_deinsar(parameter_file: str) -> None:
    """Set up the directories and run files for DeInSAR.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.

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
        assert (
            f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_{tracks[track]:0>3d}" in datadirs.keys()
        ), f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_{tracks[track]:0>3d} is not in di_data_directories!"

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
        datadir = datadirs[f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_{tracks[track]:0>3d}"]
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


def prepare_depsi(parameter_file: str) -> None:
    """Set up the directories for DePSI.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
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
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    for track in range(len(tracks)):
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

        # link the mother resfile and dem_radar
        os.system(f"ln -sf {mother} {depsi_directory}/psi/slave.res")
        os.system(f"ln -sf {dem_radar} {depsi_directory}/psi/dem_radar.raw")


def prepare_doris(parameter_file: str) -> None:
    """Set up the directories for Doris v5.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
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


def prepare_mrm(parameter_file: str) -> None:
    """Set up the directories for mrm creation, part of DePSI-post.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
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


def prepare_reslc(parameter_file: str) -> None:
    """Set up the directories for re-SLC.

    Parameters
    ----------
    parameter_file: str
        Absolute path to the parameter file.
    """
    search_parameters = [
        "reslc_directory",
        "reslc_AoI_name",
        "track",
        "asc_dsc",
        "sensor",
    ]
    out_parameters = read_parameter_file(parameter_file, search_parameters)

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    for track in range(len(tracks)):
        reslc_directory = format_process_folder(
            base_folder=out_parameters["reslc_directory"],
            AoI_name=out_parameters["reslc_AoI_name"],
            sensor=out_parameters["sensor"],
            asc_dsc=asc_dsc[track],
            track=tracks[track],
        )

        os.makedirs(reslc_directory, exist_ok=True)
