from sys import argv, path
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, auxiliary_files = argv

search_parameters = ['do_coregistration', 'do_stack_stitching', 'do_depsi', 'do_depsi_post',  'coregistration_directory',
                     'stitch_directory', 'depsi_directory', 'shape_directory', 'coregistration_AoI_name',
                     'stitch_AoI_name', 'depsi_AoI_name', 'shape_AoI_name', 'Caroline_version',
                     'dem_file', 'depsi_code_dir', 'rdnaptrans_dir', 'geocoding_dir', 'depsi_post_dir',
                     'cpxfiddle_dir', 'depsi_post_mode', 'asc_dsc', 'track', 'sensor', 'do_reslc', 'reslc_AoI_name',
                     'reslc_directory', 'skygeo_viewer']
out_parameters = read_param_file(cpath, param_file, search_parameters)

for param in out_parameters.keys():

    if param == 'depsi_post_mode':
        f = open(f'{cpath}/{auxiliary_files}/{param}.txt', 'w')
        if out_parameters[param] == 'csv':
            f.write('0')
        elif out_parameters[param] == 'tarball':
            f.write('1')
        else:
            raise ValueError("Unknown depsi post mode {}, known are 'csv' and 'tarball'".format(out_parameters[param]))
    elif param == 'dem_file':
        f = open(f'{cpath}/{auxiliary_files}/dem_directory.txt', 'w')
        # cut off the dem file name
        delta = len(out_parameters[param].split('/')[-1]) + 1
        f.write(out_parameters[param][:-delta])
    elif param == 'do_coregistration':
        # need to split between doris and deinsar
        if out_parameters['sensor'] == 'S1':
            nparam = param.replace('coregistration', 'doris')
            f = open(f'{cpath}/{auxiliary_files}/do_deinsar.txt', "w")
            f.write('0')
            f.close()
        else:
            nparam = param.replace('coregistration', 'deinsar')
            f = open(f'{cpath}/{auxiliary_files}/do_doris.txt', "w")
            f.write('0')
            f.close()
        f = open(f'{cpath}/{auxiliary_files}/{nparam}.txt', 'w')
        f.write(out_parameters[param])
    elif param in ['coregistration_AoI_name', 'coregistration_directory']:
        f = open(f'{cpath}/{auxiliary_files}/{param.replace("coregistration", "doris")}.txt', "w")
        f.write(out_parameters[param])
        f.close()
        f = open(f'{cpath}/{auxiliary_files}/{param.replace("coregistration", "deinsar")}.txt', "w")
        f.write(out_parameters[param])
    elif param == 'do_stack_stitching' and out_parameters['sensor'] != 'S1':
        if out_parameters[param] == '1':
            print(f'WARNING: do_stack_stitching (S1 only) is turned on while sensor is {out_parameters["sensor"]}, ignoring...')
        f = open(f'{cpath}/{auxiliary_files}/{param}.txt', 'w')
        f.write('0')
    elif param == 'do_reslc' and out_parameters['sensor'] != 'S1':
        if out_parameters[param] == '1':
            print(f'WARNING: do_reslc (S1 only) is turned on while sensor is {out_parameters["sensor"]}, ignoring...')
        f = open(f'{cpath}/{auxiliary_files}/{param}.txt', 'w')
        f.write('0')
    else:
        f = open(f'{cpath}/{auxiliary_files}/{param}.txt', 'w')
        f.write(out_parameters[param])
    f.close()

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])
for prefix in ['doris', 'deinsar', 'stitch', 'depsi', 'reslc']:
    if prefix in ['doris', 'deinsar']:
        AoI_name = out_parameters['coregistration_AoI_name']
    else:
        AoI_name = out_parameters[prefix + '_AoI_name']

    f = open("{}/{}/loop_directories_{}.txt".format(cpath, auxiliary_files, prefix), "w")
    for track in range(len(tracks)):
        f.write("{}_{}_{}_t{:0>3d}\n".format(AoI_name, out_parameters['sensor'].lower(), asc_dsc[track], tracks[track]))
    f.close()
