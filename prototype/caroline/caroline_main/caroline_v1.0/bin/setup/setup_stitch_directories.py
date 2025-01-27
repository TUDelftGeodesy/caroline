from sys import argv, path
from os import mkdir
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name, doris_AoI_name = argv

search_parameters = ['coregistration_directory', 'track', 'asc_dsc', 'stitch_directory']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

for track in range(len(tracks)):	
    try:
        mkdir("{}/{}_s1_{}_t{:0>3d}".format(out_parameters['stitch_directory'], AoI_name, asc_dsc[track],
                                            tracks[track]))
    except OSError:
        pass  # Directory already exists
    f = open("{}/{}_s1_{}_t{:0>3d}/link_directory.txt".format(out_parameters['stitch_directory'], AoI_name,
                                                              asc_dsc[track], tracks[track]), "w")
    f.write("{}/{}_s1_{}_t{:0>3d}".format(out_parameters['coregistration_directory'], doris_AoI_name, asc_dsc[track], tracks[track]))
    f.close()
