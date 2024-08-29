from sys import argv, path
import os
import glob
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name, stitch_AoI_name, version, caroline_dir = argv

search_parameters = ['stitch_directory', 'track', 'asc_dsc', 'depsi_directory', 'max_mem_buffer', 'visible_plots',
                     'detail_plots', 'processing_groups', 'run_mode', 'exclude_date', 'az_spacing', 'r_spacing',
                     'slc_selection_input',
                     'ifg_selection_input', 'ref_cn', 'Ncv', 'ps_method', 'psc_model', 'ps_model', 'final_model',
                     'breakpoint', 'breakpoint2', 'ens_coh_threshold', 'varfac_threshold', 'detrend_method',
                     'output_format', 'stc_min_max',
                     'do_apriori_sidelobe_mask', 'do_aposteriori_sidelobe_mask', 'ref_height', 'amplitude_calibration',
                     'psc_selection_method', 'psc_selection_gridsize', 'psc_threshold', 'max_arc_length',
                     'network_method', 'Ncon',
                     'Nparts', 'Npsc_selections', 'filename_water_mask', 'gamma_threshold', 'psc_distribution',
                     'weighted_unwrap', 'livetime_threshold', 'peak_tolerance', 'psp_selection_method',
                     'psp_threshold1', 'psp_threshold2',
                     'ps_eval_method', 'Namp_disp_bins', 'Ndens_iterations', 'densification_flag',
                     'ps_area_of_interest', 'dens_method', 'dens_check', 'Nest', 'std_param', 'defo_range', 'weighting',
                     'ts_atmo_filter', 'ts_atmo_filter_length',
                     'ts_noise_filter', 'ts_noise_filter_length', 'defo_method', 'xc0', 'yc0', 'zc0', 'r0', 'r10',
                     'epoch']
out_parameters = read_param_file(cpath, param_file, search_parameters)

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])
stc_min_max = eval(out_parameters['stc_min_max'])
std_param = eval(out_parameters['std_param'])

