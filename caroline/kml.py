import glob
import os
from typing import Literal

from caroline.config import get_config
from caroline.io import read_parameter_file, read_shp_extent, read_SLC_json, read_SLC_xml
from caroline.parameter_file import generate_full_parameter_file
from caroline.utils import (
    convert_bytesize_to_humanreadable,
    get_path_bytesize,
    get_processing_time,
    identify_s1_orbits_in_aoi,
    job_schedule_check,
)

CONFIG_PARAMETERS = get_config()
JOB_DEFINITIONS = get_config(
    f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/job-definitions.yaml", flatten=False
)


class KML:
    def __init__(self, save_path: str) -> None:
        """Write coloured polygons into a KML.

        Parameters
        ----------
        save_path: str
            Location to save the KML.
        """
        self.save_path = save_path
        self.kml = ""
        self._prepare_kml()

    def _prepare_kml(self) -> None:
        """Initialize the KML by adding the necessary decorators."""
        self.kml += """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
"""
        self._add_kml_styles()

    def _finish_kml(self) -> None:
        """Add the remaining decorators to the KML."""
        self.kml += """</Document>
</kml>"""

    def save(self) -> None:
        """Save the KML."""
        self._finish_kml()
        f = open(self.save_path, "w")
        f.write(self.kml)
        f.close()

    def _add_kml_styles(self) -> None:
        """Add the style maps to the KML."""
        self.kml += """    <StyleMap id="SLC">
        <Pair>
            <key>normal</key>
            <styleUrl>#SLC-n</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#SLC-h</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="SLC-n">
        <LineStyle>
            <color>ff0000ff</color>
            <width>1</width>
        </LineStyle>
        <PolyStyle>
            <color>8014B4FF</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <Style id="SLC-h">
        <LineStyle>
            <color>ff00ffff</color>
            <width>3</width>
        </LineStyle>
        <PolyStyle>
            <color>5014B4FF</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <StyleMap id="AoI">
        <Pair>
            <key>normal</key>
            <styleUrl>#AoI-n</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#AoI-h</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="AoI-n">
        <LineStyle>
            <color>ff00ff00</color>
            <width>1</width>
        </LineStyle>
        <PolyStyle>
            <color>8078E352</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <Style id="AoI-h">
        <LineStyle>
            <color>ff00ffff</color>
            <width>3</width>
        </LineStyle>
        <PolyStyle>
            <color>5078E352</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <StyleMap id="stack">
        <Pair>
            <key>normal</key>
            <styleUrl>#stack-n</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#stack-h</styleUrl>
        </Pair>
    </StyleMap>
    <Style id="stack-n">
        <LineStyle>
            <color>ffff0000</color>
            <width>1</width>
        </LineStyle>
        <PolyStyle>
            <color>80919C8E</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <Style id="stack-h">
        <LineStyle>
            <color>ff00ffff</color>
            <width>3</width>
        </LineStyle>
        <PolyStyle>
            <color>50919C8E</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>    
"""

    def open_folder(self, folder_name: str, folder_description: str = "") -> None:
        """Open a folder in the KML.

        Parameters
        ----------
        folder_name: str
            Name of the folder
        folder_description: str
            Description of the folder. Default empty.

        """
        self.kml += f"""<Folder>
    <name>{folder_name}</name>
    <description>{folder_description}</description>
"""

    def close_folder(self) -> None:
        """Close a folder opened by `open_folder`."""
        self.kml += "</Folder>\n"

    def add_polygon(
        self, coordinate_list: list, name: str, description: str, style: Literal["SLC", "AoI", "stack"]
    ) -> None:
        """Add a polygon to self.kml.

        Parameters
        ----------
        coordinate_list: list
            The coordinates of the polygon
        name: str
            Name to be given to the polygon
        description:
            Description to be added to the polygon on clicking
        style: Literal["SLC", "AoI", "stack"]
            Style of colouring of the polygon. Options are "SLC" (red), "AoI" (green), "stack" (blue)

        """
        self.kml += f"""<Placemark>
    <name>{name}</name>
    <description>{description}</description>
    <styleUrl>#{style}</styleUrl>
    <Polygon>
        <outerBoundaryIs>
            <LinearRing>
                <coordinates>
"""

        for coordinate in coordinate_list:
            self.kml += f"                  {coordinate[0]},{coordinate[1]}\n"

        self.kml += """             </coordinates>
            </LinearRing>
        </outerBoundaryIs>
    </Polygon>
</Placemark>"""


