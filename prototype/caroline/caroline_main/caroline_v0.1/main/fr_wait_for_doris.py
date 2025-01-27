from sys import argv
filename, param_file, cpath, AoI_name = argv
import time as t
from datetime import datetime
import glob

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
finished = False
while not finished:
    now = datetime.now()
    print("\ndoris v5: Checking on {}-{:0>2d}-{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}".format(now.year,now.month,now.day,now.hour,now.minute,now.second))
    track_status = [False for track in tracks]
    proper_finish = [False for track in tracks]
    for track in range(len(tracks)):	
    
        f = open("{}/{}_s1_{}_t{:0>3d}/dir_contents.txt".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track]))
        orig_content = f.read().split("\n")
        f.close()
	cur_content = glob.glob("{}/{}_s1_{}_t{:0>3d}/*".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track]))
	cur_content = [c.split("/")[-1] for c in cur_content]
	doris_stack_orig = [o for o in orig_content if "doris_stack.sh" in o]
	doris_stack_curr = [c for c in cur_content if "doris_stack.sh" in c]
	prof_log_orig = [o for o in orig_content if "profile_log" in o]
	prof_log_curr = [c for c in cur_content if "profile_log" in c]
	prof_log = [p for p in prof_log_curr if p not in prof_log_orig]
	if len(doris_stack_orig) != len(doris_stack_curr):
	    track_status[track] = True
	    if len(prof_log) == 1:
		f = open("{}/{}_s1_{}_t{:0>3d}/{}".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track], prof_log[0]))
		data = f.read().split("\n")
		if data[-1] == "":
		    data = data[:-1]
		f.close()
		if "end" in data[-1]:
		    proper_finish[track] = True
	if len(prof_log) == 1:
            f = open("{}/{}_s1_{}_t{:0>3d}/{}".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track], prof_log[0]))
            data = f.read().split("\n")
	    if data[-1] == "":
		data = data[:-1]
            f.close()
	    print("Track {:0>3d} ({}) current step: {}".format(tracks[track], "Finished" if track_status[track] else "Unfinished", data[-1]))
    print("{} tracks not finished, {} finished ({} proper)".format(len(track_status)-sum(track_status), sum(track_status), sum(proper_finish)))
    if False in track_status:
	t.sleep(30)

    else:
	finished = True



	
	    

