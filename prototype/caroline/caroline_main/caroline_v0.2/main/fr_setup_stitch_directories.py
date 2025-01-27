from sys import argv
filename, param_file, cpath, AoI_name = argv
from os import mkdir

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['doris_directory', 'track','asc_dsc', 'stitch_directory']
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
    f = open("{}/{}_s1_{}_t{:0>3d}/link_directory.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]),"w")
    f.write("{}/{}_s1_{}_t{:0>3d}".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track]))
    f.close()
