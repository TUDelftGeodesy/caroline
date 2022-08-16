from sys import argv
filename, param_file, cpath, AoI_name = argv
from os import mkdir
import os
import glob

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['stitch_directory', 'track','asc_dsc', 'depsi_directory']
out_parameters = []

for param in search_parameters:
    for p in parameters:
        if param in p.split("=")[0]:
            do = p.split("=")[1]
            if "#" in do:
                do = do.split("#")[0]
            do = do.strip().strip("'").strip('"')
            out_parameters.append(do)
            break

tracks = eval(out_parameters[1])
asc_dsc = eval(out_parameters[2])

for track in range(len(tracks)):
    try:
        mkdir("{}/{}_s1_{}_t{:0>3d}".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
    except OSError:
        pass  # Directory already exists
    try:
        mkdir("{}/{}_s1_{}_t{:0>3d}/psi".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
    except OSError:
        pass  # Directory already exists
    try:
        mkdir("{}/{}_s1_{}_t{:0>3d}/boxes".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
    except OSError:
        pass  # Directory already exists
    basedir = "{}/{}_s1_{}_t{:0>3d}/{}_cropped_stack/".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track], AoI_name)
    files = glob.glob("{}*".format(basedir))
    dirs = [f for f in files if os.path.isdir(f)]
    masterdir = ""
    for dir in dirs:
        files = glob.glob("{}/*".format(dir))
        files = [f.split("/")[-1] for f in files]
        master = [f for f in files if f == "master.res"]
        if len(master) == 1:
            masterdir = dir
            break
    f = open("{}/{}_s1_{}_t{:0>3d}/psi/master_directory.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]),"w")
    f.write("{}".format(masterdir))
    f.close()
