from sys import argv
filename, param_file, cpath = argv

pf = open(cpath+"/"+param_file)
parameters = pf.read().split("\n")
pf.close()

search_parameters = ['do_doris', 'do_stack_stitching', 'do_depsi', 'do_depsi_post',
		     'doris_directory', 'stitch_directory', 'depsi_directory', 'shape_directory', 'AoI_name', 'Caroline_version']

for parameter in search_parameters:
    for param in parameters:
        if parameter in param.split("=")[0]:
            do = param.split("=")[1]
            if "#" in do:
                do = do.split("#")[0]
            do = do.strip().strip("'").strip('"')
            f = open("{}/auxiliary_files/{}.txt".format(cpath, parameter), "w")
            f.write(do)
            f.close()
            break


search_parameters = ["track", "asc_dsc", "AoI_name"]
output = []

for parameter in search_parameters:
    for param in parameters:
        if parameter+' ' in param:
            do = param.split("=")[1]
            if "#" in do:
                do = do.split("#")[0]
            do = do.strip().strip("'").strip('"')
            output.append(do)
            break

tracks = eval(output[0])
asc_dsc = eval(output[1])
AoI_name = output[2]

f = open("{}/auxiliary_files/loop_directories.txt".format(cpath), "w")
for track in range(len(tracks)):
    f.write("{}_s1_{}_t{:0>3d}\n".format(AoI_name, asc_dsc[track], tracks[track]))
f.close()
