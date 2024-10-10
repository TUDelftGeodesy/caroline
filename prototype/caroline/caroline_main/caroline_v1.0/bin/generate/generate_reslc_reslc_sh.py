from sys import argv, path
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name, version, caroline_dir = argv

search_parameters = ['reslc_directory', 'track', 'asc_dsc', 'sensor', 'reslc_code_dir']
out_parameters = read_param_file(cpath, param_file, search_parameters)

base_stack = open("{}/caroline_v{}/files/reslc/reslc.sh".format(caroline_dir, version))
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

for track in range(len(tracks)):
    main = stack.format(AoI_name=AoI_name, pydepsi_code_dir=out_parameters['reslc_code_dir'], asc_dsc=asc_dsc[track],
                        track="{:0>3d}".format(tracks[track]), sensor=out_parameters['sensor'].lower())

    fw = open("{}/{}_{}_{}_t{:0>3d}/reslc.sh".format(out_parameters['reslc_directory'], AoI_name,
                                                     out_parameters['sensor'].lower(), asc_dsc[track],
                                                     tracks[track]), 'w')
    fw.write(main)
    fw.close()



