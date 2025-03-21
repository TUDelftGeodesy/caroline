import os
from sys import argv, path

path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from read_param_file import read_param_file

filename, param_file, cpath, AoI_name, shape_AoI_name, version, caroline_dir = argv

search_parameters = ["crop_directory", "track", "asc_dsc", "shape_directory", "sensor"]
out_parameters = read_param_file(cpath, param_file, search_parameters)

base_stack = open(f"{caroline_dir}/caroline_v{version}/files/crop/crop.m")
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters["track"])
asc_dsc = eval(out_parameters["asc_dsc"])

for track in range(len(tracks)):
    main = stack.format(
        shape_dir=out_parameters["shape_directory"],
        caroline_dir=caroline_dir,
        shape_AoI_name=shape_AoI_name,
        version=version,
        sensor=out_parameters["sensor"],
    )

    fw = open(
        "{}/{}_{}_{}_t{:0>3d}/crop.m".format(
            out_parameters["crop_directory"], AoI_name, out_parameters["sensor"].lower(), asc_dsc[track], tracks[track]
        ),
        "w",
    )
    fw.write(main)
    fw.close()
