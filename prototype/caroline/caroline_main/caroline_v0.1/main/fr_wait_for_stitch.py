from sys import argv
filename, param_file, cpath, AoI_name = argv
import time as t
from datetime import datetime
import glob

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['doris_directory', 'track','asc_dsc', 'stitch_directory']
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
    print("\nStack stitching: Checking on {}-{:0>2d}-{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}".format(now.year,now.month,now.day,now.hour,now.minute,now.second))
    track_status = [False for track in tracks]
    proper_finish = [False for track in tracks]
    for track in range(len(tracks)):	
    
        f = open("{}/{}_s1_{}_t{:0>3d}/dir_contents.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
        orig_content = f.read().split("\n")
        f.close()
	cur_content = glob.glob("{}/{}_s1_{}_t{:0>3d}/*".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
	cur_content = [c.split("/")[-1] for c in cur_content]
	doris_stack_orig = [o for o in orig_content if "MAIN.sh" in o]
	doris_stack_curr = [c for c in cur_content if "MAIN.sh" in c]
	
	crop_dir = [c for c in cur_content if "cropped_stack" in c]
	crop_dir = [c for c in crop_dir if "DePSI" not in c]
	if len(crop_dir) == 1:
	    crop_dir = "{}/{}_s1_{}_t{:0>3d}/{}/*".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track], crop_dir[0])	
	    crop_content = glob.glob(crop_dir)
	    crop_content = [c.split("/")[-1] for c in crop_content]
	    

	if len(doris_stack_orig) != len(doris_stack_curr):
	    track_status[track] = True
	    if len(crop_dir) >= 1:
		if "dates.txt" in crop_content:
		    proper_finish[track] = True
	if len(crop_dir) >= 1:
            data = list(sorted(list([c for c in crop_content if "." not in c])))
	    print("Track {:0>3d} ({}) current last directory: {} ({} done)".format(tracks[track], "Finished" if track_status[track] else "Unfinished", data[-1], len(data)))
    print("{} tracks not finished, {} finished ({} proper)".format(len(track_status)-sum(track_status), sum(track_status), sum(proper_finish)))
    if False in track_status:
	t.sleep(30)

    else:
	finished = True



	
	    

