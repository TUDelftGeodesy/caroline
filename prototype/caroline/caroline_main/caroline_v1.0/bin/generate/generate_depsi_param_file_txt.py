import glob
import os
from sys import argv, path

import numpy as np

path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from read_param_file import read_param_file

filename, param_file, cpath, AoI_name, crop_AoI_name, version, caroline_dir = argv

search_parameters = [
    "crop_directory",
    "track",
    "asc_dsc",
    "depsi_directory",
    "max_mem_buffer",
    "visible_plots",
    "detail_plots",
    "processing_groups",
    "run_mode",
    "exclude_date",
    "az_spacing",
    "r_spacing",
    "slc_selection_input",
    "ifg_selection_input",
    "ref_cn",
    "Ncv",
    "ps_method",
    "psc_model",
    "ps_model",
    "final_model",
    "breakpoint",
    "breakpoint2",
    "ens_coh_threshold",
    "varfac_threshold",
    "detrend_method",
    "output_format",
    "stc_min_max",
    "do_apriori_sidelobe_mask",
    "do_aposteriori_sidelobe_mask",
    "ref_height",
    "amplitude_calibration",
    "psc_selection_method",
    "psc_selection_gridsize",
    "psc_threshold",
    "max_arc_length",
    "network_method",
    "Ncon",
    "Nparts",
    "Npsc_selections",
    "do_water_mask",
    "gamma_threshold",
    "psc_distribution",
    "weighted_unwrap",
    "livetime_threshold",
    "peak_tolerance",
    "psp_selection_method",
    "psp_threshold1",
    "psp_threshold2",
    "ps_eval_method",
    "Namp_disp_bins",
    "Ndens_iterations",
    "densification_flag",
    "ps_area_of_interest",
    "dens_method",
    "dens_check",
    "Nest",
    "std_param",
    "defo_range",
    "weighting",
    "ts_atmo_filter",
    "ts_atmo_filter_length",
    "ts_noise_filter",
    "ts_noise_filter_length",
    "defo_method",
    "xc0",
    "yc0",
    "zc0",
    "r0",
    "r10",
    "epoch",
    "sensor",
    "coregistration_AoI_name",
    "coregistration_directory",
]
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters["track"])
asc_dsc = eval(out_parameters["asc_dsc"])
stc_min_max = eval(out_parameters["stc_min_max"])
std_param = eval(out_parameters["std_param"])

