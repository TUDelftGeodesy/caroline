clear all
close all

addpath(genpath('../boxes/depsi_post_v2.1.4.0'));
addpath(genpath('../boxes/geocoding_v0.9'));
addpath(genpath('../boxes/rdnaptrans'));

%dbstop if error

param_file = 'param_file_{AoI_name}_{asc_dsc}_t{fill_track}.txt';

do_read = 1;
do_hist_orig = 0;
do_plots_orig = 0;
do_param_filtering = {do_csv};
do_hist_filt = 0;
do_plots_filt = 0;
do_interactive = 0;
do_create_final_dataset = {do_csv};
do_plots_final = 0;
do_write_shape_csv = {do_csv};

dlat = {dlat};
dlon = {dlon};
drdx = {drdx};
drdy = {drdy};
id_annot = 'S1{asc_dsc}{fill_track}';
file_out = '{AoI_name}_{asc_dsc}_{fill_track}';
%proj = 'wgs84';
proj = '{proj}';
ref_dheight = {ref_dheight};
posteriori_scale_factor = {posteriori_scale_factor};
%crop_manual = [24461,40460,235,3434];

track = [{track}];
pred_model = {pred_model};
plot_mode = '{plot_mode}';
%plot_mode = 'vector';
%do_plots_example = {lb}'defo','height','m_atmo','ens_coh','ens_coh_local','stc','perio_amp','perio_tshift','ens_coh_filt','stc_filt','amp_disp','coef'{rb};
do_plots = {lb}{do_plots}{rb};
%do_plots = {lb}'defo','height'{rb};
fontsize = {fontsize};
markersize = {markersize};
do_print = {do_print};
output_format = {output_format};
az0 = {az0};
azN = {azN};
r0 = {r0};
rN = {rN};
result = {result};
psc_selection = {psc_selection};
%ml_az = 2;
%ml_r = 2;
ml_az = 1;
ml_r = 1;
do_remove_filtered = {do_remove_filtered};
which_sl_mask = '{which_sl_mask}';
shift_to_mean = {shift_to_mean};
new_ref_cn = {new_ref_cn};
map_to_vert = {map_to_vert};
%output = {lb}'shape','csv','shape_conv'{rb};
%output = {lb}'csv'{rb};
%output = {lb}'shape_conv'{rb};
output = {lb}{output}{rb};


defo_lim = {defo_lim};
height_lim = {height_lim};
ens_coh_lim = {ens_coh_lim};
ens_coh_local_lim = {ens_coh_local_lim};
stc_lim = {stc_lim};

defo_clim = [{defo_clim_min} {defo_clim_max}];
height_clim = [{height_clim_min} {height_clim_max}];
%ens_coh_clim = ens_coh_lim;
%ens_coh_local_clim = ens_coh_local_lim;
%stc_clim = stc_lim;
ens_coh_clim = {ens_coh_clim};
ens_coh_local_clim = {ens_coh_local_clim};
stc_clim = {stc_clim};


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


