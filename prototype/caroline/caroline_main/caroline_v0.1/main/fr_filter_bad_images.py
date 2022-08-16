from sys import argv
filename, param_file, cpath, AoI_name = argv
from os import mkdir

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['doris_directory', 'track','asc_dsc']
out_parameters = []

for param in search_parameters:
    for p in parameters:
	if param in p:
	    do = p.split("=")[1]
	    if "#" in do:
		do = do.split("#")[0]
	    do = do.strip().strip("'").strip('"')
	    out_parameters.append(do)
	    break

tracks = eval(out_parameters[1])
asc_dsc = eval(out_parameters[2])

for track in range(len(tracks)):	
    
    f = open("{}/{}_s1_{}_t{:0>3d}/good_images/zip_files.txt".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track]))
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
	dir = d[-1]
	size = d[-5]
	if eval(size) < 3000000000:
	    bad_zip = dir.split("/")[0]
	    if bad_zip not in bad_zips:
		bad_zips.append(bad_zip)
    f = open("{}/{}_s1_{}_t{:0>3d}/good_images/bad_zips.txt".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track]), "w")   
    for zip in bad_zips:
	f.write("{}\n".format(zip))
    f.close()
