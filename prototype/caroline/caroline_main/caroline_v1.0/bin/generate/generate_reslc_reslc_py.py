from sys import argv, path
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name, coregistration_AoI_name, version, caroline_dir = argv

search_parameters = ['reslc_directory', 'track', 'asc_dsc', 'sensor', 'coregistration_directory',
                     'shape_directory', 'shape_AoI_name']
out_parameters = read_param_file(cpath, param_file, search_parameters)

base_stack = open("{}/caroline_v{}/files/reslc/reslc.py".format(caroline_dir, version))
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])
stack_folder_name = 'stack' if out_parameters['sensor'].lower() == 's1' else 'process'
mother_slc_name = 'slave_rsmp_reramped.raw' if out_parameters['sensor'].lower() == 's1' else 'slave_rsmp.raw'

for track in range(len(tracks)):
    if out_parameters['sensor'].lower() == 's1':
        f = open(f"{out_parameters['coregistration_directory']}/{coregistration_AoI_name}_{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}/doris_input.xml", "r")
        data = f.read().split("\n")
        f.close()
        mother = None
        for line in data:
            if '<master_date>' in line:
                mother = line.split('>')[1].split('<')[0].replace("-", "")
                break

        if mother is None:
            raise ValueError(f"Failed to detect mother in {out_parameters['coregistration_directory']}/{coregistration_AoI_name}_{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}/doris_input.xml !")

    else:
        f = open(f"{out_parameters['coregistration_directory']}/{coregistration_AoI_name}_{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}/run_deinsar.py", "r")
        data = f.read().split("\n")
        f.close()
        mother = None
        for line in data:
            if 'master = ' in line:
                mother = line.split("'")[1]
                break

        if mother is None:
            raise ValueError(f"Failed to detect mother in {out_parameters['coregistration_directory']}/{coregistration_AoI_name}_{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}/run_deinsar.py !")

    main = stack.format(reslc_AoI_name=AoI_name, coregistration_directory=out_parameters['coregistration_directory'],
                        asc_dsc=asc_dsc[track], coregistration_AoI_name=coregistration_AoI_name,
                        track="{:0>3d}".format(tracks[track]), sensor=out_parameters['sensor'].lower(),
                        mother=mother, lb="{", rb="}", shape_directory=out_parameters['shape_directory'],
                        shape_AoI_name=out_parameters["shape_AoI_name"], stack_folder_name=stack_folder_name,
                        mother_slc_name=mother_slc_name)

    fw = open("{}/{}_{}_{}_t{:0>3d}/reslc_{}_{}_{}_t{:0>3d}.py".format(out_parameters['reslc_directory'], AoI_name,
                                                                       out_parameters['sensor'].lower(), asc_dsc[track],
                                                                       tracks[track], AoI_name,
                                                                       out_parameters['sensor'].lower(), asc_dsc[track],
                                                                       tracks[track]), 'w')
    fw.write(main)
    fw.close()



