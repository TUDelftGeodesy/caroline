from sys import argv, path
import time as t
from datetime import datetime
import glob
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name = argv

search_parameters = ['track','asc_dsc', 'crop_directory']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

job_ids = {}
for track in range(len(tracks)):
    jf = open("{}/{}_s1_{}_t{:0>3d}/job_id.txt".format(out_parameters['crop_directory'], AoI_name, asc_dsc[track],
                                                       tracks[track]))
    job = jf.read().strip()
    job_ids["{}_s1_{}_t{:0>3d}".format(AoI_name, asc_dsc[track], tracks[track])] = job.split(" ")[-1]
    jf.close()

print("Submitted with job IDs: {}".format(job_ids))

finished = False
while not finished:
    now = datetime.now()
    print("\nS1 crop: Checking on {}-{:0>2d}-{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}".format(now.year,now.month,now.day,now.hour,now.minute,now.second))
    track_status = [False for track in tracks]
    proper_finish = [False for track in tracks]
    for track in range(len(tracks)):
        f = open("{}/{}_s1_{}_t{:0>3d}/dir_contents.txt".format(out_parameters['crop_directory'], AoI_name, asc_dsc[track], tracks[track]))
        orig_content = f.read().split("\n")
        f.close()
        cur_content = glob.glob("{}/{}_s1_{}_t{:0>3d}/*".format(out_parameters['crop_directory'], AoI_name, asc_dsc[track], tracks[track]))
        cur_content = [c.split("/")[-1] for c in cur_content]
        crop_dir = [c for c in cur_content if "cropped_stack" in c]
        crop_dir = [c for c in crop_dir if "DePSI" not in c]
        if len(crop_dir) == 1:
            crop_dir = "{}/{}_s1_{}_t{:0>3d}/{}/*".format(out_parameters['crop_directory'], AoI_name, asc_dsc[track], tracks[track], crop_dir[0])
            crop_content = glob.glob(crop_dir)
            crop_content = [c.split("/")[-1] for c in crop_content]

        os.system("squeue > {}/{}_s1_{}_t{:0>3d}/queue.txt".format(out_parameters['crop_directory'], AoI_name, asc_dsc[track], tracks[track]))
        qf = open("{}/{}_s1_{}_t{:0>3d}/queue.txt".format(out_parameters['crop_directory'], AoI_name, asc_dsc[track], tracks[track]))
        queue = qf.read().split("\n")
        qf.close()
        found = False
        for i in range(len(queue)):
            queue[i] = queue[i].strip().split(" ")
            if queue[i][0] == job_ids["{}_s1_{}_t{:0>3d}".format(AoI_name, asc_dsc[track], tracks[track])]:
                found = True

        if not found:
            track_status[track] = True
            if len(crop_dir) >= 1:
                if "dates.txt" in crop_content:
                    proper_finish[track] = True
        if len(crop_dir) >= 1:
            data = list(sorted(list([c for c in crop_content if "." not in c])))
            if len(data) >= 1:
                print("Track {:0>3d} ({}, job_id {})) current last directory: {} ({} done)".format(tracks[track], "Finished" if track_status[track] else "Unfinished", job_ids["{}_s1_{}_t{:0>3d}".format(AoI_name, asc_dsc[track], tracks[track])], data[-1], len(data)))
            else:
                print("Track {:0>3d} ({}, job_id {})) current last directory: N/A (0 done)".format(tracks[track], "Finished" if track_status[track] else "Unfinished", job_ids["{}_s1_{}_t{:0>3d}".format(AoI_name, asc_dsc[track], tracks[track])]))
    print("{} tracks not finished, {} finished ({} proper)".format(len(track_status)-sum(track_status), sum(track_status), sum(proper_finish)))
    if False in track_status:
        t.sleep(30)

    else:
        finished = True