def add_AoI_extent_folder(kml: KML) -> KML:
    """Add the folder containing the extents of all AoIs available in Caroline to the provided KML.

    Parameters
    ----------
    kml: caroline.kml.KML
        KML to which the AoI extents folder should be added

    Returns
    -------
    caroline.kml.KML
        KML with the AoI extents folder added

    Raises
    ------
    AssertionError
        when kml is not an instance of caroline.kml.KML
    """
    assert isinstance(kml, KML), f"provided kml is type {type(kml)}, not caroline.kml.KML!"

    # read the parameter file data
    param_file_data = read_all_caroline_parameter_files_for_overview_kml()

    kml.open_folder("AoIs", "Extents of CAROLINEs AoIs")

    for param_file_AoI_name in list(sorted(param_file_data.keys())):
        if os.path.exists(
            f"{param_file_data[param_file_AoI_name]['general:shape-file:directory']}/"
            f"{param_file_data[param_file_AoI_name]['general:shape-file:aoi-name']}_shape.shp"
        ):  # first check if the AoI has been generated. If not, we cannot visualize it
            coordinate_dict = read_shp_extent(
                f"{param_file_data[param_file_AoI_name]['general:shape-file:directory']}/"
                f"{param_file_data[param_file_AoI_name]['general:shape-file:aoi-name']}_shape.shp",
                "AoI",
            )  # then read the AoI

            # Next, combine all info into the message that will be shown when clicking
            # General info
            message = f"Active: {param_file_data[param_file_AoI_name]['general:active']}\n\n"
            message += f"Tracks: {param_file_data[param_file_AoI_name]['general:tracks:track'].strip().strip(',')}\n\n"
            message += (
                f"Project owner: {param_file_data[param_file_AoI_name]['general:project:owner:name']} ("
                f"{param_file_data[param_file_AoI_name]['general:project:owner:email']})\n"
                f"Project engineer: {param_file_data[param_file_AoI_name]['general:project:engineer:name']} ("
                f"{param_file_data[param_file_AoI_name]['general:project:engineer:email']})\n"
                f"Objective: {param_file_data[param_file_AoI_name]['general:project:objective']}\n"
            )
            if param_file_data[param_file_AoI_name]["general:project:notes"] not in [None, ""]:
                message += f"Notes: {param_file_data[param_file_AoI_name]['general:project:notes']}\n\n"
            else:
                message += "\n"

            # Processing info per step
            message += "Processing steps done: \n"
            jobs = ""
            dependency = "\n"
            size_check_keys = []
            for job in JOB_DEFINITIONS["jobs"].keys():
                if job_schedule_check(
                    param_file_data[param_file_AoI_name]["full_parameter_file"], job, JOB_DEFINITIONS["jobs"]
                ):
                    jobs += f"{job}, "

                    if JOB_DEFINITIONS["jobs"][job]["bash-file"] is not None:
                        if JOB_DEFINITIONS["jobs"][job]["bash-file"]["bash-file-base-directory"] not in size_check_keys:
                            size_check_keys.append(
                                JOB_DEFINITIONS["jobs"][job]["bash-file"]["bash-file-base-directory"]
                            )

                    # check if the dependency also runs here, if not, we will specify it
                    if JOB_DEFINITIONS["jobs"][job]["requirement"] not in [None, "*"]:
                        if isinstance(JOB_DEFINITIONS["jobs"][job]["requirement"], str):
                            if not job_schedule_check(
                                param_file_data[param_file_AoI_name]["full_parameter_file"],
                                JOB_DEFINITIONS["jobs"][job]["requirement"],
                                JOB_DEFINITIONS["jobs"],
                            ):
                                dependency = (
                                    f'Previous step {JOB_DEFINITIONS["jobs"][job]["requirement"]} loaded from AoI '
                                    f'{param_file_data[param_file_AoI_name]["general:workflow:dependency:aoi-name"]}\n'
                                )
                        else:  # it's a list:
                            if not any(
                                [
                                    job_schedule_check(
                                        param_file_data[param_file_AoI_name]["full_parameter_file"],
                                        JOB_DEFINITIONS["jobs"][job]["requirement"][i],
                                        JOB_DEFINITIONS["jobs"],
                                    )
                                    for i in range(len(JOB_DEFINITIONS["jobs"][job]["requirement"]))
                                ]
                            ):
                                dependency = (
                                    f'Previous step {"/".join(JOB_DEFINITIONS["jobs"][job]["requirement"])} loaded '
                                    'from AoI '
                                    f'{param_file_data[param_file_AoI_name]["general:workflow:dependency:aoi-name"]}\n'
                                )

            if len(jobs) > 0:  # then we need to cut off the last ', '
                jobs = jobs[:-2]
            message += dependency
            message += f"{jobs}\n\n"

            # determine the data size and processing time
            if param_file_data[param_file_AoI_name]["general:tracks:track"] == "Unknown":
                data_size_fmt = "Unknown"
                processing_time_fmt = "Unknown"
            else:
                tracks = param_file_data[param_file_AoI_name]["general:tracks:track-list"]
                data_size = []
                for key in size_check_keys:
                    data_size.append(0)
                    locations = read_parameter_file(
                        param_file_data[param_file_AoI_name]["full_parameter_file"],
                        [f"{key}:general:directory", f"{key}:general:AoI-name"],
                    )
                    for track in tracks:
                        directories = glob.glob(
                            f"{locations[f'{key}:general:directory']}/"
                            f"{locations[f'{key}:general:AoI-name']}_*_[ad]sc_t{track:0>3d}*"
                        )
                        for directory in directories:
                            data_size[-1] += get_path_bytesize(directory)
                data_size_fmt = [
                    f"{size_check_keys[byte]}: {convert_bytesize_to_humanreadable(data_size[byte])}"
                    for byte in range(len(data_size))
                ]
                data_size_fmt = " / ".join(data_size_fmt)
                data_size_fmt += f" (total {convert_bytesize_to_humanreadable(sum(data_size))})"

                processing_time = 0

                for track in tracks:
                    track_processes = os.popen(
                        f"""grep "{param_file_AoI_name}_{track}" """
                        f"""{CONFIG_PARAMETERS['CAROLINE_WORK_DIRECTORY']}/submission-log.csv"""
                    ).read()
                    for line in track_processes.split("\n"):
                        if ";" in line:  # filter out empty lines
                            process_id = eval(line.split(";")[-1])
                            processing_time += get_processing_time(process_id)
                ndays = int(processing_time / (60 * 60 * 24))
                nhours = int(processing_time / (60 * 60)) % 24
                nminutes = int(processing_time / 60) % 60
                nseconds = processing_time % 60
                processing_time_fmt = (
                    f"{ndays} days, {nhours:0>2d}:{nminutes:0>2d}:{nseconds:0>2d} ({round(processing_time/3600, 2)} h)"
                )

            message += f"Storage size: {data_size_fmt}\n\n"
            message += f"Total used computation time (since 28 April 2025): {processing_time_fmt}\n"

            # determine the processing time

            # finally, add the polygon
            kml.add_polygon(coordinate_dict["0"], param_file_AoI_name, message, "AoI")

    kml.close_folder()
    return kml


