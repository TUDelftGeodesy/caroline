from sys import argv, path
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name = argv

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['stitch_directory', 'track', 'asc_dsc', 'depsi_directory', 'coregistration_directory',
                     'sensor', 'coregistration_AoI_name', 'stitch_AoI_name']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

for track in range(len(tracks)):
    if out_parameters['sensor'] == 'S1':
        fr = open("{stitch_dir}/{AoI_name}_s1_{asc_dsc}_t{fill_track}/cropped_stack/nlines_crp.txt".format(
            stitch_dir=out_parameters['stitch_directory'], AoI_name=out_parameters['stitch_AoI_name'],
            asc_dsc=asc_dsc[track], fill_track="{:0>3d}".format(tracks[track])))
        data = fr.read().split("\n")
        num = data[0]
        fr.close()
    else:
        fr = open('{coregistration_dir}/{AoI_name}_{sensor}_{asc_dsc}_t{fill_track}/process/input.crop'.format(
            coregistration_dir=out_parameters['coregistration_directory'],
            AoI_name=out_parameters['coregistration_AoI_name'],
            sensor=out_parameters['sensor'].lower(), asc_dsc=asc_dsc[track], fill_track="{:0>3d}".format(tracks[track])))
        data = fr.read().split("\n")
        fr.close()
        num = 0
        for i in data:
            if "S_DBOW_GEO" in i and i[:2] != 'c ':
                num = i.split('//')[0].strip().split(' ')[-1]  # TODO: -2 = vertical, -1 = horizontal, which one is it?
                break

    f = open("{}/{}_{}_{}_t{:0>3d}/psi/nlines_crop.txt".format(out_parameters['depsi_directory'], AoI_name,
                                                               out_parameters['sensor'].lower(),
                                                               asc_dsc[track], tracks[track]), "w")
    f.write("{}".format(num))
    f.close()

    f = open("{}/{}_{}_{}_t{:0>3d}/psi/project_id.txt".format(out_parameters['depsi_directory'], AoI_name,
                                                              out_parameters['sensor'].lower(),
                                                              asc_dsc[track], tracks[track]),"w")
    f.write("{}_{}_{}_t{:0>3d}".format(AoI_name, out_parameters['sensor'].lower(), asc_dsc[track], tracks[track]))
    f.close()
