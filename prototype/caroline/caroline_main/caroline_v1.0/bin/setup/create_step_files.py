from sys import argv, path
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, auxiliary_files = argv

search_parameters = ['do_doris', 'do_stack_stitching', 'do_depsi', 'do_depsi_post',  'doris_directory',
                     'stitch_directory', 'depsi_directory', 'shape_directory', 'doris_AoI_name',
                     'stitch_AoI_name', 'depsi_AoI_name', 'shape_AoI_name', 'Caroline_version',
                     'dem_directory', 'depsi_code_dir', 'rdnaptrans_dir', 'geocoding_dir', 'depsi_post_dir',
                     'cpxfiddle_dir', 'depsi_post_mode', 'asc_dsc', 'track']
out_parameters = read_param_file(cpath, param_file, search_parameters)

for param in out_parameters.keys():
    f = open(f'{cpath}/{auxiliary_files}/{param}.txt', 'w')
    if param == 'depsi_post_mode':
        if out_parameters[param] == 'csv':
            f.write('0')
        elif out_parameters[param] == 'tarball':
            f.write('1')
        else:
            raise ValueError("Unknown depsi post mode {}, known are 'csv' and 'tarball'".format(out_parameters[param]))
    else:
        f.write(out_parameters[param])
    f.close()

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])
for prefix in ['doris', 'stitch', 'depsi']:
    AoI_name = out_parameters[prefix + '_AoI_name']

    f = open("{}/{}/loop_directories_{}.txt".format(cpath, auxiliary_files, prefix), "w")
    for track in range(len(tracks)):
        f.write("{}_s1_{}_t{:0>3d}\n".format(AoI_name, asc_dsc[track], tracks[track]))
    f.close()
