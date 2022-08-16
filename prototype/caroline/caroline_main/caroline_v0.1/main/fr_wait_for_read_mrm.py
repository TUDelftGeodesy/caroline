from sys import argv
filename, param_file, cpath, AoI_name = argv
import time as t
from datetime import datetime
import glob

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['doris_directory', 'track','asc_dsc', 'depsi_directory']
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

finished = False
while not finished:
    now = datetime.now()
    print("\nread_mrm: Checking on {}-{:0>2d}-{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}".format(now.year,now.month,now.day,now.hour,now.minute,now.second))
    track_status = [False for track in tracks]
    proper_finish = [False for track in tracks]
    for track in range(len(tracks)):	
    
        f = open("{}/{}_s1_{}_t{:0>3d}/psi/dir_contents_read_mrm.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
        orig_content = f.read().split("\n")
        f.close()
	cur_content = glob.glob("{}/{}_s1_{}_t{:0>3d}/psi/*".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
	doris_stack_orig = [o for o in orig_content if "read_mrm.sh" in o]
	doris_stack_curr = [c for c in cur_content if "read_mrm.sh" in c]

	if len(doris_stack_orig) != len(doris_stack_curr):
	    track_status[track] = True
	    proper_finish[track] = True
        
    print("{} tracks not finished, {} finished".format(len(track_status)-sum(track_status), sum(track_status)))
    if False in track_status:
	t.sleep(30)

    else:
	finished = True



	
	    

