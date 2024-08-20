from sys import argv, path
from os import mkdir
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name = argv


fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['doris_directory', 'track', 'asc_dsc']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

for track in range(len(tracks)):
    try:
        mkdir("{}/{}_s1_{}_t{:0>3d}".format(out_parameters['doris_directory'], AoI_name, asc_dsc[track], tracks[track]))
    except OSError:
        pass  # Directory already exists

    try:
        mkdir("{}/{}_s1_{}_t{:0>3d}/good_images".format(out_parameters['doris_directory'], AoI_name, asc_dsc[track],
                                                        tracks[track]))
    except OSError:
        pass  # Directory already exists
    f = open("{}/{}_s1_{}_t{:0>3d}/good_images/link_directory.txt".format(out_parameters['doris_directory'], AoI_name,
                                                                          asc_dsc[track], tracks[track]), "w")
    f.write("/project/caroline/Data/radar_data/sentinel1/s1_{}_t{:0>3d}/IW_SLC__1SDV_VVVH/".format(asc_dsc[track],
                                                                                                   tracks[track]))
    f.close()

    try:
        mkdir("{}/{}_s1_{}_t{:0>3d}/bad_images".format(out_parameters['doris_directory'], AoI_name, asc_dsc[track],
                                                       tracks[track]))
    except OSError:
        pass  # Directory already exists


