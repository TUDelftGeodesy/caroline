from sys import argv
filename, param_file, cpath, AoI_name, version, caroline_dir = argv


fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['doris_directory', 'track','asc_dsc']
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

base_stack = open("{}/caroline_v{}/files/doris_v5/doris_stack.sh".format(caroline_dir, version))
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters[1])
asc_dsc = eval(out_parameters[2])

for track in range(len(tracks)):
    doris_stack = stack.format(doris_path="{}/{}_s1_{}_t{:0>3d}".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track]))

    fw = open("{}/{}_s1_{}_t{:0>3d}/doris_stack.sh".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track]), 'w')
    fw.write(doris_stack)
    fw.close()



