import os
from sys import argv, path

path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from read_param_file import read_param_file

filename, param_file, cpath, AoI_name, version, caroline_dir = argv


search_parameters = ["coregistration_directory", "track", "asc_dsc", "doris_code_directory"]
out_parameters = read_param_file(cpath, param_file, search_parameters)

base_stack = open(f"{caroline_dir}/caroline_v{version}/files/doris_v5/doris_stack.sh")
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters["track"])
asc_dsc = eval(out_parameters["asc_dsc"])

for track in range(len(tracks)):
    doris_stack = stack.format(
        doris_path="{}/{}_s1_{}_t{:0>3d}".format(
            out_parameters["coregistration_directory"], AoI_name, asc_dsc[track], tracks[track]
        ),
        doris_code_path=out_parameters["doris_code_directory"],
        track=tracks[track],
        caroline_work=caroline_dir + "/work",
        area=AoI_name,
    )

    fw = open(
        "{}/{}_s1_{}_t{:0>3d}/doris_stack.sh".format(
            out_parameters["coregistration_directory"], AoI_name, asc_dsc[track], tracks[track]
        ),
        "w",
    )
    fw.write(doris_stack)
    fw.close()