def add_SLC_folder(kml: KML) -> KML:
    """Add the folder containing the extents of all SLCs available on Spider to the provided KML.

    Parameters
    ----------
    kml: caroline.kml.KML
        KML to which the SLC extents folder should be added

    Returns
    -------
    caroline.kml.KML
        KML with the SLC extents folder added

    Raises
    ------
    AssertionError
        when kml is not an instance of caroline.kml.KML
    """
    assert isinstance(kml, KML), f"provided kml is type {type(kml)}, not caroline.kml.KML!"

    kml.open_folder("SLCs", "Extents of all downloaded SLCs")

    SLC_folders = list(sorted(glob.glob(f"{CONFIG_PARAMETERS['SLC_BASE_DIRECTORY']}/s1*")))

    for SLC_folder in SLC_folders:
        size = convert_bytesize_to_humanreadable(get_path_bytesize(SLC_folder))

        name_pt1 = SLC_folder.split("/")[-1]  # this is e.g. s1_asc_t088

        # collect the dates
        dates = glob.glob(f"{SLC_folder}/IW_SLC__1SDV_VVVH/2*")
        dates = [date.split("/")[-1] for date in dates]

        if len(dates) > 0:
            # start a folder in the KML
            kml.open_folder(name_pt1, f"Storage size: {size}")

            # gather the statistics
            first_date = min(dates)
            last_date = max(dates)
            n_dates = len(dates)

            # gather the JSON files in the directory of the last date
            jsons = list(sorted(glob.glob(f"{SLC_folder}/IW_SLC__1SDV_VVVH/{last_date}/*.json")))
            if len(jsons) > 0:
                for n, json_file in enumerate(jsons):
                    coordinates = read_SLC_json(json_file)

                    kml.add_polygon(
                        coordinates,
                        f"{name_pt1}_img{n + 1}",
                        f'{first_date} - {last_date} ({n_dates} image{"" if n_dates == 1 else "s"})\n'
                        f'Total track storage size: {size}',
                        "SLC",
                    )
            else:
                # if the last folder does not contain jsons, the current download has not been activated.
                # We need to reverse in time to find a .xml or .json
                rev_dates = list(sorted(dates))[::-1]
                for date in rev_dates:
                    jsons = list(sorted(glob.glob(f"{SLC_folder}/IW_SLC__1SDV_VVVH/{date}/*.json")))
                    xmls = list(sorted(glob.glob(f"{SLC_folder}/IW_SLC__1SDV_VVVH/{date}/*.xml")))
                    if len(jsons) > 0 or len(xmls) > 0:
                        if len(jsons) > 0:  # we prefer a json
                            for n, json_file in enumerate(jsons):
                                coordinates = read_SLC_json(json_file)

                                kml.add_polygon(
                                    coordinates,
                                    f"{name_pt1}_img{n + 1}",
                                    f'{first_date} - {last_date} ({n_dates} image{"" if n_dates == 1 else "s"})\n'
                                    f'Total track storage size: {size}',
                                    "SLC",
                                )
                        elif len(xmls) > 0:  # in the past xmls were downloaded, so those are supported too
                            for n, xml_file in enumerate(xmls):
                                coordinates = read_SLC_xml(xml_file)

                                kml.add_polygon(
                                    coordinates,
                                    f"{name_pt1}_img{n + 1}",
                                    f'{first_date} - {last_date} ({n_dates} image{"" if n_dates == 1 else "s"})'
                                    f'Total track storage size: {size}',
                                    "SLC",
                                )
                        break  # to only add each track once, stop when one is found with jsons or xmls

            kml.close_folder()
    kml.close_folder()
    return kml


