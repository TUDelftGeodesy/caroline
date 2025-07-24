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

dlat = **depsi_post:depsi_post-settings:dlat**;
dlon = **depsi_post:depsi_post-settings:dlon**;
drdx = **depsi_post:depsi_post-settings:drdx**;
drdy = **depsi_post:depsi_post-settings:drdy**;
id_annot = '**general:input-data:sensor****asc_dsc****fill_track**';
file_out = '**depsi:general:AoI-name**_**asc_dsc**_**fill_track**';
%proj = 'wgs84';
proj = '**depsi_post:depsi_post-settings:proj**';
ref_dheight = **depsi_post:depsi_post-settings:ref-dheight**;
posteriori_scale_factor = **depsi_post:depsi_post-settings:posteriori-scale-factor**;
%crop_manual = [24461,40460,235,3434];

track = [**track**];
pred_model = **depsi_post:depsi_post-settings:pred-model**;
plot_mode = '**depsi_post:depsi_post-settings:plot-mode**';
%plot_mode = 'vector';
%do_plots_example = {'defo','height','m_atmo','ens_coh','ens_coh_local','stc','perio_amp','perio_tshift','ens_coh_filt','stc_filt','amp_disp','coef'};
do_plots = {**depsi_post:depsi_post-settings:do-plots**};
%do_plots = {'defo','height'};
fontsize = **depsi_post:depsi_post-settings:fontsize**;
markersize = **depsi_post:depsi_post-settings:markersize**;
do_print = **depsi_post:depsi_post-settings:do-print**;
output_format = **depsi_post:depsi_post-settings:output-format**;
az0 = **depsi_post:depsi_post-settings:az0**;
azN = **depsi_post:depsi_post-settings:azN**;
r0 = **depsi_post:depsi_post-settings:r0**;
rN = **depsi_post:depsi_post-settings:rN**;
result = **depsi_post:depsi_post-settings:result**;
psc_selection = **depsi_post:depsi_post-settings:psc-selection**;
%ml_az = 2;
%ml_r = 2;
ml_az = 1;
ml_r = 1;
do_remove_filtered = **depsi_post:depsi_post-settings:do-remove-filtered**;
which_sl_mask = '**depsi_post:depsi_post-settings:which-sl-mask**';
shift_to_mean = **depsi_post:depsi_post-settings:shift-to-mean**;
new_ref_cn = **depsi_post:depsi_post-settings:new-ref-cn**;
map_to_vert = **depsi_post:depsi_post-settings:map-to-vert**;
%output = {'shape','csv','shape_conv'};
%output = {'csv'};
%output = {'shape_conv'};
output = {**depsi_post:depsi_post-settings:output**};


defo_lim = **depsi_post:depsi_post-settings:defo-lim**;
height_lim = **depsi_post:depsi_post-settings:height-lim**;
ens_coh_lim = **depsi_post:depsi_post-settings:ens-coh-lim**;
ens_coh_local_lim = **depsi_post:depsi_post-settings:ens-coh-local-lim**;
stc_lim = **depsi_post:depsi_post-settings:stc-lim**;

defo_clim = [**dp_defo_clim_min** **dp_defo_clim_max**];
height_clim = [**dp_height_clim_min** **dp_height_clim_max**];
%ens_coh_clim = ens_coh_lim;
%ens_coh_local_clim = ens_coh_local_lim;
%stc_clim = stc_lim;
ens_coh_clim = **depsi_post:depsi_post-settings:ens-coh-clim**;
ens_coh_local_clim = **depsi_post:depsi_post-settings:ens-coh-local-clim**;
stc_clim = **depsi_post:depsi_post-settings:stc-clim**;


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


