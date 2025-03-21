import os
from os import mkdir
from sys import argv, path

path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from read_param_file import read_param_file

filename, param_file, cpath, AoI_name, doris_AoI_name = argv

search_parameters = ["coregistration_directory", "track", "asc_dsc", "crop_directory", "sensor"]
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters["track"])
asc_dsc = eval(out_parameters["asc_dsc"])

for track in range(len(tracks)):
    try:
        mkdir(
            "{}/{}_{}_{}_t{:0>3d}".format(
                out_parameters["crop_directory"],
                AoI_name,
                out_parameters["sensor"].lower(),
                asc_dsc[track],
                tracks[track],
            )
        )
    except OSError:
        pass  # Directory already exists
    f = open(
        "{}/{}_{}_{}_t{:0>3d}/link_directory.txt".format(
            out_parameters["crop_directory"], AoI_name, out_parameters["sensor"].lower(), asc_dsc[track], tracks[track]
        ),
        "w",
    )
    f.write(
        "{}/{}_{}_{}_t{:0>3d}".format(
            out_parameters["coregistration_directory"],
            doris_AoI_name,
            out_parameters["sensor"].lower(),
            asc_dsc[track],
            tracks[track],
        )
    )
    f.close()
