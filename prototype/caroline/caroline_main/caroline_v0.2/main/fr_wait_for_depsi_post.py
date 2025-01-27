from sys import argv
filename, param_file, cpath, AoI_name = argv
import time as t
from datetime import datetime
import glob
import os

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['doris_directory', 'track','asc_dsc', 'depsi_directory']
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

tracks = eval(out_parameters[1])
asc_dsc = eval(out_parameters[2])

job_ids = {}
for track in range(len(tracks)):
    jf = open("{}/{}_s1_{}_t{:0>3d}/psi/job_id.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
    job = jf.read().strip()
    job_ids["{}_s1_{}_t{:0>3d}".format(AoI_name, asc_dsc[track], tracks[track])] = job.split(" ")[-1]
    jf.close()

print("Submitted with job IDs: {}".format(job))

finished = False
while not finished:
    now = datetime.now()
    print("\nDePSI_post: Checking on {}-{:0>2d}-{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}".format(now.year,now.month,now.day,now.hour,now.minute,now.second))
    track_status = [False for track in tracks]
    proper_finish = [False for track in tracks]
    for track in range(len(tracks)):
        f = open("{}/{}_s1_{}_t{:0>3d}/psi/dir_contents_depsi_post.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
        orig_content = f.read().split("\n")
        f.close()
        cur_content = glob.glob("{}/{}_s1_{}_t{:0>3d}/psi/*".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))

        os.system("squeue > {}/{}_s1_{}_t{:0>3d}/queue.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
        qf = open("{}/{}_s1_{}_t{:0>3d}/queue.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track]))
        queue = qf.read().split("\n")
        qf.close()
        found = False
        for i in range(len(queue)):
            queue[i] = queue[i].strip().split(" ")
            if queue[i][0] == job_ids["{}_s1_{}_t{:0>3d}".format(AoI_name, asc_dsc[track], tracks[track])]:
                found = True

        if not found:
            track_status[track] = True
            proper_finish[track] = True

    print("{} tracks not finished, {} finished".format(len(track_status)-sum(track_status), sum(track_status)))
    if False in track_status:
        t.sleep(30)

    else:
        finished = True

