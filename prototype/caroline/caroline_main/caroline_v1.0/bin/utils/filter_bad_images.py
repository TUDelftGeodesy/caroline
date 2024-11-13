from sys import argv
from read_param_file import read_param_file
import glob
import zipfile
filename, param_file, cpath, AoI_name = argv

search_parameters = ['coregistration_directory', 'track', 'asc_dsc']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

status = []

for track in range(len(tracks)):
    f = open("{}/{}_s1_{}_t{:0>3d}/good_images/zip_files.txt".format(out_parameters['coregistration_directory'], AoI_name,
                                                                     asc_dsc[track], tracks[track]))
    data = f.read().split("\n")
    f.close()

    # check for incomplete downloads
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
        if 'SLC__1SDV_' in dirr:  # VV/VH dual polarisation
            if eval(size) < 3000000000:
                bad_zip = dirr.split("/")[0]
                if bad_zip not in bad_zips:
                    bad_zips.append(bad_zip)
        elif 'SLC__1SSV_' in dirr:  # VV polarisation is half the size
            if eval(size) < 1500000000:
                bad_zip = dirr.split("/")[0]
                if bad_zip not in bad_zips:
                    bad_zips.append(bad_zip)
        else:
            print(f'Cannot detect polarisation on {dirr}, skipping...')

    # check for directories without zip files
    dirs = glob.glob("{}/{}_s1_{}_t{:0>3d}/good_images/2*".format(out_parameters['coregistration_directory'], AoI_name,
                                                                  asc_dsc[track], tracks[track]))
    for dr in dirs:
        files = glob.glob(f'{dr}/*.zip')
        if len(files) == 0:  # no zip files present
            bad_zip = dr.split('/')[-1]
            if bad_zip not in bad_zips:
                bad_zips.append(bad_zip)
        for file in files:
            try:
                _ = zipfile.ZipFile(file)
            except zipfile.BadZipFile:  # zip file cannot be opened --> incomplete download
                status.append(file)
                bad_zip = dr.split('/')[-1]
                if bad_zip not in bad_zips:
                    bad_zips.append(bad_zip)

    f = open("{}/{}_s1_{}_t{:0>3d}/good_images/bad_zips.txt".format(out_parameters['coregistration_directory'], AoI_name,
                                                                    asc_dsc[track], tracks[track]), "w")
    for zipp in bad_zips:
        f.write("{}\n".format(zipp))
    f.close()

if len(status) > 0:
    print('Rejected the following ZIP files as incomplete downloads:')
    for i in status:
        print(status)
else:
    print('Found no incomplete downloads.')
