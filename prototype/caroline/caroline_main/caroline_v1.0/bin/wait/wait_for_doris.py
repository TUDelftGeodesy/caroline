import glob
import os
import time as t
from datetime import datetime
from sys import argv, path

path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from read_param_file import read_param_file

filename, param_file, cpath, AoI_name = argv

search_parameters = ["coregistration_directory", "track", "asc_dsc"]
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters["track"])
asc_dsc = eval(out_parameters["asc_dsc"])

job_ids = {}
for track in range(len(tracks)):
    jf = open(
        "{}/{}_s1_{}_t{:0>3d}/job_id.txt".format(
            out_parameters["coregistration_directory"], AoI_name, asc_dsc[track], tracks[track]
        )
    )
    job = jf.read().strip()
    job_ids[f"{AoI_name}_s1_{asc_dsc[track]}_t{tracks[track]:0>3d}"] = job.split(" ")[-1]
    jf.close()

print(f"Submitted with job IDs: {job_ids}")

finished = False
while not finished:
    now = datetime.now()
    print(
        f"\ndoris v5: Checking on {now.year}-{now.month:0>2d}-{now.day:0>2d} "
        f"{now.hour:0>2d}:{now.minute:0>2d}:{now.second:0>2d}"
    )
    track_status = [False for track in tracks]
    proper_finish = [False for track in tracks]
    for track in range(len(tracks)):
        f = open(
            "{}/{}_s1_{}_t{:0>3d}/dir_contents.txt".format(
                out_parameters["coregistration_directory"], AoI_name, asc_dsc[track], tracks[track]
            )
        )
        orig_content = f.read().split("\n")
        f.close()
        cur_content = glob.glob(
            "{}/{}_s1_{}_t{:0>3d}/*".format(
                out_parameters["coregistration_directory"], AoI_name, asc_dsc[track], tracks[track]
            )
        )
        cur_content = [c.split("/")[-1] for c in cur_content]
        prof_log_orig = [o for o in orig_content if "profile_log" in o]
        prof_log_curr = [c for c in cur_content if "profile_log" in c]
        prof_log = [p for p in prof_log_curr if p not in prof_log_orig]

        os.system(
            "squeue > {}/{}_s1_{}_t{:0>3d}/queue.txt".format(
                out_parameters["coregistration_directory"], AoI_name, asc_dsc[track], tracks[track]
            )
        )
        qf = open(
            "{}/{}_s1_{}_t{:0>3d}/queue.txt".format(
                out_parameters["coregistration_directory"], AoI_name, asc_dsc[track], tracks[track]
            )
        )
        queue = qf.read().split("\n")
        qf.close()
        found = False
        for i in range(len(queue)):
            queue[i] = queue[i].strip().split(" ")
            if queue[i][0] == job_ids[f"{AoI_name}_s1_{asc_dsc[track]}_t{tracks[track]:0>3d}"]:
                found = True

        if not found:
            track_status[track] = True
            if len(prof_log) == 1:
                f = open(
                    "{}/{}_s1_{}_t{:0>3d}/{}".format(
                        out_parameters["coregistration_directory"], AoI_name, asc_dsc[track], tracks[track], prof_log[0]
                    )
                )
                data = f.read().split("\n")
                if data[-1] == "":
                    data = data[:-1]
                f.close()
                if "end" in data[-1]:
                    proper_finish[track] = True

        if len(prof_log) == 1:
            f = open(
                "{}/{}_s1_{}_t{:0>3d}/{}".format(
                    out_parameters["coregistration_directory"], AoI_name, asc_dsc[track], tracks[track], prof_log[0]
                )
            )
            data = f.read().split("\n")
            if data[-1] == "":
                data = data[:-1]
            f.close()
            print(
                "Track {:0>3d} ({}, job_id {}) current step: {}".format(
                    tracks[track],
                    "Finished" if track_status[track] else "Unfinished",
                    job_ids[f"{AoI_name}_s1_{asc_dsc[track]}_t{tracks[track]:0>3d}"],
                    data[-1],
                )
            )
    print(
        f"{len(track_status) - sum(track_status)} tracks not finished, "
        f"{sum(track_status)} finished ({sum(proper_finish)} proper)"
    )
    if False in track_status:
        t.sleep(30)

    else:
        finished = True
