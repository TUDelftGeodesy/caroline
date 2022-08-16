from sys import argv
filename, param_file, cpath = argv

pf = open(cpath+"/"+param_file)
parameters = pf.read().split("\n")
pf.close()

search_parameters = ['do_doris', 'do_stack_stitching', 'do_depsi', 'do_depsi_post',
		     'doris_directory', 'stitch_directory', 'depsi_directory', 'shape_directory', 'AoI_name', 'Caroline_version']

for parameter in search_parameters:
    for param in parameters:
        if parameter+' ' in param:
	    do = param.split("=")[1]
            if "#" in do:
                do = do.split("#")[0]
	    do = do.strip().strip("'").strip('"')
            f = open("{}/auxiliary_files/{}.txt".format(cpath, parameter), "w")
	    f.write(do)
	    f.close()
	    break


