import glob
import os
import time as t
from datetime import datetime
from sys import argv, path

path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from read_param_file import read_param_file

filename, param_file, cpath, AoI_name = argv

search_parameters = ["coregistration_directory", "track", "asc_dsc", "sensor"]
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters["track"])
asc_dsc = eval(out_parameters["asc_dsc"])

job_ids = {}
for track in range(len(tracks)):
    jf = open(
        "{}/{}_{}_{}_t{:0>3d}/job_id.txt".format(
            out_parameters["coregistration_directory"],
            AoI_name,
            out_parameters["sensor"].lower(),
            asc_dsc[track],
            tracks[track],
        )
    )
    job = jf.read().strip()
    job_ids["{}_{}_{}_t{:0>3d}".format(AoI_name, out_parameters["sensor"].lower(), asc_dsc[track], tracks[track])] = (
        job.split(" ")[-1]
    )
    jf.close()

print(f"Submitted with job IDs: {job_ids}")

finished = False
while not finished:
    now = datetime.now()
    print(
        f"\nDeInSAR: Checking on {now.year}-{now.month:0>2d}-{now.day:0>2d} "
        f"{now.hour:0>2d}:{now.minute:0>2d}:{now.second:0>2d}"
    )
    track_status = [False for track in tracks]
    proper_finish = [False for track in tracks]
    for track in range(len(tracks)):
        f = open(
            "{}/{}_{}_{}_t{:0>3d}/dir_contents.txt".format(
                out_parameters["coregistration_directory"],
                AoI_name,
                out_parameters["sensor"].lower(),
                asc_dsc[track],
                tracks[track],
            )
        )
        orig_content = f.read().split("\n")
        f.close()
        cur_content = glob.glob(
            "{}/{}_{}_{}_t{:0>3d}/*".format(
                out_parameters["coregistration_directory"],
                AoI_name,
                out_parameters["sensor"].lower(),
                asc_dsc[track],
                tracks[track],
            )
        )

        os.system(
            "squeue > {}/{}_{}_{}_t{:0>3d}/queue.txt".format(
                out_parameters["coregistration_directory"],
                AoI_name,
                out_parameters["sensor"].lower(),
                asc_dsc[track],
                tracks[track],
            )
        )
        qf = open(
            "{}/{}_{}_{}_t{:0>3d}/queue.txt".format(
                out_parameters["coregistration_directory"],
                AoI_name,
                out_parameters["sensor"].lower(),
                asc_dsc[track],
                tracks[track],
            )
        )
        queue = qf.read().split("\n")
        qf.close()
        found = False
        for i in range(len(queue)):
            queue[i] = queue[i].strip().split(" ")
            if (
                queue[i][0]
                == job_ids[
                    "{}_{}_{}_t{:0>3d}".format(
                        AoI_name, out_parameters["sensor"].lower(), asc_dsc[track], tracks[track]
                    )
                ]
            ):
                found = True

        if not found:
            track_status[track] = True
            proper_finish[track] = True

    print(f"{len(track_status) - sum(track_status)} tracks not finished, {sum(track_status)} finished")
    if False in track_status:
        t.sleep(30)

    else:
        finished = True
