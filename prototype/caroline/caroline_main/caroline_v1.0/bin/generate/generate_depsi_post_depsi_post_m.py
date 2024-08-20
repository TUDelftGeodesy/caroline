from sys import argv, path
import os
path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from read_param_file import read_param_file
filename, param_file, cpath, AoI_name, version, caroline_dir = argv

search_parameters = ['depsi_directory', 'track','asc_dsc', 'depsi_post_mode', 'dp_dlat', 'dp_dlon', 'dp_drdx',
                     'dp_drdy', 'dp_proj', 'dp_ref_dheight', 'dp_posteriori_scale_factor', 'dp_pred_model', 'dp_plot_mode', 'dp_do_plots', 'dp_fontsize',
                     'dp_markersize', 'dp_do_print', 'dp_output_format', 'dp_az0', 'dp_azN', 'dp_r0', 'dp_rN', 'dp_result', 
                     'dp_psc_selection', 'dp_do_remove_filtered', 'dp_which_sl_mask', 'dp_shift_to_mean', 'dp_new_ref_cn', 
                     'dp_map_to_vert', 'dp_output', 'dp_defo_lim', 'dp_height_lim', 'dp_ens_coh_lim', 'dp_ens_coh_local_lim',
                     'dp_stc_lim', 'dp_defo_clim', 'dp_height_clim', 'dp_ens_coh_clim', 'dp_ens_coh_local_clim', 'dp_stc_clim']
out_parameters = read_param_file(cpath, param_file, search_parameters)

base_stack = open("{}/caroline_v{}/files/depsi_post/depsi_post.m".format(caroline_dir, version))
stack = base_stack.read()
base_stack.close()

tracks = eval(out_parameters['track'])
asc_dsc = eval(out_parameters['asc_dsc'])

if out_parameters['depsi_post_mode'] == 'tarball':
    do_csv = 0
elif out_parameters['depsi_post_mode'] == 'csv':
    do_csv = 1
else:
    raise ValueError("depsi_post_mode is set to {}, only know 'tarball' and 'csv'!".format(out_parameters[3]))

pred_model_raw = out_parameters['dp_pred_model']
pred_model = ''
for c in pred_model_raw:
    if c not in ' ':
        pred_model += c

do_plots_raw = out_parameters['dp_do_plots']
do_plots = ''
for c in do_plots_raw:
    if c not in '{} ':
        do_plots += c

output_raw = out_parameters['dp_output']
output = ''
for c in output_raw:
    if c not in '{} ':
        output += c

defo_clim_raw = out_parameters['dp_defo_clim']
defo_clim_min = defo_clim_raw.split(",")[0][1:].strip()
defo_clim_max = defo_clim_raw.split(",")[1][:-1].strip()

height_clim_raw = out_parameters['dp_height_clim']
height_clim_min = height_clim_raw.split(",")[0][1:].strip()
height_clim_max = height_clim_raw.split(",")[1][:-1].strip()

for track in range(len(tracks)):

    main = stack.format(AoI_name=AoI_name, asc_dsc=asc_dsc[track],fill_track="{:0>3d}".format(tracks[track]),track=tracks[track],lb="{",rb="}",
do_csv=do_csv,
dlat=out_parameters['dp_dlat'],
dlon=out_parameters['dp_dlon'],
drdx=out_parameters['dp_drdx'],
drdy=out_parameters['dp_drdy'],
proj=out_parameters['dp_proj'],
ref_dheight=out_parameters['dp_ref_dheight'],
posteriori_scale_factor=out_parameters['dp_posteriori_scale_factor'],
pred_model=pred_model,
plot_mode=out_parameters['dp_plot_mode'],
do_plots=do_plots,
fontsize=out_parameters['dp_fontsize'],
markersize=out_parameters['dp_markersize'],
do_print=out_parameters['dp_do_print'],
output_format=out_parameters['dp_output_format'],
az0=out_parameters['dp_az0'],
azN=out_parameters['dp_azN'],
r0=out_parameters['dp_r0'],
rN=out_parameters['dp_rN'],
result=out_parameters['dp_result'],
psc_selection=out_parameters['dp_psc_selection'],
do_remove_filtered=out_parameters['dp_do_remove_filtered'],
which_sl_mask=out_parameters['dp_which_sl_mask'],
shift_to_mean=out_parameters['dp_shift_to_mean'],
new_ref_cn=out_parameters['dp_new_ref_cn'],
map_to_vert=out_parameters['dp_map_to_vert'],
output=output,
defo_lim=out_parameters['dp_defo_lim'],
height_lim=out_parameters['dp_height_lim'],
ens_coh_lim=out_parameters['dp_ens_coh_lim'],
ens_coh_local_lim=out_parameters['dp_ens_coh_local_lim'],
stc_lim=out_parameters['dp_stc_lim'],
defo_clim_min=defo_clim_min,
defo_clim_max=defo_clim_max,
height_clim_min=height_clim_min,
height_clim_max=height_clim_max,
ens_coh_clim=out_parameters['dp_ens_coh_clim'],
ens_coh_local_clim=out_parameters['dp_ens_coh_local_clim'],
stc_clim=out_parameters['dp_stc_clim'])

    fw = open("{}/{}_s1_{}_t{:0>3d}/psi/depsi_post_{}_{}_t{:0>3d}.m".format(out_parameters['depsi_directory'], AoI_name, asc_dsc[track], tracks[track], AoI_name, asc_dsc[track], tracks[track]), 'w')
    fw.write(main)
    fw.close()