for track in range(len(tracks)):
    basedir = "{}/{}_{}_{}_t{:0>3d}/cropped_stack/".format(
        out_parameters["crop_directory"], crop_AoI_name, out_parameters["sensor"].lower(), asc_dsc[track], tracks[track]
    )

    if out_parameters["do_water_mask"] == "yes":
        filename_water_mask = (
            f"/project/caroline/Software/config/caroline-water-masks/water_mask_{AoI_name}_"
            f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}.raw"
        )
    else:
        filename_water_mask = "[]"

    files = glob.glob(f"{basedir}*")
    dirs = [f for f in files if os.path.isdir(f)]
    masterdir = ""
    good_dirs = []
    for dir in dirs:
        files = glob.glob(f"{dir}/*")
        files = [f.split("/")[-1] for f in files]
        master = [f for f in files if f == "master.res"]
        if len(master) == 1:
            masterdir = eval(dir.split("/")[-1])
            good_dirs.append(masterdir)
        else:
            h2ph = [f for f in files if "h2ph" in f]
            if len(h2ph) in [1, 2]:
                good_dirs.append(eval(dir.split("/")[-1]))
    if len(good_dirs) > 0:
        startdate = min(good_dirs)
        end_date = max(good_dirs)
    else:
        # From #77 , not doing this will cause the following in multi-track starts:
        # Looping over A,B,C,D , if C has no good_dirs, the parameter file for D will not be generated
        # as the generation in C will throw an error with the min() and max() commands above
        startdate = None
        end_date = None
        print(
            "WARNING: Did not identify any properly coregistered / cropped directories! Cannot determine start and "
            "end date for DePSI, setting to None. This will crash DePSI."
        )

    # #62 -> figure out the reference point
    if out_parameters["ref_cn"][0] == "{":  # it's a dictionary
        data = eval(out_parameters["ref_cn"])
        assert (
            f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}" in data.keys()
        ), f"Cannot find {out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d} in ref_cn {data}!"
        mode = str(data[f"{out_parameters['sensor'].lower()}_{asc_dsc[track]}_t{tracks[track]:0>3d}"])
    else:
        mode = str(out_parameters["ref_cn"])

    if mode in ["independent", "[]"]:
        ref_cn = "[]"
    elif mode[0] == "[":  # hardcoded
        ref_cn = mode.replace(" ", "")  # remove spaces since Matlab doesn't like them
    elif mode == "constant":
        # find the old runs
        directories = glob.glob(
            "{}/{}_{}_{}_t{:0>3d}-*".format(
                out_parameters["depsi_directory"],
                AoI_name,
                out_parameters["sensor"].lower(),
                asc_dsc[track],
                tracks[track],
            )
        )
        ref_cn = "[]"
        if len(directories) == 0:
            # no old runs are present, so we run on mode 'independent' for the initialization
            pass
        else:
            rev_order_runs = list(sorted(directories))[::-1]  # sort and reverse them to find the most recent one
            for i in range(len(rev_order_runs)):  # loop in case one crashed. If all crashed,
                # ref_cn is defined before the if/else, and we run on mode 'independent'
                ref_file = (
                    f"{rev_order_runs[i]}/psi/{AoI_name}_{out_parameters['sensor'].lower()}_"
                    f"{asc_dsc[track]}_t{tracks[track]:0>3d}_ref_sel1.raw"
                )  # this file saves the selected reference
                if os.path.exists(ref_file):
                    ref_data = np.memmap(ref_file, mode="r", shape=(3,), dtype="float64")
                    # this outputs the reference point in [index, az, r]. We need [az,r]
                    ref_cn = f"[{int(round(ref_data[1]))},{int(round(ref_data[2]))}]"
                    break  # we found one, so we can stop

    else:
        raise ValueError(f"Expected types are dictionary, 'independent', '[]', '[az, r]', or 'constant', got {mode}")

    rf = open(f"{caroline_dir}/caroline_v{version}/files/depsi/psi/param_file.txt")
    param_file = rf.read()
    rf.close()
    param_file = param_file.format(
        depsi_AoI_name=AoI_name,
        sensor=out_parameters["sensor"].lower(),
        fill_track=f"{tracks[track]:0>3d}",
        asc_dsc=asc_dsc[track],
        processdir=basedir,
        start_date=startdate,
        stop_date=end_date,
        master_date=masterdir,
        max_mem_buffer=out_parameters["max_mem_buffer"],
        visible_plots=out_parameters["visible_plots"],
        detail_plots=out_parameters["detail_plots"],
        processing_groups=out_parameters["processing_groups"],
        run_mode=out_parameters["run_mode"],
        exclude_date=out_parameters["exclude_date"],
        az_spacing=out_parameters["az_spacing"],
        r_spacing=out_parameters["r_spacing"],
        slc_selection_input=out_parameters["slc_selection_input"],
        ifg_selection_input=out_parameters["ifg_selection_input"],
        ref_cn=ref_cn,
        Ncv=out_parameters["Ncv"],
        ps_method=out_parameters["ps_method"],
        psc_model=out_parameters["psc_model"],
        ps_model=out_parameters["ps_model"],
        final_model=out_parameters["final_model"],
        breakpoint=out_parameters["breakpoint"],
        breakpoint2=out_parameters["breakpoint2"],
        ens_coh_threshold=out_parameters["ens_coh_threshold"],
        varfac_threshold=out_parameters["varfac_threshold"],
        detrend_method=out_parameters["detrend_method"],
        output_format=out_parameters["output_format"],
        stc_min=stc_min_max[0],
        stc_max=stc_min_max[1],
        do_apriori_sidelobe_mask=out_parameters["do_apriori_sidelobe_mask"],
        do_aposteriori_sidelobe_mask=out_parameters["do_aposteriori_sidelobe_mask"],
        ref_height=out_parameters["ref_height"],
        amplitude_calibration=out_parameters["amplitude_calibration"],
        psc_selection_method=out_parameters["psc_selection_method"],
        psc_selection_gridsize=out_parameters["psc_selection_gridsize"],
        psc_threshold=out_parameters["psc_threshold"],
        max_arc_length=out_parameters["max_arc_length"],
        network_method=out_parameters["network_method"],
        Ncon=out_parameters["Ncon"],
        Nparts=out_parameters["Nparts"],
        Npsc_selections=out_parameters["Npsc_selections"],
        filename_water_mask=filename_water_mask,
        gamma_threshold=out_parameters["gamma_threshold"],
        psc_distribution=out_parameters["psc_distribution"],
        weighted_unwrap=out_parameters["weighted_unwrap"],
        livetime_threshold=out_parameters["livetime_threshold"],
        peak_tolerance=out_parameters["peak_tolerance"],
        psp_selection_method=out_parameters["psp_selection_method"],
        psp_threshold1=out_parameters["psp_threshold1"],
        psp_threshold2=out_parameters["psp_threshold2"],
        ps_eval_method=out_parameters["ps_eval_method"],
        Namp_disp_bins=out_parameters["Namp_disp_bins"],
        Ndens_iterations=out_parameters["Ndens_iterations"],
        densification_flag=out_parameters["densification_flag"],
        ps_area_of_interest=out_parameters["ps_area_of_interest"],
        dens_method=out_parameters["dens_method"],
        dens_check=out_parameters["dens_check"],
        Nest=out_parameters["Nest"],
        std_param1=std_param[0],
        std_param2=std_param[1],
        std_param3=std_param[2],
        std_param4=std_param[3],
        std_param5=std_param[4],
        std_param6=std_param[5],
        std_param7=std_param[6],
        defo_range=out_parameters["defo_range"],
        weighting=out_parameters["weighting"],
        ts_atmo_filter=out_parameters["ts_atmo_filter"],
        ts_atmo_filter_length=out_parameters["ts_atmo_filter_length"],
        ts_noise_filter=out_parameters["ts_noise_filter"],
        ts_noise_filter_length=out_parameters["ts_noise_filter_length"],
        defo_method=out_parameters["defo_method"],
        xc0=out_parameters["xc0"],
        yc0=out_parameters["yc0"],
        zc0=out_parameters["zc0"],
        r0=out_parameters["r0"],
        r10=out_parameters["r10"],
        epoch=out_parameters["epoch"],
        processor="doris_flinsar",
    )

    f = open(
        "{}/{}_{}_{}_t{:0>3d}/psi/param_file_{}_{}_t{:0>3d}.txt".format(
            out_parameters["depsi_directory"],
            AoI_name,
            out_parameters["sensor"].lower(),
            asc_dsc[track],
            tracks[track],
            AoI_name,
            asc_dsc[track],
            tracks[track],
        ),
        "w",
    )
    f.write(param_file)
    f.close()
