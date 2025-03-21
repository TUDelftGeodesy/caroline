import os
from sys import argv, path

path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from read_param_file import read_param_file

filename, param_file, cpath, AoI_name, shape_AoI_name, version, caroline_dir = argv

search_parameters = ["stitch_directory", "track", "asc_dsc", "shape_directory"]
out_parameters = read_param_file(cpath, param_file, search_parameters)

base_stack = open(f"{caroline_dir}/caroline_v{version}/files/stack_stitching/MAIN.m")
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters["track"])
asc_dsc = eval(out_parameters["asc_dsc"])

for track in range(len(tracks)):
    main = stack.format(
        stitch_AoI_name=AoI_name,
        shape_dir=out_parameters["shape_directory"],
        caroline_dir=caroline_dir,
        shape_AoI_name=shape_AoI_name,
        version=version,
    )

    fw = open(
        "{}/{}_s1_{}_t{:0>3d}/MAIN.m".format(
            out_parameters["stitch_directory"], AoI_name, asc_dsc[track], tracks[track]
        ),
        "w",
    )
    fw.write(main)
    fw.close()
