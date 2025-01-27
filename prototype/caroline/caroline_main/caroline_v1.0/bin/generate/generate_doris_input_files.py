from sys import argv, path
import os
import glob
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name, version, caroline_dir = argv

search_parameters = ['coregistration_directory', 'track', 'asc_dsc', 'dem_file', 'dem_format', 'dem_size', 'dem_upperleft',
                     'dem_nodata', 'dem_delta']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])
dem_delta = eval(out_parameters['dem_delta'])
dem_size = eval(out_parameters['dem_size'])
dem_upperleft = eval(out_parameters['dem_upperleft'])


for file in ['input.comprefdem', 'input.dembased']:
    base_stack = open("{}/caroline_v{}/files/doris_v5/input_files/{}".format(caroline_dir, version, file))
    stack = base_stack.read()
    base_stack.close()

    for track in range(len(tracks)):
        doris_stack = stack.format(dem_file=out_parameters['dem_file'],
                                   dem_format=out_parameters['dem_format'],
                                   dem_s1=dem_size[0],
                                   dem_s2=dem_size[1],
                                   dem_d1=dem_delta[0],
                                   dem_d2=dem_delta[1],
                                   dem_ul1=dem_upperleft[0],
                                   dem_ul2=dem_upperleft[1],
                                   dem_nodata=out_parameters['dem_nodata'])

        fw = open("{}/{}_s1_{}_t{:0>3d}/input_files/{}".format(out_parameters['coregistration_directory'], AoI_name,
                                                               asc_dsc[track], tracks[track], file), 'w')
        fw.write(doris_stack)
        fw.close()
