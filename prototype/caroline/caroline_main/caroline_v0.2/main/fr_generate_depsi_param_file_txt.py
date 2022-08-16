from sys import argv
filename, param_file, cpath, AoI_name, version, caroline_dir = argv
from os import mkdir
import os
import glob

fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['stitch_directory', 'track','asc_dsc', 'depsi_directory', 'max_mem_buffer', 'visible_plots','detail_plots','processing_groups','run_mode','exclude_date','az_spacing','r_spacing','slc_selection_input',
                     'ifg_selection_input','ref_cn','Ncv','ps_method','psc_model','ps_model','final_model','breakpoint','breakpoint2','ens_coh_threshold','varfac_threshold','detrend_method','output_format','stc_min_max',
                     'do_apriori_sidelobe_mask','do_aposteriori_sidelobe_mask','ref_height','amplitude_calibration','psc_selection_method','psc_selection_gridsize','psc_threshold','max_arc_length','network_method','Ncon',
                     'Nparts','Npsc_selections','filename_water_mask','gamma_threshold','psc_distribution','weighted_unwrap','livetime_threshold','peak_tolerance','psp_selection_method','psp_threshold1','psp_threshold2',
                     'ps_eval_method','Namp_disp_bins','Ndens_iterations','densification_flag','ps_area_of_interest','dens_method','dens_check','Nest','std_param','defo_range','weighting','ts_atmo_filter','ts_atmo_filter_length',
                     'ts_noise_filter','ts_noise_filter_length','defo_method','xc0','yc0','zc0','r0','r10','epoch']
out_parameters = []

for param in search_parameters:
    found = False
    for p in parameters:
        if param in p.split("=")[0]:
            do = p.split("=")[1]
            if "#" in do:
                do = do.split("#")[0]
            do = do.strip().strip("'").strip('"')
            out_parameters.append(do)
            found = True
            break
    if not found:
        print("Parameter {} not found!!".format(param))

tracks = eval(out_parameters[1])
asc_dsc = eval(out_parameters[2])
stc_min_max = eval(out_parameters[26])
std_param = eval(out_parameters[56])

for track in range(len(tracks)):
    basedir = "{}/{}_s1_{}_t{:0>3d}/{}_cropped_stack/".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track], AoI_name)
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
        h2ph = [f for f in files if "h2ph" in f]
        if len(h2ph) == 1:
            good_dirs.append(eval(dir.split("/")[-1]))
    startdate = min(good_dirs)
    end_date = max(good_dirs)

    rf = open("{}/caroline_v{}/files/depsi/psi/param_file.txt".format(caroline_dir, version))
    param_file = rf.read()
    rf.close()
    param_file = param_file.format(AoI_name=AoI_name,
fill_track="{:0>3d}".format(tracks[track]),
asc_dsc=asc_dsc[track],
start_date=startdate,
stop_date=end_date,
master_date=masterdir,
stitch_dir=out_parameters[0],
max_mem_buffer=out_parameters[4],
visible_plots=out_parameters[5],
detail_plots=out_parameters[6],
processing_groups=out_parameters[7],
run_mode=out_parameters[8],
exclude_date=out_parameters[9],
az_spacing=out_parameters[10],
r_spacing=out_parameters[11],
slc_selection_input=out_parameters[12],
ifg_selection_input=out_parameters[13],
ref_cn=out_parameters[14],
Ncv=out_parameters[15],
ps_method=out_parameters[16],
psc_model=out_parameters[17],
ps_model=out_parameters[18],
final_model=out_parameters[19],
breakpoint=out_parameters[20],
breakpoint2=out_parameters[21],
ens_coh_threshold=out_parameters[22],
varfac_threshold=out_parameters[23],
detrend_method=out_parameters[24],
output_format=out_parameters[25],
stc_min=stc_min_max[0], stc_max=stc_min_max[1],
do_apriori_sidelobe_mask=out_parameters[27],
do_aposteriori_sidelobe_mask=out_parameters[28],
ref_height=out_parameters[29],
amplitude_calibration=out_parameters[30],
psc_selection_method=out_parameters[31],
psc_selection_gridsize=out_parameters[32],
psc_threshold=out_parameters[33],
max_arc_length=out_parameters[34],
network_method=out_parameters[35],
Ncon=out_parameters[36],
Nparts=out_parameters[37],
Npsc_selections=out_parameters[38],
filename_water_mask=out_parameters[39],
gamma_threshold=out_parameters[40],
psc_distribution=out_parameters[41],
weighted_unwrap=out_parameters[42],
livetime_threshold=out_parameters[43],
peak_tolerance=out_parameters[44],
psp_selection_method=out_parameters[45],
psp_threshold1=out_parameters[46],
psp_threshold2=out_parameters[47],
ps_eval_method=out_parameters[48],
Namp_disp_bins=out_parameters[49],
Ndens_iterations=out_parameters[50],
densification_flag=out_parameters[51],
ps_area_of_interest=out_parameters[52],
dens_method=out_parameters[53],
dens_check=out_parameters[54],
Nest=out_parameters[55],
std_param1=std_param[0],std_param2=std_param[1],std_param3=std_param[2],std_param4=std_param[3],std_param5=std_param[4],std_param6=std_param[5],std_param7=std_param[6],
defo_range=out_parameters[57],
weighting=out_parameters[58],
ts_atmo_filter=out_parameters[59],
ts_atmo_filter_length=out_parameters[60],
ts_noise_filter=out_parameters[61],
ts_noise_filter_length=out_parameters[62],
defo_method=out_parameters[63],
xc0=out_parameters[64],
yc0=out_parameters[65],
zc0=out_parameters[66],
r0=out_parameters[67],
r10=out_parameters[68],
epoch=out_parameters[69])

    f = open("{}/{}_s1_{}_t{:0>3d}/psi/param_file_{}_{}_t{:0>3d}.txt".format(out_parameters[3], AoI_name, asc_dsc[track], tracks[track], AoI_name, asc_dsc[track], tracks[track]),"w")
    f.write(param_file)
    f.close()