for track in range(len(tracks)):
    basedir = "{}/{}_s1_{}_t{:0>3d}/*cropped_stack/".format(out_parameters['stitch_directory'], stitch_AoI_name,
                                                            asc_dsc[track], tracks[track])
    files = glob.glob("{}*".format(basedir))
    dirs = [f for f in files if os.path.isdir(f)]
    masterdir = ""
    good_dirs = []
    for dir in dirs:
        files = glob.glob("{}/*".format(dir))
        files = [f.split("/")[-1] for f in files]
        master = [f for f in files if f == "master.res"]
        if len(master) == 1:
            masterdir = eval(dir.split("/")[-1])
            good_dirs.append(masterdir)
        else:
            h2ph = [f for f in files if "h2ph" in f]
            if len(h2ph) == 1:
                good_dirs.append(eval(dir.split("/")[-1]))
    startdate = min(good_dirs)
    end_date = max(good_dirs)

    rf = open("{}/caroline_v{}/files/depsi/psi/param_file.txt".format(caroline_dir, version))
    param_file = rf.read()
    rf.close()
    param_file = param_file.format(depsi_AoI_name=AoI_name,
                                   stitch_AoI_name=stitch_AoI_name,
                                   fill_track="{:0>3d}".format(tracks[track]),
                                   asc_dsc=asc_dsc[track],
                                   start_date=startdate,
                                   stop_date=end_date,
                                   master_date=masterdir,
                                   stitch_dir=out_parameters['stitch_directory'],
                                   max_mem_buffer=out_parameters['max_mem_buffer'],
                                   visible_plots=out_parameters['visible_plots'],
                                   detail_plots=out_parameters['detail_plots'],
                                   processing_groups=out_parameters['processing_groups'],
                                   run_mode=out_parameters['run_mode'],
                                   exclude_date=out_parameters['exclude_date'],
                                   az_spacing=out_parameters['az_spacing'],
                                   r_spacing=out_parameters['r_spacing'],
                                   slc_selection_input=out_parameters['slc_selection_input'],
                                   ifg_selection_input=out_parameters['ifg_selection_input'],
                                   ref_cn=out_parameters['ref_cn'],
                                   Ncv=out_parameters['Ncv'],
                                   ps_method=out_parameters['ps_method'],
                                   psc_model=out_parameters['psc_model'],
                                   ps_model=out_parameters['ps_model'],
                                   final_model=out_parameters['final_model'],
                                   breakpoint=out_parameters['breakpoint'],
                                   breakpoint2=out_parameters['breakpoint2'],
                                   ens_coh_threshold=out_parameters['ens_coh_threshold'],
                                   varfac_threshold=out_parameters['varfac_threshold'],
                                   detrend_method=out_parameters['detrend_method'],
                                   output_format=out_parameters['output_format'],
                                   stc_min=stc_min_max[0], stc_max=stc_min_max[1],
                                   do_apriori_sidelobe_mask=out_parameters['do_apriori_sidelobe_mask'],
                                   do_aposteriori_sidelobe_mask=out_parameters['do_aposteriori_sidelobe_mask'],
                                   ref_height=out_parameters['ref_height'],
                                   amplitude_calibration=out_parameters['amplitude_calibration'],
                                   psc_selection_method=out_parameters['psc_selection_method'],
                                   psc_selection_gridsize=out_parameters['psc_selection_gridsize'],
                                   psc_threshold=out_parameters['psc_threshold'],
                                   max_arc_length=out_parameters['max_arc_length'],
                                   network_method=out_parameters['network_method'],
                                   Ncon=out_parameters['Ncon'],
                                   Nparts=out_parameters['Nparts'],
                                   Npsc_selections=out_parameters['Npsc_selections'],
                                   filename_water_mask=out_parameters['filename_water_mask'],
                                   gamma_threshold=out_parameters['gamma_threshold'],
                                   psc_distribution=out_parameters['psc_distribution'],
                                   weighted_unwrap=out_parameters['weighted_unwrap'],
                                   livetime_threshold=out_parameters['livetime_threshold'],
                                   peak_tolerance=out_parameters['peak_tolerance'],
                                   psp_selection_method=out_parameters['psp_selection_method'],
                                   psp_threshold1=out_parameters['psp_threshold1'],
                                   psp_threshold2=out_parameters['psp_threshold2'],
                                   ps_eval_method=out_parameters['ps_eval_method'],
                                   Namp_disp_bins=out_parameters['Namp_disp_bins'],
                                   Ndens_iterations=out_parameters['Ndens_iterations'],
                                   densification_flag=out_parameters['densification_flag'],
                                   ps_area_of_interest=out_parameters['ps_area_of_interest'],
                                   dens_method=out_parameters['dens_method'],
                                   dens_check=out_parameters['dens_check'],
                                   Nest=out_parameters['Nest'],
                                   std_param1=std_param[0], std_param2=std_param[1], std_param3=std_param[2],
                                   std_param4=std_param[3], std_param5=std_param[4], std_param6=std_param[5],
                                   std_param7=std_param[6],
                                   defo_range=out_parameters['defo_range'],
                                   weighting=out_parameters['weighting'],
                                   ts_atmo_filter=out_parameters['ts_atmo_filter'],
                                   ts_atmo_filter_length=out_parameters['ts_atmo_filter_length'],
                                   ts_noise_filter=out_parameters['ts_noise_filter'],
                                   ts_noise_filter_length=out_parameters['ts_noise_filter_length'],
                                   defo_method=out_parameters['defo_method'],
                                   xc0=out_parameters['xc0'],
                                   yc0=out_parameters['yc0'],
                                   zc0=out_parameters['zc0'],
                                   r0=out_parameters['r0'],
                                   r10=out_parameters['r10'],
                                   epoch=out_parameters['epoch'])

    f = open(
        "{}/{}_s1_{}_t{:0>3d}/psi/param_file_{}_{}_t{:0>3d}.txt".format(out_parameters['depsi_directory'], AoI_name, asc_dsc[track],
                                                                        tracks[track], AoI_name, asc_dsc[track],
                                                                        tracks[track]), "w")
    f.write(param_file)
    f.close()
