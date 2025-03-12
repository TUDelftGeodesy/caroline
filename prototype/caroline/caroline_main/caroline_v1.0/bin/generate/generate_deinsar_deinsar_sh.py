import os
from sys import argv, path

path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from read_param_file import read_param_file

filename, param_file, cpath, version, caroline_dir = argv

search_parameters = [
    "sensor",
    "coregistration_directory",
    "deinsar_code_directory",
    "coregistration_AoI_name",
    "track",
    "asc_dsc",
    "di_data_directories",
    "doris_v4_code_directory",
]
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters["track"])
asc_dsc = eval(out_parameters["asc_dsc"])
datadirs = eval(out_parameters["di_data_directories"])

fr = open(f"{caroline_dir}/caroline_v{version}/files/deinsar/run_deinsar.sh")
base_data = fr.read()
fr.close()

for track in range(len(tracks)):
    basedir = "{}/{}_{}_{}_t{:0>3d}".format(
        out_parameters["coregistration_directory"],
        out_parameters["coregistration_AoI_name"],
        out_parameters["sensor"].lower(),
        asc_dsc[track],
        tracks[track],
    )

    data = base_data.format(
        coregistration_dir=basedir,
        deinsar_dir=out_parameters["deinsar_code_directory"],
        doris_v4_dir=out_parameters["doris_v4_code_directory"],
        track=tracks[track],
        caroline_work=caroline_dir + "/work",
        area=out_parameters["coregistration_AoI_name"],
    )

    fw = open(f"{basedir}/run_deinsar.sh", "w")
    fw.write(data)
    fw.close()
