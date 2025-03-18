import glob
import os

from caroline.io import read_parameter_file, write_run_file
from caroline.utils import format_process_folder, remove_incomplete_sentinel1_images

CONFIG_PARAMETERS = {
    "CAROLINE_WORK_DIRECTORY": "/project/caroline/Software/run/caroline/work",
    "SLC_BASE_DIRECTORY": "/project/caroline/Data/radar_data/sentinel1",
    "CAROLINE_INSTALL_DIRECTORY": "/project/caroline/Software/caroline",
}


def prepare_crop(parameter_file: str) -> None:
    """Set up the directories for cropping.

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
    """Set up the directories for DeInSAR.

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
        os.makedirs(f"{coregistration_directory}/process", exist_ok=True)


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
