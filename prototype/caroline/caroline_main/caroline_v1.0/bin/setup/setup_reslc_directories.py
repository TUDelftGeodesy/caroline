from sys import argv, path
from os import mkdir
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name = argv

search_parameters = ['coregistration_directory', 'track', 'asc_dsc', 'reslc_directory', 'sensor']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

for track in range(len(tracks)):	
    try:
        mkdir("{}/{}_{}_{}_t{:0>3d}".format(out_parameters['reslc_directory'], AoI_name,
                                            out_parameters['sensor'].lower(), asc_dsc[track],
                                            tracks[track]))
    except OSError:
        pass  # Directory already exists

