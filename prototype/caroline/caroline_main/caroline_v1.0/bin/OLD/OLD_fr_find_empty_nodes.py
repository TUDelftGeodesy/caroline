from os import mkdir
from sys import argv

filename, param_file, cpath, AoI_name, needed_threads = argv

UNALLOWED_NODES = ["01", "02", "13"]  # 01 is too slow,
# 02 often fails to copy output and error files causing the code to fail, 13 cannot run on guest node

fp = open(f"{cpath}/{param_file}")
parameters = fp.read().split("\n")
fp.close()

search_parameters = ["track", "asc_dsc"]
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

tracks = eval(out_parameters[0])
asc_dsc = eval(out_parameters[1])

f = open(f"{cpath}/auxiliary_files/nodeload.txt")
data = f.read().split("\n")[2:-1]
f.close()

nodeloads = []
for node in data:
    dat = node.split(" ")
    cut_dat = []
    for d in dat:
        if d != "":
            cut_dat.append(d)
        if "down" in cut_dat[2]:
            nodeloads.append([cut_dat[0][-2:], eval(cut_dat[1]), eval(cut_dat[1])])
        else:
            nodeloads.append([cut_dat[0][-2:], eval(cut_dat[1]), eval(cut_dat[2] if cut_dat[2] != "free" else "0")])

allowed_nodes = []
for node in nodeloads:
    if node[1] - node[2] >= eval(needed_threads) and node[0] not in UNALLOWED_NODES:
        allowed_nodes.append(node[0])

if len(allowed_nodes) < len(tracks):
    print("Warning: not enough nodes available for running all tracks concurrently! Processing may take longer...")

if len(allowed_nodes) == 0:
    print("Warning: no nodes available! Waiting for nodes...")
    f = open(f"{cpath}/auxiliary_files/nodes_available.txt", "w")
    f.write("0")
    f.close()
else:
    f = open(f"{cpath}/auxiliary_files/nodes_available.txt", "w")
    f.write("1")
    f.close()

if len(allowed_nodes) > 0:
    for track in range(len(tracks)):
        try:
            mkdir(f"{cpath}/auxiliary_files/{AoI_name}_s1_{asc_dsc[track]}_t{tracks[track]:0>3d}")
        except OSError:
            pass  # Directory already exists
        print(
            f"{AoI_name}_s1_{asc_dsc[track]}_t{tracks[track]:0>3d}: "
            f"selected node {allowed_nodes[track % len(allowed_nodes)]}"
        )
        f = open(f"{cpath}/auxiliary_files/{AoI_name}_s1_{asc_dsc[track]}_t{tracks[track]:0>3d}/node.txt", "w")
        f.write(f"{allowed_nodes[track % len(allowed_nodes)]}")
        f.close()