def add_coregistered_stack_folder(kml: KML) -> KML:
    """Add the folder containing the extents of all coregistered stacks available on Spider to the provided KML.

    Parameters
    ----------
    kml: caroline.kml.KML
        KML to which the coregistered stack extents folder should be added

    Returns
    -------
    caroline.kml.KML
        KML with the coregistered stack extents folder added

    Raises
    ------
    AssertionError
        when kml is not an instance of caroline.kml.KML
    """
    assert isinstance(kml, KML), f"provided kml is type {type(kml)}, not caroline.kml.KML!"

    # read the parameter file data
    param_file_data = read_all_caroline_parameter_files_for_overview_kml()

    kml.open_folder("Coregistered stacks", "Extents of all coregistered stacks")

    s1_stack_folders = []
    for param_file in param_file_data.keys():
        if "doris:general:directory" in param_file_data[param_file].keys():
            s1_stack_folders.append(param_file_data[param_file]["doris:general:directory"])
    s1_stack_folders = list(sorted(list(set(s1_stack_folders))))

    # filter out the Sentinel-1 stacks in all coregistration directories
    stack_folders = []
    for folder in s1_stack_folders:
        part_folders = list(sorted(glob.glob(f"{folder}/*_s1_[ad]sc_t*")))
        for f in part_folders:
            stack_folders.append(f)
    stack_folders = list(sorted(stack_folders))

    # Group them per track
    grouped_stack_folders = {}

    for stack_folder in stack_folders:
        track = "s1_" + stack_folder.split("_s1_")[-1]
        if track in grouped_stack_folders.keys():
            grouped_stack_folders[track].append(stack_folder)
        else:
            grouped_stack_folders[track] = [stack_folder]

    for track in list(sorted(list(grouped_stack_folders.keys()))):
        kml.open_folder(track)

        # for each track name, collect all the coregistered stack names and read the coverage shapefile
        AoI_names = [
            [stack_folder.split("/")[-1].split("_s1_")[0], stack_folder]
            for stack_folder in grouped_stack_folders[track]
        ]
        for AoI_name_zipped in list(sorted(AoI_names)):
            stack_folder = AoI_name_zipped[1]
            AoI_name = AoI_name_zipped[0]
            if os.path.exists(f"{stack_folder}/stackswath_coverage.shp"):
                size = convert_bytesize_to_humanreadable(get_path_bytesize(stack_folder))

                kml.open_folder(AoI_name, f"Storage size: {size}")

                coordinate_dict = read_shp_extent(f"{stack_folder}/stackswath_coverage.shp")

                # Collect the statistics
                dates = glob.glob(f"{stack_folder}/stack/2*")
                dates = [date.split("/")[-1] for date in dates]
                if len(dates) > 0:
                    first_date = min(dates)
                    last_date = max(dates)
                    n_dates = len(dates)
                else:
                    first_date = None
                    last_date = None
                    n_dates = 0

                message = f'{first_date} - {last_date} ({n_dates} image{"" if n_dates == 1 else "s"})\n'
                message += f"Storage size: {size}\n\n"
                message += f"Located in {stack_folder}\n\n"

                # Gather which caroline workflows this coregistered stack is part of
                check_coreg_directory = stack_folder.split("/" + AoI_name + "_s1_")[0]
                check_track = stack_folder.split(check_coreg_directory + "/" + AoI_name + "_")[1]
                workflows = []
                for param_file_AoI_name in list(sorted(param_file_data.keys())):
                    if "doris:general:directory" in param_file_data[param_file_AoI_name].keys():
                        if param_file_data[param_file_AoI_name]["doris:general:directory"] == check_coreg_directory:
                            if param_file_data[param_file_AoI_name]["doris:general:AoI-name"] == AoI_name:
                                if check_track in param_file_data[param_file_AoI_name]["general:tracks:track-list"]:
                                    workflows.append(param_file_AoI_name)
                    # if this AoI doesn't run it, check if its dependency does
                    elif (
                        param_file_data[param_file_AoI_name]["general:workflow:dependency:aoi-name"]
                        in param_file_data.keys()
                    ):
                        if (
                            "doris:general:directory"
                            in param_file_data[
                                param_file_data[param_file_AoI_name]["general:workflow:dependency:aoi-name"]
                            ].keys()
                        ):
                            if (
                                param_file_data[
                                    param_file_data[param_file_AoI_name]["general:workflow:dependency:aoi-name"]
                                ]["doris:general:AoI-name"]
                                == AoI_name
                            ):
                                if (
                                    check_track
                                    in param_file_data[
                                        param_file_data[param_file_AoI_name]["general:workflow:dependency:aoi-name"]
                                    ]["general:tracks:track-list"]
                                ):
                                    workflows.append(param_file_AoI_name)
                if len(workflows) > 0:
                    message += "Part of CAROLINE workflows " + ", ".join(workflows)
                else:
                    message += "Not part of any CAROLINE workflows"

                for name in list(sorted(list(coordinate_dict.keys()))):
                    kml.add_polygon(coordinate_dict[name], f"{AoI_name}_{track}_{name}", message, "stack")

                kml.close_folder()

        kml.close_folder()

    kml.close_folder()
    return kml


