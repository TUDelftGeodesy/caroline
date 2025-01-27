from sys import argv
filename, param_file, cpath, AoI_name, version = argv


fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['depsi_directory', 'track','asc_dsc']
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

base_stack = open("/home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v{}/files/depsi_post/read_mrm.m".format(version))
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters[1])
asc_dsc = eval(out_parameters[2])

for track in range(len(tracks)):

    main = stack.format(AoI_name=AoI_name, asc_dsc=asc_dsc[track],fill_track="{:0>3d}".format(tracks[track]))

    fw = open("{}/{}_s1_{}_t{:0>3d}/psi/read_mrm_{}_s1_{}_t{:0>3d}.m".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track], AoI_name, asc_dsc[track], tracks[track]), 'w')
    fw.write(main)
    fw.close()



