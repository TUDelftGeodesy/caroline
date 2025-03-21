import os
from sys import argv, path

path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from read_param_file import read_param_file

filename, param_file, cpath, AoI_name, version, caroline_dir = argv

search_parameters = ["stitch_directory", "track", "asc_dsc"]
out_parameters = read_param_file(cpath, param_file, search_parameters)

base_stack = open(f"{caroline_dir}/caroline_v{version}/files/stack_stitching/MAIN.sh")
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters["track"])
asc_dsc = eval(out_parameters["asc_dsc"])

for track in range(len(tracks)):
    main = stack.format(
        AoI_name=AoI_name,
        stitch_dir=out_parameters["stitch_directory"],
        asc_dsc=asc_dsc[track],
        track=f"{tracks[track]:0>3d}",
        caroline_work=caroline_dir + "/work",
    )

    fw = open(
        "{}/{}_s1_{}_t{:0>3d}/MAIN.sh".format(
            out_parameters["stitch_directory"], AoI_name, asc_dsc[track], tracks[track]
        ),
        "w",
    )
    fw.write(main)
    fw.close()
