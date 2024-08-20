from sys import argv, path
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name = argv

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['stitch_directory', 'track', 'asc_dsc', 'depsi_directory']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

for track in range(len(tracks)):	
    fr = open("{stitch_dir}/{AoI_name}_s1_{asc_dsc}_t{fill_track}/cropped_stack/nlines_crp.txt".format(
        stitch_dir=out_parameters['stitch_directory'], AoI_name=AoI_name, asc_dsc=asc_dsc[track],
        fill_track="{:0>3d}".format(tracks[track])))
    data = fr.read().split("\n")
    fr.close()

    f = open("{}/{}_s1_{}_t{:0>3d}/psi/nlines_crop.txt".format(out_parameters['depsi_directory'], AoI_name,
                                                               asc_dsc[track], tracks[track]), "w")
    f.write("{}".format(data[0]))
    f.close()

    f = open("{}/{}_s1_{}_t{:0>3d}/psi/project_id.txt".format(out_parameters['depsi_directory'], AoI_name,
                                                              asc_dsc[track], tracks[track]),"w")
    f.write("{}_s1_{}_t{:0>3d}".format(AoI_name, asc_dsc[track], tracks[track]))
    f.close()
