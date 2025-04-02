clear all
close all

addpath(genpath('../boxes/**depsi_post_version**'));
addpath(genpath('../boxes/**geocoding_version**'));
addpath(genpath('../boxes/**rdnaptrans_version**'));

%dbstop if error

param_file = 'param_file_depsi.txt';

do_read = 1;
do_hist_orig = 0;
do_plots_orig = 0;
do_param_filtering = **do_csv**;
do_hist_filt = 0;
do_plots_filt = 0;
do_interactive = 0;
do_create_final_dataset = **do_csv**;
do_plots_final = 0;
do_write_shape_csv = **do_csv**;

dlat = **dp_dlat**;
dlon = **dp_dlon**;
drdx = **dp_drdx**;
drdy = **dp_drdy**;
id_annot = '**sensor****asc_dsc****fill_track**';
file_out = '**depsi_AoI_name**_**asc_dsc**_**fill_track**';
%proj = 'wgs84';
proj = '**dp_proj**';
ref_dheight = **dp_ref_dheight**;
posteriori_scale_factor = **dp_posteriori_scale_factor**;
%crop_manual = [24461,40460,235,3434];

track = [**track**];
pred_model = **dp_pred_model**;
plot_mode = '**dp_plot_mode**';
%plot_mode = 'vector';
%do_plots_example = {'defo','height','m_atmo','ens_coh','ens_coh_local','stc','perio_amp','perio_tshift','ens_coh_filt','stc_filt','amp_disp','coef'};
do_plots = {**dp_do_plots**};
%do_plots = {'defo','height'};
fontsize = **dp_fontsize**;
markersize = **dp_markersize**;
do_print = **dp_do_print**;
output_format = **dp_output_format**;
az0 = **dp_az0**;
azN = **dp_azN**;
r0 = **dp_r0**;
rN = **dp_rN**;
result = **dp_result**;
psc_selection = **dp_psc_selection**;
%ml_az = 2;
%ml_r = 2;
ml_az = 1;
ml_r = 1;
do_remove_filtered = **dp_do_remove_filtered**;
which_sl_mask = '**dp_which_sl_mask**';
shift_to_mean = **dp_shift_to_mean**;
new_ref_cn = **dp_new_ref_cn**;
map_to_vert = **dp_map_to_vert**;
%output = {'shape','csv','shape_conv'};
%output = {'csv'};
%output = {'shape_conv'};
output = {**dp_output**};


defo_lim = **dp_defo_lim**;
height_lim = **dp_height_lim**;
ens_coh_lim = **dp_ens_coh_lim**;
ens_coh_local_lim = **dp_ens_coh_local_lim**;
stc_lim = **dp_stc_lim**;

defo_clim = [**dp_defo_clim_min** **dp_defo_clim_max**];
height_clim = [**dp_height_clim_min** **dp_height_clim_max**];
%ens_coh_clim = ens_coh_lim;
%ens_coh_local_clim = ens_coh_local_lim;
%stc_clim = stc_lim;
ens_coh_clim = **dp_ens_coh_clim**;
ens_coh_local_clim = **dp_ens_coh_local_clim**;
stc_clim = **dp_stc_clim**;


% ----------------------------------------------------------------------
% 0
% Initialize
% ----------------------------------------------------------------------

ps_post_set_globals;

if exist(param_file)
  project_id = readinput('project_id',[],param_file);
else
  error('The parameter file you specified does not exist.');
end

% #11 -> if the file exists we want to move it and create a new one
if exist([project_id '_post_project.mat'],'file');
  movefile([project_id '_post_project.mat'],[project_id '_post_project_OLD.mat']);
end
copyfile([project_id '_project.mat'],[project_id '_post_project.mat']);

load([project_id '_post_project.mat']);
Nifgs = nIfgs;
visible_plots = 'y';

[plot_id,...
 plot_xlabel,...
 plot_quan,...
 plot_cmap,...
 Nplot,...
 plot_dir,...
 sl_mask_file,...
 Nps,...
 Nresults,...
 results_id] = ps_post_initialize(which_sl_mask,...
				  Nps_atmo,...
				  Nps_defo);
ps_index = (1:Nps(result))';
rm_index = [];

if do_read
  plot_id = ps_post_read_orig_data(Nifgs,...
				   Nps,...
				   result,...
				   psc_selection,...
				   ts_noise_filter,...
				   ts_noise_filter_length,...
				   plot_id);
end

%ps_post_param_plots(ps_index);

if do_hist_orig
  fprintf(1,'\n');
  fprintf(1,['Creating histograms original data ....\n']);

  ps_post_histograms(ps_index,rm_index,'orig');
end
  
if do_plots_orig
  fprintf(1,'\n');
  fprintf(1,['Creating plots original data ....\n']);

  ps_post_plots(ps_index,rm_index,'orig');
end

if do_param_filtering
  [ps_index,...
   rm_index] = ps_post_param_filtering(ps_index,...
					   rm_index,...
					   defo_lim,...
					   height_lim,...
					   ens_coh_lim,...
					   ens_coh_local_lim,...
					   stc_lim,...
                       amp_disp_lim);
  save([project_id '_param_filtering.mat'],'ps_index','rm_index');
else
  if exist([project_id '_param_filtering.mat'])
    load([project_id '_param_filtering.mat']);
  end
end

%ps_post_param_plots(ps_index);

if do_hist_filt
  fprintf(1,'\n');
  fprintf(1,['Creating histograms filtered data ....\n']);

  ps_post_histograms(ps_index,rm_index,'filt');
end
  
if do_plots_filt
  fprintf(1,'\n');
  fprintf(1,['Creating plots filtered data ....\n']);

  ps_post_plots(ps_index,rm_index,'filt');
end

if do_interactive
  plot_mode = 'vector';
  ps_post_manual_interactive(ps_index,Btemp,Nifgs,dates);
end

if do_create_final_dataset
  ref_height = ref_height + ref_dheight;
  ps_post_create_final_dataset(ps_index,...
			       Nifgs,...
			       dates,...
			       Btemp,...
			       m2ph,...
			       dlat,...
			       dlon,...
			       proj,...
			       master_res,...
			       ref_height,...
			       crop,...
			       drdx,...
			       drdy,...
                   shift_to_mean,...
                   map_to_vert,...
                   new_ref_cn);
end

if do_plots_final
  fprintf(1,'\n');
  fprintf(1,['Creating plots final data ....\n']);

  ps_post_plots_final(ps_index,rm_index,'final');
end

if do_write_shape_csv
  ps_post_write_shape_csv(id_annot,...
			  file_out,...
			  proj,...
                          output);
end


