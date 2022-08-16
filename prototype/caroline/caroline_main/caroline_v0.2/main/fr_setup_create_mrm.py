from sys import argv
filename, param_file, cpath, AoI_name = argv
from os import mkdir

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['stitch_directory', 'track','asc_dsc', 'depsi_directory']
out_parameters = []

for param in search_parameters:
    for p in parameters:
        if param in p.split("=")[0]:
            do = p.split("=")[1]
            if "#" in do:
                do = do.split("#")[0]
            do = do.strip().strip("'").strip('"')
            out_parameters.append(do)
            break

tracks = eval(out_parameters[1])
asc_dsc = eval(out_parameters[2])

for track in range(len(tracks)):	
    fr = open("{stitch_dir}/{AoI_name}_s1_{asc_dsc}_t{fill_track}/{AoI_name}_cropped_stack/nlines_crp.txt".format(stitch_dir=out_parameters[0], AoI_name=AoI_name, asc_dsc=asc_dsc[track],fill_track="{:0>3d}".format(tracks[track])))
    data = fr.read().split("\n")
    fr.close()

    f = open("{}/{}_s1_{}_t{:0>3d}/psi/nlines_crop.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]),"w")
    f.write("{}".format(data[0]))
    f.close()

    f = open("{}/{}_s1_{}_t{:0>3d}/psi/project_id.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]),"w")
    f.write("{}_s1_{}_t{:0>3d}".format(AoI_name, asc_dsc[track], tracks[track]))
    f.close()
