import os
from sys import argv, path

path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from read_param_file import read_param_file

filename, param_file, cpath, AoI_name, version, caroline_dir = argv

search_parameters = ["depsi_directory", "track", "asc_dsc", "sensor"]
out_parameters = read_param_file(cpath, param_file, search_parameters)

base_stack = open(f"{caroline_dir}/caroline_v{version}/files/depsi_post/depsi_post.sh")
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters["track"])
asc_dsc = eval(out_parameters["asc_dsc"])

for track in range(len(tracks)):
    main = stack.format(
        AoI_name=AoI_name,
        depsi_dir=out_parameters["depsi_directory"],
        asc_dsc=asc_dsc[track],
        track=f"{tracks[track]:0>3d}",
        sensor=out_parameters["sensor"].lower(),
        caroline_work=caroline_dir + "/work",
    )

    fw = open(
        "{}/{}_{}_{}_t{:0>3d}/psi/depsi_post.sh".format(
            out_parameters["depsi_directory"], AoI_name, out_parameters["sensor"].lower(), asc_dsc[track], tracks[track]
        ),
        "w",
    )
    fw.write(main)
    fw.close()
