from sys import argv, path
from os import mkdir
import os
import glob
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name, stitch_AoI_name = argv

search_parameters = ['crop_directory', 'track', 'asc_dsc', 'depsi_directory', 'sensor',
                     'coregistration_directory', 'coregistration_AoI_name']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

for track in range(len(tracks)):
    try:
        mkdir("{}/{}_{}_{}_t{:0>3d}".format(out_parameters['depsi_directory'], AoI_name,
                                            out_parameters['sensor'].lower(), asc_dsc[track], tracks[track]))
    except OSError:
        pass  # Directory already exists
    try:
        mkdir("{}/{}_{}_{}_t{:0>3d}/psi".format(out_parameters['depsi_directory'], AoI_name,
                                                out_parameters['sensor'].lower(), asc_dsc[track], tracks[track]))
    except OSError:
        pass  # Directory already exists
    try:
        mkdir("{}/{}_{}_{}_t{:0>3d}/boxes".format(out_parameters['depsi_directory'], AoI_name,
                                                  out_parameters['sensor'].lower(), asc_dsc[track], tracks[track]))
    except OSError:
        pass  # Directory already exists

    if out_parameters['sensor'] == 'S1':
        basedir = "{}/{}_s1_{}_t{:0>3d}/*cropped_stack/".format(out_parameters['crop_directory'], stitch_AoI_name,
                                                                asc_dsc[track], tracks[track])
        files = glob.glob("{}*".format(basedir))
        dirs = [f for f in files if os.path.isdir(f)]
        masterdir = ""
        for dr in dirs:
            files = glob.glob("{}/*".format(dr))
            files = [f.split("/")[-1] for f in files]
            master = [f for f in files if f == "master.res"]
            if len(master) == 1:
                masterdir = dr
                break

        f = open("{}/{}_{}_{}_t{:0>3d}/psi/mother_res.txt".format(out_parameters['depsi_directory'], AoI_name,
                                                                    out_parameters['sensor'].lower(),
                                                                    asc_dsc[track], tracks[track]), "w")
        f.write("{}/master.res".format(masterdir))
        f.close()
        f = open("{}/{}_{}_{}_t{:0>3d}/psi/mother_dem.txt".format(out_parameters['depsi_directory'], AoI_name,
                                                                    out_parameters['sensor'].lower(),
                                                                    asc_dsc[track], tracks[track]), "w")
        f.write("{}/dem_radar.raw".format(masterdir))
        f.close()

    else:
        basedir = '{}/{}_{}_{}_t{:0>3d}'.format(out_parameters['coregistration_directory'],
                                                         out_parameters['coregistration_AoI_name'],
                                                         out_parameters['sensor'].lower(), asc_dsc[track],
                                                         tracks[track])
        f = open(f'{basedir}/run_deinsar.py')
        data = f.read().split('\n')
        f.close()
        master_line = None
        for i in data:
            if "master = '" in i:
                master_line = i
                break
        masterdir = f'''{basedir}/process/{master_line.strip().strip("'").split("'")[-1]}'''

        f = open("{}/{}_{}_{}_t{:0>3d}/psi/mother_res.txt".format(out_parameters['depsi_directory'], AoI_name,
                                                                    out_parameters['sensor'].lower(),
                                                                    asc_dsc[track], tracks[track]), "w")
        f.write("{}/slave.res".format(masterdir))
        f.close()
        f = open("{}/{}_{}_{}_t{:0>3d}/psi/mother_dem.txt".format(out_parameters['depsi_directory'], AoI_name,
                                                                    out_parameters['sensor'].lower(),
                                                                    asc_dsc[track], tracks[track]), "w")
        f.write("{}/dem_radar.raw".format(masterdir))
        f.close()
