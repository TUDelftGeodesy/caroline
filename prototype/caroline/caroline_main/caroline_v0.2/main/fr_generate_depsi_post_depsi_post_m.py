from sys import argv
filename, param_file, cpath, AoI_name, version, caroline_dir = argv


fp = open("{}/{}".format(cpath, param_file))
parameters = fp.read().split("\n")
fp.close()

search_parameters = ['depsi_directory', 'track','asc_dsc', 'depsi_post_mode', 'dp_dlat', 'dp_dlon', 'dp_drdx',
                     'dp_drdy', 'dp_proj', 'dp_ref_dheight', 'dp_posteriori_scale_factor', 'dp_pred_model', 'dp_plot_mode', 'dp_do_plots', 'dp_fontsize',
                     'dp_markersize', 'dp_do_print', 'dp_output_format', 'dp_az0', 'dp_azN', 'dp_r0', 'dp_rN', 'dp_result', 
                     'dp_psc_selection', 'dp_do_remove_filtered', 'dp_which_sl_mask', 'dp_shift_to_mean', 'dp_new_ref_cn', 
                     'dp_map_to_vert', 'dp_output', 'dp_defo_lim', 'dp_height_lim', 'dp_ens_coh_lim', 'dp_ens_coh_local_lim',
                     'dp_stc_lim', 'dp_defo_clim', 'dp_height_clim', 'dp_ens_coh_clim', 'dp_ens_coh_local_clim', 'dp_stc_clim']
out_parameters = []

for param in search_parameters:
    for p in parameters:
        if p.split("=")[0].strip() == param:
            do = p.split("=")[1]
            if "#" in do:
                do = do.split("#")[0]
            do = do.strip().strip("'").strip('"')
            out_parameters.append(do)
            break

base_stack = open("{}/caroline_v{}/files/depsi_post/depsi_post.m".format(caroline_dir, version))
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters[1])
asc_dsc = eval(out_parameters[2])

if out_parameters[3] == 'tarball':
    do_csv = 0
elif out_parameters[3] == 'csv':
    do_csv = 1
else:
    raise ValueError("depsi_post_mode is set to {}, only know 'tarball' and 'csv'!".format(out_parameters[3]))

pred_model_raw = out_parameters[11]
pred_model = ''
for c in pred_model_raw:
    if c not in ' ':
        pred_model += c

do_plots_raw = out_parameters[13]
do_plots = ''
for c in do_plots_raw:
    if c not in '{} ':
        do_plots += c

output_raw = out_parameters[29]
output = ''
for c in output_raw:
    if c not in '{} ':
        output += c

defo_clim_raw = out_parameters[35]
defo_clim_min = defo_clim_raw.split(",")[0][1:].strip()
defo_clim_max = defo_clim_raw.split(",")[1][:-1].strip()

height_clim_raw = out_parameters[36]
height_clim_min = height_clim_raw.split(",")[0][1:].strip()
height_clim_max = height_clim_raw.split(",")[1][:-1].strip()

for track in range(len(tracks)):

    main = stack.format(AoI_name=AoI_name, asc_dsc=asc_dsc[track],fill_track="{:0>3d}".format(tracks[track]),track=tracks[track],lb="{",rb="}",
do_csv=do_csv,
dlat=out_parameters[4],
dlon=out_parameters[5],
drdx=out_parameters[6],
drdy=out_parameters[7],
proj=out_parameters[8],
ref_dheight=out_parameters[9],
posteriori_scale_factor=out_parameters[10],
pred_model=pred_model,
plot_mode=out_parameters[12],
do_plots=do_plots,
fontsize=out_parameters[14],
markersize=out_parameters[15],
do_print=out_parameters[16],
output_format=out_parameters[17],
az0=out_parameters[18],
azN=out_parameters[19],
r0=out_parameters[20],
rN=out_parameters[21],
result=out_parameters[22],
psc_selection=out_parameters[23],
do_remove_filtered=out_parameters[24],
which_sl_mask=out_parameters[25],
shift_to_mean=out_parameters[26],
new_ref_cn=out_parameters[27],
map_to_vert=out_parameters[28],
output=output,
defo_lim=out_parameters[30],
height_lim=out_parameters[31],
ens_coh_lim=out_parameters[32],
ens_coh_local_lim=out_parameters[33],
stc_lim=out_parameters[34],
defo_clim_min=defo_clim_min,
defo_clim_max=defo_clim_max,
height_clim_min=height_clim_min,
height_clim_max=height_clim_max,
ens_coh_clim=out_parameters[37],
ens_coh_local_clim=out_parameters[38],
stc_clim=out_parameters[39])

    fw = open("{}/{}_s1_{}_t{:0>3d}/psi/depsi_post_{}_{}_t{:0>3d}.m".format(out_parameters[0], AoI_name, asc_dsc[track], tracks[track], AoI_name, asc_dsc[track], tracks[track]), 'w')
    fw.write(main)
    fw.close()



