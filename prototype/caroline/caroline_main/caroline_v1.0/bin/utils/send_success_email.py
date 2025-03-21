import glob
from sys import argv
from typing import Literal

from read_param_file import read_param_file

try:
    filename, param_file, cpath, slurm_job_id = argv

    search_parameters = [
        "track",
        "asc_dsc",
        "do_coregistration",
        "do_crop",
        "do_depsi",
        "do_depsi_post",
        "sensor",
        "coregistration_directory",
        "crop_directory",
        "depsi_directory",
        "do_reslc",
        "reslc_directory",
        "skygeo_viewer",
        "coregistration_AoI_name",
        "crop_AoI_name",
        "depsi_AoI_name",
        "reslc_AoI_name",
        "skygeo_customer",
        "project_owner",
        "project_owner_email",
        "project_engineer",
        "project_engineer_email",
        "project_objective",
        "project_notes",
    ]
    out_parameters = read_param_file(cpath, param_file, search_parameters)

    if out_parameters["skygeo_customer"] is None:  # backwards compatibility for #12
        out_parameters["skygeo_customer"] = "caroline"

    tracks = eval(out_parameters["track"])
    asc_dsc = eval(out_parameters["asc_dsc"])

    tracks_formatted = []
    for i in range(len(tracks)):
        tracks_formatted.append(f"{asc_dsc[i]}_t{tracks[i]:0>3d}")

    if len(tracks_formatted) == 1:
        tracks_formatted = tracks_formatted[0]

    run_id = param_file.split("_spider_")[1].split("/")[0][:-16]

    f = open(f"{cpath}/{param_file}")
    paramfile = f.read()
    f.close()

    log = "==========DEBUG LOGS===========\n\n"
    log += f"CAROLINE Slurm output: {cpath}/slurm-{slurm_job_id}.out\n\n"

    success_rates = {
        "do_coregistration": [[], []],
        "do_crop": [[], []],
        "do_reslc": [[], []],
        "do_depsi": [[], []],
        "do_depsi_post": [[], []],
    }
    for step in ["do_coregistration", "do_crop", "do_reslc", "do_depsi", "do_depsi_post"]:
        if out_parameters[step] == "1":
            if step == "do_coregistration":
                if out_parameters["sensor"] == "S1":
                    log += "\n\n---------DORIS v5--------\n\n"
                    for track in range(len(tracks)):
                        log += f"---Track {tracks[track]}_{asc_dsc[track]}---\n\n"
                        status_file = None
                        slurm_file = None
                        dir_file = "{}/{}_s1_{}_t{:0>3d}/dir_contents.txt".format(
                            out_parameters["coregistration_directory"],
                            out_parameters["coregistration_AoI_name"],
                            asc_dsc[track],
                            tracks[track],
                        )
                        f = open(dir_file)
                        prev_dir_contents = f.read().split("\n")
                        f.close()
                        profile_logs = glob.glob(
                            "{}/{}_s1_{}_t{:0>3d}/profile_log*".format(
                                out_parameters["coregistration_directory"],
                                out_parameters["coregistration_AoI_name"],
                                asc_dsc[track],
                                tracks[track],
                            )
                        )
                        slurms = glob.glob(
                            "{}/{}_s1_{}_t{:0>3d}/slurm*.out".format(
                                out_parameters["coregistration_directory"],
                                out_parameters["coregistration_AoI_name"],
                                asc_dsc[track],
                                tracks[track],
                            )
                        )
                        for profile_log in profile_logs:
                            if profile_log.split("/")[-1] not in prev_dir_contents:
                                status_file = profile_log
                                break
                        for slurm in list(sorted(list(slurms))):
                            if slurm.split("/")[-1] not in prev_dir_contents:
                                slurm_file = slurm
                                break

                        if status_file is not None:
                            f = open(status_file)
                            status = f.read()
                            f.close()

                            if " : end" in status:
                                success_rates[step][0].append(
                                    f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                                )
                                log += "Step finished successfully!\n\n"
                            else:
                                success_rates[step][1].append(
                                    f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                                )
                                log += "!!! Step did not finish properly!\n\n"
                        else:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                            )
                            log += "!!! Step did not start properly!\n\n"

                        log += f"Profile log: {status_file}\nSlurm output: {slurm_file}\n\n"

                        if status_file is not None:
                            f = open(status_file)
                            status = f.read()
                            f.close()
                            log += "Profile log output:\n"
                            log += status
                            log += "\n\n"

                else:
                    log += "\n\n---------DeInSAR---------\n\n"
                    for track in range(len(tracks)):
                        log += f"---Track {tracks[track]}_{asc_dsc[track]}---\n\n"

                        slurm_file = None
                        dir_file = "{}/{}_{}_{}_t{:0>3d}/dir_contents.txt".format(
                            out_parameters["coregistration_directory"],
                            out_parameters["coregistration_AoI_name"],
                            out_parameters["sensor"].lower(),
                            asc_dsc[track],
                            tracks[track],
                        )
                        f = open(dir_file)
                        prev_dir_contents = f.read().split("\n")
                        f.close()
                        slurms = glob.glob(
                            "{}/{}_{}_{}_t{:0>3d}/slurm*.out".format(
                                out_parameters["coregistration_directory"],
                                out_parameters["coregistration_AoI_name"],
                                out_parameters["sensor"].lower(),
                                asc_dsc[track],
                                tracks[track],
                            )
                        )
                        for slurm in slurms:
                            if slurm.split("/")[-1] not in prev_dir_contents:
                                slurm_file = slurm
                                break

                        if slurm_file is not None:
                            f = open(slurm_file)
                            status = f.read()
                            f.close()

                            if "Traceback (most recent call last):" in status or "EXCEPTION class" in status:
                                success_rates[step][1].append(
                                    f'{out_parameters["sensor"].lower()}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                                )
                                log += "!!! Step did not finish properly!\n\n"
                            else:
                                success_rates[step][0].append(
                                    f'{out_parameters["sensor"].lower()}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                                )
                                log += "Step finished successfully!\n\n"
                        else:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"].lower()}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                            )
                            log += "!!! Step did not start properly!\n\n"

                        log += f"Slurm output: {slurm_file}\n\n"

            elif step == "do_crop":
                log += "\n\n---------Cropping---------\n\n"
                for track in range(len(tracks)):
                    log += f"---Track {tracks[track]}_{asc_dsc[track]}---\n\n"

                    slurm_file = None
                    dir_file = "{}/{}_{}_{}_t{:0>3d}/dir_contents.txt".format(
                        out_parameters["crop_directory"],
                        out_parameters["crop_AoI_name"],
                        out_parameters["sensor"].lower(),
                        asc_dsc[track],
                        tracks[track],
                    )
                    f = open(dir_file)
                    prev_dir_contents = f.read().split("\n")
                    f.close()
                    slurms = glob.glob(
                        "{}/{}_{}_{}_t{:0>3d}/slurm*.out".format(
                            out_parameters["crop_directory"],
                            out_parameters["crop_AoI_name"],
                            out_parameters["sensor"].lower(),
                            asc_dsc[track],
                            tracks[track],
                        )
                    )
                    for slurm in list(sorted(list(slurms))):
                        if slurm.split("/")[-1] not in prev_dir_contents:
                            slurm_file = slurm
                            break

                    if slurm_file is not None:
                        f = open(slurm_file)
                        status = f.read()
                        f.close()

                        if "Error in " in status:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                            )
                            log += "!!! Step did not finish properly!\n\n"
                        else:
                            success_rates[step][0].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                            )
                            log += "Step finished successfully!\n\n"
                    else:
                        success_rates[step][1].append(
                            f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                        )
                        log += "!!! Step did not start properly!\n\n"

                    log += f"Slurm output: {slurm_file}\n\n"

            elif step == "do_reslc":
                log += "\n\n---------Re-SLC---------\n\n"
                for track in range(len(tracks)):
                    log += f"---Track {tracks[track]}_{asc_dsc[track]}---\n\n"

                    slurm_file = None
                    dir_file = "{}/{}_{}_{}_t{:0>3d}/dir_contents.txt".format(
                        out_parameters["reslc_directory"],
                        out_parameters["reslc_AoI_name"],
                        out_parameters["sensor"].lower(),
                        asc_dsc[track],
                        tracks[track],
                    )
                    f = open(dir_file)
                    prev_dir_contents = f.read().split("\n")
                    f.close()
                    slurms = glob.glob(
                        "{}/{}_{}_{}_t{:0>3d}/slurm*.out".format(
                            out_parameters["reslc_directory"],
                            out_parameters["reslc_AoI_name"],
                            out_parameters["sensor"].lower(),
                            asc_dsc[track],
                            tracks[track],
                        )
                    )
                    for slurm in list(sorted(list(slurms))):
                        if slurm.split("/")[-1] not in prev_dir_contents:
                            slurm_file = slurm  # it's the first one
                            break

                    if slurm_file is not None:
                        f = open(slurm_file)
                        status = f.read()
                        f.close()

                        if "Finishing... Closing client." not in status:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                            )
                            log += "!!! Step did not finish properly!\n\n"
                        else:
                            success_rates[step][0].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                            )
                            log += "Step finished successfully!\n\n"
                    else:
                        success_rates[step][1].append(
                            f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                        )
                        log += "!!! Step did not start properly!\n\n"

                    log += f"Slurm output: {slurm_file}\n\n"

                    if slurm_file is not None:
                        f = open(slurm_file)
                        status = f.read()
                        f.close()
                        log += "Scheduler Slurm output:\n"
                        log += status
                        log += "\n\n"

            elif step == "do_depsi":
                log += "\n\n---------DePSI--------\n\n"
                for track in range(len(tracks)):
                    log += f"---Track {tracks[track]}_{asc_dsc[track]}---\n\n"
                    status_file = None
                    slurm_file = None
                    dir_file = "{}/{}_{}_{}_t{:0>3d}/psi/dir_contents.txt".format(
                        out_parameters["depsi_directory"],
                        out_parameters["depsi_AoI_name"],
                        out_parameters["sensor"].lower(),
                        asc_dsc[track],
                        tracks[track],
                    )
                    f = open(dir_file)
                    prev_dir_contents = f.read().split("\n")
                    f.close()
                    resfiles = glob.glob(
                        "{}/{}_{}_{}_t{:0>3d}/psi/*resfile.txt".format(
                            out_parameters["depsi_directory"],
                            out_parameters["depsi_AoI_name"],
                            out_parameters["sensor"].lower(),
                            asc_dsc[track],
                            tracks[track],
                        )
                    )
                    slurms = glob.glob(
                        "{}/{}_{}_{}_t{:0>3d}/psi/slurm*.out".format(
                            out_parameters["depsi_directory"],
                            out_parameters["depsi_AoI_name"],
                            out_parameters["sensor"].lower(),
                            asc_dsc[track],
                            tracks[track],
                        )
                    )
                    for resfile in resfiles:
                        if resfile.split("/")[-1] not in prev_dir_contents:
                            status_file = resfile
                            break
                    for slurm in list(sorted(list(slurms))):
                        if slurm.split("/")[-1] not in prev_dir_contents:
                            slurm_file = slurm  # it's the first one
                            break

                    if status_file is not None:
                        f = open(status_file)
                        status = f.read()
                        f.close()

                        if "group8, end spatio-temporal consistency." in status:
                            success_rates[step][0].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                            )
                            log += "Step finished successfully!\n\n"
                        else:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                            )
                            log += "!!! Step did not finish properly!\n\n"
                    else:
                        success_rates[step][1].append(
                            f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                        )
                        log += "!!! Step did not start properly!\n\n"

                    log += f"Resfile: {status_file}\nSlurm output: {slurm_file}\n\n"

                    if status_file is not None:
                        f = open(status_file)
                        status = f.read()
                        f.close()
                        log += "Resfile output:\n"
                        log += status
                        log += "\n\n"

            elif step == "do_depsi_post":
                log += "\n\n---------DePSI-post--------\n\n"
                for track in range(len(tracks)):
                    log += f"---Track {tracks[track]}_{asc_dsc[track]}---\n\n"
                    status_file = None
                    slurm_file = None
                    dir_file = "{}/{}_{}_{}_t{:0>3d}/psi/dir_contents_depsi_post.txt".format(
                        out_parameters["depsi_directory"],
                        out_parameters["depsi_AoI_name"],
                        out_parameters["sensor"].lower(),
                        asc_dsc[track],
                        tracks[track],
                    )
                    f = open(dir_file)
                    prev_dir_contents = f.read().split("\n")
                    f.close()

                    slurms = glob.glob(
                        "{}/{}_{}_{}_t{:0>3d}/psi/slurm*.out".format(
                            out_parameters["depsi_directory"],
                            out_parameters["depsi_AoI_name"],
                            out_parameters["sensor"].lower(),
                            asc_dsc[track],
                            tracks[track],
                        )
                    )

                    for slurm in list(sorted(list(slurms))):
                        if slurm.split("/")[-1] not in prev_dir_contents:
                            slurm_file = slurm  # it's the first one
                            break

                    if slurm_file is not None:
                        f = open(slurm_file)
                        status = f.read()
                        f.close()

                        if "Write csv web portal file ..." in status:
                            success_rates[step][0].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                            )
                            log += "Step finished successfully!\n\n"
                        else:
                            success_rates[step][1].append(
                                f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                            )
                            log += "!!! Step did not finish properly!\n\n"
                    else:
                        success_rates[step][1].append(
                            f'{out_parameters["sensor"]}_{asc_dsc[track]}_t{f"{tracks[track]:0>3d}"}'
                        )
                        log += "!!! Step did not start properly!\n\n"

                    log += f"Slurm output: {slurm_file}\n\n"
    log += "================"

    project_characteristics = f"""Project characteristics:
Owner: {out_parameters['project_owner']} ({out_parameters['project_owner_email']})
Engineer: {out_parameters['project_engineer']} ({out_parameters['project_engineer_email']})
Objective: {out_parameters['project_objective']}
Notes: {out_parameters['project_notes']}
"""

    def print_mail(
        run_id: str,
        track: str,
        sensor: str,
        dv5: Literal["Yes", "No"],
        crop: Literal["Yes", "No"],
        depsi: Literal["Yes", "No"],
        dppu: Literal["Yes", "No"],
        portal_link: str,
        coreg_dir: str,
        crop_dir: str,
        depsi_dir: str,
        depsipost_dir: str,
        reslc: Literal["Yes", "No"],
        reslcdir: str,
        paramfile: str,
        param_file: str,
        logs: str,
        coreg_correct: str,
        crop_correct: str,
        reslc_correct: str,
        depsi_correct: str,
        dp_correct: str,
        project_characteristics: str,
    ) -> None:
        """Print the CAROLINE email.

        This function prints the CAROLINE email based on a set of parameters defined below.

        Parameters
        ----------
        run_id : str
            Name of the run as specified by the parameter file naming and area-track-list
        track : str
            Track (or tracks) that was processed
        sensor : str
            Sensor which was processed
        dv5 : Literal["Yes", "No"]
            Whether Coregistration was done (either Doris v5 or Doris v4)
        crop : Literal["Yes", "No"]
            Whether cropping was done
        depsi : Literal["Yes", "No"]
            Whether DePSI was done
        dppu : Literal["Yes", "No"]
            Whether DePSI-post and portal uploading was done
        portal_link : str
            Link to the portal if `dppu`=`"Yes"`, otherwise ""
        coreg_dir : str
            Coregistration directory
        crop_dir : str
            Crop directory
        depsi_dir : str
            DePSI directory
        depsipost_dir : str
            DePSI-post directory (should be equal to `depsi_dir`)
        reslc : Literal["Yes", "No"]
            Whether re-SLC was done
        reslcdir : str
            re-SLC directory
        paramfile : str
            Contents of the parameter file
        param_file : str
            Absolute path to the parameter file
        logs : str
            Logs of all subprocesses
        coreg_correct : str
            Indication whether coregistration finished correctly
        crop_correct : str
            Indication whether cropping finished correctly
        reslc_correct : str
            Indication whether re-SLC finished correctly
        depsi_correct : str
            Indication whether DePSI finished correctly
        dp_correct : str
            Indication whether DePSI-post finished correctly
        project_characteristics : str
            List of project owner, engineer, objective, and notes

        """
        if dv5 == "Yes":
            if "improper finish: []" in coreg_correct:
                coreg_correct = coreg_correct.split(", improper")[0]
            coreg_line = f"Coregistration: {coreg_correct} {coreg_dir}\n\n"
        else:
            coreg_line = ""

        if crop == "Yes":
            if "improper finish: []" in crop_correct:
                crop_correct = crop_correct.split(", improper")[0]
            crop_line = f"Cropping: {crop_correct} {crop_dir}\n"
        else:
            crop_line = ""

        if reslc == "Yes":
            if "improper finish: []" in reslc_correct:
                reslc_correct = reslc_correct.split(", improper")[0]
            reslc_line = f"Re-SLC: {reslc_correct} {reslcdir}\n\n"
        elif crop == "Yes":
            reslc_line = "\n"  # add an extra divider line
        else:
            reslc_line = ""

        if depsi == "Yes":
            if "improper finish: []" in depsi_correct:
                depsi_correct = depsi_correct.split(", improper")[0]
            depsi_line = f"DePSI: {depsi_correct} {depsi_dir}\n"
        else:
            depsi_line = ""

        if dppu == "Yes":
            if "improper finish: []" in dp_correct:
                dp_correct = dp_correct.split(", improper")[0]
            dppu_line = f"DePSI-post & portal upload: {dp_correct} {depsipost_dir}\n"
        else:
            dppu_line = ""

        print(
            f"""Dear radargroup,
    
    A new CAROLINE run has just finished on run {run_id}! 
    
    {project_characteristics}
    Run characteristics:
    Track(s): {track}
    Sensor: {sensor}
    
    The following steps were run:
    {coreg_line}{crop_line}{reslc_line}{depsi_line}{dppu_line}
    
    {portal_link}
    
    In case of questions, please contact Niels at n.h.jansen@tudelft.nl or Simon at s.a.n.vandiepen@tudelft.nl
    
    Kind regards,
    The CAROLINE development team,
    Freek, Niels, and Simon
    
    =======================================
    ===========DEBUG info==================
    =======================================
    First logs of the subprocesses, then the parameter file.
    =======================================
    
    {logs}
    
    --- PARAMETER FILE: {param_file} ---
    {paramfile}"""
        )

    print_mail(
        run_id=run_id,
        track=tracks_formatted,
        sensor=out_parameters["sensor"],
        dv5="Yes" if eval(out_parameters["do_coregistration"]) == 1 else "No",
        crop="Yes" if eval(out_parameters["do_crop"]) == 1 else "No",
        depsi="Yes" if eval(out_parameters["do_depsi"]) == 1 else "No",
        dppu="Yes" if eval(out_parameters["do_depsi_post"]) == 1 else "No",
        portal_link="NOTE: it can take a few hours for the results to show up in the portal.\n"
        + "The DePSI-post results can be accessed at "
        + "https://caroline.portal-tud.skygeo.com/portal/"
        + f"{out_parameters['skygeo_customer']}/{out_parameters['skygeo_viewer']} ."
        if eval(out_parameters["do_depsi_post"]) == 1
        else "",
        coreg_dir=f"(located in {out_parameters['coregistration_directory']} )"
        if eval(out_parameters["do_coregistration"]) == 1
        else "",
        crop_dir=f"(located in {out_parameters['crop_directory']} )" if eval(out_parameters["do_crop"]) == 1 else "",
        depsi_dir=f"(located in {out_parameters['depsi_directory']} )" if eval(out_parameters["do_depsi"]) == 1 else "",
        depsipost_dir=f"(located in {out_parameters['depsi_directory']} )"
        if eval(out_parameters["do_depsi_post"]) == 1
        else "",
        reslc="Yes" if eval(out_parameters["do_reslc"]) == 1 else "No",
        reslcdir=f"(located in {out_parameters['reslc_directory']} )" if eval(out_parameters["do_reslc"]) == 1 else "",
        paramfile=paramfile,
        param_file=f"{cpath}/{param_file}",
        logs=log,
        coreg_correct=f"Proper finish: {success_rates['do_coregistration'][0]}, "
        + f"improper finish: {success_rates['do_coregistration'][1]}"
        if eval(out_parameters["do_coregistration"]) == 1
        else "",
        crop_correct=f"Proper finish: {success_rates['do_crop'][0]}, improper finish: {success_rates['do_crop'][1]}"
        if eval(out_parameters["do_crop"]) == 1
        else "",
        reslc_correct=f"Proper finish: {success_rates['do_reslc'][0]}, improper finish: {success_rates['do_reslc'][1]}"
        if eval(out_parameters["do_reslc"]) == 1
        else "",
        depsi_correct=f"Proper finish: {success_rates['do_depsi'][0]}, improper finish: {success_rates['do_depsi'][1]}"
        if eval(out_parameters["do_depsi"]) == 1
        else "",
        dp_correct=f"Proper finish: {success_rates['do_depsi_post'][0]}, "
        + f"improper finish: {success_rates['do_depsi_post'][1]}"
        if eval(out_parameters["do_depsi_post"]) == 1
        else "",
        project_characteristics=project_characteristics,
    )

except Exception as e:
    print(f"""Dear radargroup,

It appears the CAROLINE email generation has encountered an error. Please create an issue on the CAROLINE GitHub project
https://github.com/TUDelftGeodesy/caroline/issues mentioning:
1) that the email generation failed
2) the subject of this mail
3) the following error message:

{e}


Please add the labels Priority-0 and bug, and assign Simon.

Thank you in advance, and sorry for the inconvenience.

Kind regards,
The CAROLINE development team,
Freek, Niels, and Simon

""")
