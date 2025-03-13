import glob
import os
from typing import Literal

from caroline.io import read_parameter_file, read_shp_extent, read_SLC_json, read_SLC_xml

SLC_BASE_FOLDER = "/project/caroline/Data/radar_data/sentinel1"
CAROLINE_PARAM_DIR = "/project/caroline/Software/caroline-prototype/caroline_v1.0/run_files"


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
            f"{param_file_data[param_file_AoI_name]['shape_directory']}/"
            f"{param_file_data[param_file_AoI_name]['shape_AoI_name']}_shape.shp"
        ):  # first check if the AoI has been generated. If not, we cannot visualize it
            coordinate_dict = read_shp_extent(
                f"{param_file_data[param_file_AoI_name]['shape_directory']}/"
                f"{param_file_data[param_file_AoI_name]['shape_AoI_name']}_shape.shp",
                "AoI",
            )  # then read the AoI

            # Next, combine all info into the message that will be shown when clicking
            # General info
            message = f"Tracks: {param_file_data[param_file_AoI_name]['tracks'].strip().strip(',')}\n\n"
            message += (
                f"Project owner: {param_file_data[param_file_AoI_name]['project_owner']} ("
                f"{param_file_data[param_file_AoI_name]['project_owner_email']})\n"
                f"Project engineer: {param_file_data[param_file_AoI_name]['project_engineer']} ("
                f"{param_file_data[param_file_AoI_name]['project_engineer_email']})\n"
                f"Objective: {param_file_data[param_file_AoI_name]['project_objective']}\n"
            )
            if param_file_data[param_file_AoI_name]["project_notes"] != "":
                message += f"Notes: {param_file_data[param_file_AoI_name]['project_notes']}\n\n"
            else:
                message += "\n"

            # Processing info per step
            message += "Processing steps done: \n"
            for step in ["coregistration", "crop", "reslc", "depsi", "depsi_post"]:
                if param_file_data[param_file_AoI_name][f"do_{step}"] == "1":
                    if step == "depsi_post":  # also add the portal link if depsi_post ran
                        message += (
                            f"{step}: done in {param_file_data[param_file_AoI_name]['depsi_directory']}\n"
                            f"(AoI {param_file_data[param_file_AoI_name]['depsi_AoI_name']})\n"
                        )
                        message += (
                            f"Portal: https://caroline.portal-tud.skygeo.com/portal/"
                            f"{param_file_data[param_file_AoI_name]['skygeo_customer']}/"
                            f"{param_file_data[param_file_AoI_name]['skygeo_viewer']}/viewers/basic/"
                        )
                    else:
                        message += (
                            f"{step}: done in {param_file_data[param_file_AoI_name][f'{step}_directory']} "
                            f"(AoI {param_file_data[param_file_AoI_name][f'{step}_AoI_name']})\n"
                        )
                else:  # if the step did not run but further steps did, add info on where it was loaded from
                    if step == "coregistration" and any(
                        [param_file_data[param_file_AoI_name][f"do_{step_}"] == "1" for step_ in ["crop", "reslc"]]
                    ):
                        message += (
                            f"{step}: loaded from {param_file_data[param_file_AoI_name][f'{step}_directory']} "
                            f"(AoI {param_file_data[param_file_AoI_name]['coregistration_AoI_name']})\n"
                        )
                    elif step == "crop" and param_file_data[param_file_AoI_name]["do_depsi"] == "1":
                        message += (
                            f"{step}: loaded from {param_file_data[param_file_AoI_name][f'{step}_directory']} "
                            f"(AoI {param_file_data[param_file_AoI_name]['crop_AoI_name']})\n"
                        )
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

    SLC_folders = list(sorted(glob.glob(f"{SLC_BASE_FOLDER}/s1*")))

    for SLC_folder in SLC_folders:
        name_pt1 = SLC_folder.split("/")[-1]  # this is e.g. s1_asc_t088

        # collect the dates
        dates = glob.glob(f"{SLC_folder}/IW_SLC__1SDV_VVVH/2*")
        dates = [date.split("/")[-1] for date in dates]

        if len(dates) > 0:
            # start a folder in the KML
            kml.open_folder(name_pt1)

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
                        f'{first_date} - {last_date} ({n_dates} image{"" if n_dates == 1 else "s"})',
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
                                    f'{first_date} - {last_date} ({n_dates} image{"" if n_dates == 1 else "s"})',
                                    "SLC",
                                )
                        elif len(xmls) > 0:  # in the past xmls were downloaded, so those are supported too
                            for n, xml_file in enumerate(xmls):
                                coordinates = read_SLC_xml(xml_file)

                                kml.add_polygon(
                                    coordinates,
                                    f"{name_pt1}_img{n + 1}",
                                    f'{first_date} - {last_date} ({n_dates} image{"" if n_dates == 1 else "s"})',
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

    s1_stack_folders = list(
        sorted(list(set([param_file_data[i]["coregistration_directory"] for i in param_file_data.keys()])))
    )

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
                kml.open_folder(AoI_name)

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
                message += f"Located in {stack_folder}\n"

                # Gather which caroline workflows this coregistered stack is part of
                check_coreg_directory = stack_folder.split("/" + AoI_name + "_s1_")[0]
                check_track = stack_folder.split(check_coreg_directory + "/" + AoI_name + "_")[1]
                workflows = []
                for param_file_AoI_name in list(sorted(param_file_data.keys())):
                    if param_file_data[param_file_AoI_name]["coregistration_directory"] == check_coreg_directory:
                        if param_file_data[param_file_AoI_name]["coregistration_AoI_name"] == AoI_name:
                            if check_track in param_file_data[param_file_AoI_name]["tracks"]:
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
    param_files = glob.glob(f"{CAROLINE_PARAM_DIR}/param_file_Caroline_v*_spider_*")
    param_file_data = {}
    for param_file in param_files:
        out = read_parameter_file(
            param_file,
            [
                "sensor",
                "coregistration_directory",
                "coregistration_AoI_name",
                "do_coregistration",
                "do_crop",
                "do_reslc",
                "do_depsi",
                "do_depsi_post",
                "skygeo_customer",
                "skygeo_viewer",
                "crop_directory",
                "reslc_directory",
                "depsi_directory",
                "shape_directory",
                "shape_AoI_name",
                "project_owner",
                "project_owner_email",
                "project_engineer",
                "project_engineer_email",
                "project_objective",
                "project_notes",
                "crop_AoI_name",
                "depsi_AoI_name",
                "reslc_AoI_name",
            ],
        )

        if out["sensor"] == "S1":  # for now, we only consider Sentinel-1
            param_file_AoI_name = param_file.split("_spider_")[-1].split(".")[0]

            # retrieve the tracks
            track_list_file = f"{CAROLINE_PARAM_DIR}/../../area-track-lists/{param_file_AoI_name}.dat"
            if os.path.exists(track_list_file):
                f = open(track_list_file)
                data = f.read().split("\n")
                f.close()
                out["tracks"] = ", ".join(data[1:])
            elif param_file_AoI_name == "TEST_nl_amsterdam":  # this test AoI does not have a parameter file
                out["tracks"] = "s1_dsc_t037"
            else:  # if it has not yet been found, it might be inactive, which we need to check for
                track_list_file = f"{CAROLINE_PARAM_DIR}/../../area-track-lists/INACTIVE_{param_file_AoI_name}.dat"
                if os.path.exists(track_list_file):
                    f = open(track_list_file)
                    data = f.read().split("\n")
                    f.close()
                    out["tracks"] = ", ".join(data[1:])
                else:  # if we cannot find that either, leave it as unknown
                    out["tracks"] = "Unknown"
            param_file_data[param_file_AoI_name] = out
    return param_file_data
