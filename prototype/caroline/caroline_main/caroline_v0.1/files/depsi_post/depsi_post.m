clear all
close all

addpath(genpath('../boxes/depsi_post_v2.1.2.0'));
addpath(genpath('../boxes/geocoding_v0.9'));
addpath(genpath('~/matlab/rdnaptrans'));

%dbstop if error

param_file = 'param_file_{AoI_name}_{asc_dsc}_t{fill_track}.txt';

do_read = 1;
do_hist_orig = 0;
do_plots_orig = 0;
do_param_filtering = 0;
do_hist_filt = 0;
do_plots_filt = 0;
do_interactive = 0;
do_create_final_dataset = 0;
do_plots_final = 0;
do_write_shape_csv = 0;

dlat = 0;
dlon = 0;
drdx = 0;
drdy = 0;
id_annot = 'S1{asc_dsc}{fill_track}';
file_out = '{AoI_name}_{asc_dsc}_{fill_track}';
%proj = 'wgs84';
proj = 'rd';
ref_dheight = 0;
posteriori_scale_factor = 1;
%crop_manual = [24461,40460,235,3434];

track = [{track}];
pred_model = [1,3,5];
plot_mode = 'raster';
%plot_mode = 'vector';
%do_plots_example = {lb}'defo','height','m_atmo','ens_coh','ens_coh_local','stc','perio_amp','perio_tshift','ens_coh_filt','stc_filt','amp_disp','coef'{rb};
do_plots = {lb}'defo','height','ens_coh','ens_coh_local','stc','amp_disp'{rb};
%do_plots = {lb}'defo','height'{rb};
fontsize = 16;
markersize = 1;
do_print = 1;
output_format = 1;
az0 = [];
azN = [];
r0 = [];
rN = [];
result = 1;
psc_selection = 1;
%ml_az = 2;
%ml_r = 2;
ml_az = 1;
ml_r = 1;
do_remove_filtered = 0;
which_sl_mask = 'apriori';
shift_to_mean = 1;
new_ref_cn = [];
map_to_vert = 1;
%output = {lb}'shape','csv','shape_conv'{rb};
%output = {lb}'csv'{rb};
%output = {lb}'shape_conv'{rb};
output = {lb}'shape','csv','csv_web_portal','matlab'{rb};


defo_lim = [];
height_lim = [];
ens_coh_lim = 0.5;
ens_coh_local_lim = 0.6;
stc_lim = 8;

defo_clim = [-10 10];
height_clim = [-20 20];
%ens_coh_clim = ens_coh_lim;
%ens_coh_local_clim = ens_coh_local_lim;
%stc_clim = stc_lim;
ens_coh_clim = 0;
ens_coh_local_clim = 0;
stc_clim = 20;


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

if ~exist([project_id '_post_project.mat'],'file');
  copyfile([project_id '_project.mat'],[project_id '_post_project.mat']);
end

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


