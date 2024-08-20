from sys import argv
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name = argv

search_parameters = ['doris_directory', 'track', 'asc_dsc']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

for track in range(len(tracks)):
    f = open("{}/{}_s1_{}_t{:0>3d}/good_images/zip_files.txt".format(out_parameters['doris_directory'], AoI_name,
                                                                     asc_dsc[track], tracks[track]))
    data = f.read().split("\n")
    f.close()

    bad_zips = []
    for line in data:
        if line == "":
            continue
        d_ = line.split(" ")
        d = []
        for i in d_:
            if i != "":
                d.append(i)
        dirr = d[-1]
        size = d[-5]
        if eval(size) < 3000000000:
            bad_zip = dirr.split("/")[0]
            if bad_zip not in bad_zips:
                bad_zips.append(bad_zip)
    f = open("{}/{}_s1_{}_t{:0>3d}/good_images/bad_zips.txt".format(out_parameters['doris_directory'], AoI_name,
                                                                    asc_dsc[track], tracks[track]), "w")
    for zipp in bad_zips:
        f.write("{}\n".format(zipp))
    f.close()