def read_all_caroline_parameter_files_for_overview_kml() -> dict:
    """Extract the relevant parameters from the CAROLINE parameter files for the generation of the overview KML.

    Only Sentinel-1 AoIs are considered for now.

    Returns
    -------
    dict
        Dictionary containing the relevant parameters for the KML generation
    """
    param_files = glob.glob(f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/parameter-files/param-file*")
    param_file_data = {}
    for param_file in param_files:
        parameter_file_data = generate_full_parameter_file(param_file, 0, "asc", "dummy.yaml", "dict")
        out = read_parameter_file(
            parameter_file_data,
            [
                "general:input-data:sensor",
                "doris:general:directory",
                "doris:general:AoI-name",
                "general:shape-file:directory",
                "general:shape-file:aoi-name",
                "general:project:owner:name",
                "general:project:owner:email",
                "general:project:engineer:name",
                "general:project:engineer:email",
                "general:project:objective",
                "general:project:notes",
                "general:workflow:dependency:aoi-name",
                "general:active",
            ],
            nonexistent_key_handling="Ignore",
        )

        out["full_parameter_file"] = parameter_file_data

        param_file_AoI_name = param_file.split("param-file-")[-1].split(".")[0].replace("-", "_")

        # retrieve the tracks
        track_list_file = (
            f"{CONFIG_PARAMETERS['CAROLINE_INSTALL_DIRECTORY']}/config/area-track-lists/{param_file_AoI_name}.dat"
        )
        if os.path.exists(track_list_file):
            f = open(track_list_file)
            data = f.read().split("\n")
            f.close()
            out["general:tracks:track"] = ", ".join(data[1:])

            out["general:tracks:track-list"] = [eval(d.split("_")[-1][1:].lstrip("0")) for d in data[1:]]
        elif os.path.exists(
            f"{CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/periodic/"
            f"{param_file_AoI_name}/geosearch.yaml"
        ):  # a download configuration exists, we can use it
            filtered_orbits, _ = identify_s1_orbits_in_aoi(
                f"{out['general:shape-file:directory']}/{out['general:shape-file:aoi-name']}_shape.shp"
            )
            allowed_orbits = eval(
                os.popen(
                    f"""grep "relative_orbits" {CONFIG_PARAMETERS['CAROLINE_DOWNLOAD_CONFIGURATION_DIRECTORY']}/"""
                    f"""periodic/{param_file_AoI_name}/geosearch.yaml"""
                )
                .read()
                .split(": ")[1]
            )

            tracks = []
            for track in list(sorted(list(filtered_orbits))):
                if eval(track.split("_")[-1][1:].lstrip("0")) in allowed_orbits:
                    tracks.append(track)
            out["general:tracks:track"] = ", ".join(tracks)
            out["general:tracks:track-list"] = tracks

        else:  # if we cannot find that either, leave it as unknown
            out["general:tracks:track"] = "Unknown"
            out["general:tracks:track-list"] = []
        param_file_data[param_file_AoI_name] = out
        param_file_data[param_file_AoI_name]["full_name"] = param_file
    return param_file_data
