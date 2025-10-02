function ps_post_create_final_dataset(ps_index,Nifgs,dates,Btemp,m2ph,dlat,dlon,proj,master_res,ref_height,crop,drdx,drdy,shift_to_mean,map_to_vert,new_ref_cn)

ps_post_set_globals;

MAXITER = 100;
CRITERPOS = 1e-8;
ellipsoid = [6378137.0 6356752.3141]; %wgs84

if exist([project_id '_ps_perio_amp.mat']);
  perio_flag = 1;
 else
  perio_flag = 0;
end

if exist([project_id '_ps_amp_disp_valid.mat']);
  valid_flag = 1;
 else
  valid_flag = 0;
end

N = length(ps_index);
Nslc = Nifgs + 1;

%calculate master index
datenums = datenum(dates);
[dummy,sort_index] = sort(datenums);
master_index = find(sort_index==Nifgs+1);
dates_new = dates(sort_index,:);

%read data
load([project_id '_ps_defo.mat']);
load([project_id '_ps_height.mat']);
load([project_id '_ps_ens_coh.mat']);
load([project_id '_ps_ens_coh_local.mat']);
load([project_id '_ps_stc.mat']);
load([project_id '_ps_az.mat']);
load([project_id '_ps_r.mat']);
load([project_id '_ps_lat.mat']);
load([project_id '_ps_lon.mat']);
load([project_id '_ps_h.mat']);
%load([project_id '_ps_rdx.mat']);
%load([project_id '_ps_rdy.mat']);
%load([project_id '_ps_rdh.mat']);
load([project_id '_ps_sig2hat.mat']);
load([project_id '_ps_inc_angle.mat']);
load([project_id '_ps_amp_disp.mat']);

if valid_flag
  load([project_id '_ps_amp_disp_valid.mat']);
end

if perio_flag
  load([project_id '_ps_perio1.mat']);
  load([project_id '_ps_perio2.mat']);
  load([project_id '_ps_perio_amp.mat']);
  load([project_id '_ps_perio_tshift.mat']);
end

ps_id = ps_index;
ps_defo = ps_defo(ps_index);
ps_height = ps_height(ps_index);
ps_ens_coh = ps_ens_coh(ps_index);
ps_ens_coh_local = ps_ens_coh_local(ps_index);
ps_stc = ps_stc(ps_index);
ps_az = ps_az(ps_index);
ps_r = ps_r(ps_index);
ps_lat = ps_lat(ps_index);
ps_lon = ps_lon(ps_index);
ps_h = ps_h(ps_index);
%ps_rdx = ps_rdx(ps_index);
%ps_rdy = ps_rdy(ps_index);
%ps_rdh = ps_rdh(ps_index);
ps_sig2hat = ps_sig2hat(ps_index);
ps_inc_angle = ps_inc_angle(ps_index);
ps_amp_disp = ps_amp_disp(ps_index);

if valid_flag
  ps_amp_disp_valid = ps_amp_disp_valid(ps_index);
end

if perio_flag
  ps_perio1 = ps_perio1(ps_index);
  ps_perio2 = ps_perio2(ps_index);
  ps_perio_amp = ps_perio_amp(ps_index);
  ps_perio_tshift = ps_perio_tshift(ps_index);
end

ps_ts_fid = fopen([project_id subcrop_id '_ps_ts.raw'],'r');
ps_ts = NaN(N,Nifgs);

for v = 1:N
  start = (ps_index(v)-1)*Nifgs*4;
  status_ts = fseek(ps_ts_fid,start,'bof');
  ps_ts(v,:) = fread(ps_ts_fid,Nifgs,'single');
end

fclose(ps_ts_fid);
ps_ts = ps_ts*1000; %mm

ps_ts_new = [ps_ts(:,1:master_index-1) zeros(N,1) ps_ts(:,master_index:end)];
ps_ts_new = ps_ts_new - repmat(ps_ts_new(:,1),1,Nifgs+1);

Btemp_new = [Btemp(1:master_index-1);0;Btemp(master_index:end)];

if perio_flag
  A = [Btemp_new sin(2*pi*Btemp_new) (cos(2*pi*Btemp_new)-1) ones(size(Btemp_new))];
else
  A = [Btemp_new ones(size(Btemp_new))];
end

rhs = inv(A'*A)*A';

xhat = (rhs*ps_ts_new')';
ps_defo_new = xhat(:,1);

if perio_flag
  ps_perio1_new = xhat(:,2);
  ps_perio2_new = xhat(:,3);
  ps_perio_tshift_new = atan2(-ps_perio2_new,ps_perio1_new)/(2*pi);
  ps_perio_amp_new = ps_perio1_new./cos(2*pi*ps_perio_tshift_new);
end

ehat = ps_ts_new-(A*xhat')';
ehat(:,master_index) = []; % remove, otherwise influences ps_std,
                           % ps_ens_coh_coh

ps_std = std(ehat,0,2);
ps_ens_coh_new = abs((1/Nifgs)*sum(exp(i*(m2ph*ehat/1000)),2));

Qxhat = inv(A'*A);

ps_std_lin = sqrt(ps_std.^2*Qxhat(1,1));

if valid_flag

  ps_amp_valid_fid = fopen([project_id '_ps_amp_valid.raw'],'r');
  ps_phase_valid_fid = fopen([project_id '_ps_phase_valid.raw'],'r');
  ps_h2ph_valid_fid = fopen([project_id '_ps_h2ph_valid.raw'],'r');
  ps_atmo_valid_fid = fopen([project_id '_ps_atmo_valid.raw'],'r');
  ps_atmo_slc_valid_fid = fopen([project_id '_ps_atmo_slc_valid.raw'],'r');
  ps_ts_valid_fid = fopen([project_id '_ps_ts_valid.raw'],'r');
  ps_phase_res_valid_fid = fopen([project_id '_ps_phase_res_valid.raw'],'r');

  ps_phase_valid = NaN(N,Nifgs);
  ps_h2ph_valid = NaN(N,Nifgs);
  ps_atmo_valid = NaN(N,Nifgs);
  ps_ts_valid = NaN(N,Nifgs);
  ps_phase_res_valid = NaN(N,Nifgs);
  ps_amp_valid = NaN(N,Nslc);
  ps_atmo_slc_valid = NaN(N,Nslc);

  for v = 1:N
    start_Nifgs = (ps_index(v)-1)*Nifgs*4;
    start_Nslc = (ps_index(v)-1)*Nslc*4;

    status_phase = fseek(ps_phase_valid_fid,start_Nifgs,'bof');
    status_h2ph = fseek(ps_h2ph_valid_fid,start_Nifgs,'bof');
    status_atmo = fseek(ps_atmo_valid_fid,start_Nifgs,'bof');
    status_ts_valid = fseek(ps_ts_valid_fid,start_Nifgs,'bof');
    status_phase_res = fseek(ps_phase_res_valid_fid,start_Nifgs,'bof');
    status_amp = fseek(ps_amp_valid_fid,start_Nslc,'bof');
    status_atmo_slc = fseek(ps_atmo_slc_valid_fid,start_Nslc,'bof');

    ps_phase_valid(v,:) = fread(ps_phase_valid_fid,Nifgs,'single');
    ps_h2ph_valid(v,:) = fread(ps_h2ph_valid_fid,Nifgs,'single');
    ps_atmo_valid(v,:) = fread(ps_atmo_valid_fid,Nifgs,'single');
    ps_ts_valid(v,:) = fread(ps_ts_valid_fid,Nifgs,'single');
    ps_phase_res_valid(v,:) = fread(ps_phase_res_valid_fid,Nifgs,'single');
    ps_amp_valid(v,:) = fread(ps_amp_valid_fid,Nslc,'single');
    ps_atmo_slc_valid(v,:) = fread(ps_atmo_slc_valid_fid,Nslc,'single');

  end

  fclose(ps_amp_valid_fid);
  fclose(ps_phase_valid_fid);
  fclose(ps_h2ph_valid_fid);
  fclose(ps_atmo_valid_fid);
  fclose(ps_atmo_slc_valid_fid);
  fclose(ps_ts_valid_fid);
  fclose(ps_phase_res_valid_fid);

  ps_ts_valid = ps_ts_valid*1000; %mm

  ps_ts_valid_new = [ps_ts_valid(:,1:master_index-1) zeros(N,1) ps_ts_valid(:,master_index:end)];
  ps_ts_valid_new = ps_ts_valid_new - repmat(ps_ts_valid_new(:,1),1,Nifgs+1);
  ps_phase_valid_new = [ps_phase_valid(:,1:master_index-1) zeros(N,1) ps_phase_valid(:,master_index:end)];
  ps_phase_valid_new = mod(ps_phase_valid_new - repmat(ps_phase_valid_new(:,1),1,Nifgs+1)+pi,2*pi)-pi;
  ps_h2ph_valid_new = [ps_h2ph_valid(:,1:master_index-1) zeros(N,1) ps_h2ph_valid(:,master_index:end)];
  ps_h2ph_valid_new = ps_h2ph_valid_new - repmat(ps_h2ph_valid_new(:,1),1,Nifgs+1);
  ps_atmo_valid_new = [ps_atmo_valid(:,1:master_index-1) zeros(N,1) ps_atmo_valid(:,master_index:end)];
  ps_atmo_valid_new = ps_atmo_valid_new - repmat(ps_atmo_valid_new(:,1),1,Nifgs+1);
  ps_phase_res_valid_new = [ps_phase_res_valid(:,1:master_index-1) zeros(N,1) ps_phase_res_valid(:,master_index:end)];
  ps_phase_res_valid_new = mod(ps_phase_res_valid_new - repmat(ps_phase_res_valid_new(:,1),1,Nifgs+1)+pi,2*pi)-pi;

end


%map to vert
if map_to_vert
  ps_defo_vert = ps_defo_new./cos(ps_inc_angle*pi/180);
  ps_ts_vert = ps_ts_new./repmat(cos(ps_inc_angle*pi/180),1,Nifgs+1);
  ps_std_vert = ps_std./cos(ps_inc_angle*pi/180);
  ps_std_lin_vert = ps_std_lin./cos(ps_inc_angle*pi/180);
  ps_stc_vert = ps_stc./cos(ps_inc_angle*pi/180);
else
  ps_defo_vert = ps_defo_new;
  ps_ts_vert = ps_ts_new;
  ps_std_vert = ps_std;
  ps_std_lin_vert = ps_std_lin;
  ps_stc_vert = ps_stc;
end

if shift_to_mean & ~isempty(new_ref_cn)
  error('You cannot reference to the mean and to a specific point simultaneously.');

elseif shift_to_mean
  mean_defo = mean(ps_defo_vert);
  ps_defo_vert_orig = ps_defo_vert;
  ps_ts_vert_orig = ps_ts_vert;
  ps_defo_vert = ps_defo_vert-mean_defo;
  ps_ts_vert = ps_ts_vert-repmat((A(:,1)*mean_defo)',size(ps_ts_vert,1),1);

elseif ~isempty(new_ref_cn)
  refIdx = find(ps_az==new_ref_cn(1) & ps_r==new_ref_cn(2));
  if isempty(refIdx)
    error('The reference point coordinates you specified are not within the dataset.');
  end

  ps_defo_vert = ps_defo_vert - ps_defo_vert(refIdx);
  ps_ts_vert = ps_ts_vert - repmat(ps_ts_vert(refIdx,:),size(ps_ts_vert,1),1);

end

%for v = 1:3
%  ps_defo_vert_orig(v)
%  ps_defo_vert(v)
%  figure; hold on
%  plot(A(:,1),ps_ts_vert_orig(v,:),'r');
%  plot(A(:,1),ps_ts_vert(v,:),'g');
%end


if perio_flag
  if map_to_vert
    ps_perio_amp_vert = ps_perio_amp_new./cos(ps_inc_angle*pi/180);
  else
    ps_perio_amp_vert = ps_perio_amp_new;
  end
end

%if do_geocoding
%
%  [container,orbit_state] = metadataNew(master_res);
%  linelo = crop(1);
%  pixlo = crop(3);
%
%  line = ps_az+linelo-1;
%  pixel = ps_r+pixlo-1;
%  height = ps_height+ref_height;
%
%  [norm_orbit,norm_orbit_line] = intrp_orbit(line,container,orbit_state);
%
%  [xyz] = lph2xyz(line,pixel,height,ellipsoid,container,...
%                  norm_orbit_line,MAXITER,CRITERPOS);
%
%
%  phi_lam_h = xyz2ell(xyz,ellipsoid);
%
%  ps_lat = phi_lam_h(:,1);
%  ps_lon = phi_lam_h(:,2);
%  ps_h = phi_lam_h(:,3);
%
%end

ps_lat = ps_lat+dlat;
ps_lon = ps_lon+dlon;

if strcmp(proj,'rd')
  rdnap = etrs2rdnap([ps_lat*pi/180 ps_lon*pi/180 ps_h],'PLH');
  ps_rdx = rdnap(:,1);
  ps_rdy = rdnap(:,2);
  ps_rdh = rdnap(:,3);
else
  ps_rdx = NaN(N,1);
  ps_rdy = NaN(N,1);
  ps_rdh = NaN(N,1);
end

if sum([abs(drdx) abs(drdy)])~=0;
  ps_rdx = ps_rdx + drdx;
  ps_rdy = ps_rdy + drdy;

  [plh] = rdnap2etrs([ps_rdx ps_rdy ps_rdh],'PLH');

  ps_lat = plh(:,1)*180/pi;
  ps_lon = plh(:,2)*180/pi;
  ps_h = plh(:,3);
end

%figure;
%scatter(ps_rdx,ps_rdy,5,ps_defo_vert_orig);caxis([-10 10]);colorbar
%figure;
%scatter(ps_rdx,ps_rdy,5,ps_defo_vert);caxis([-10 10]);colorbar



save([project_id subcrop_id '_final_data_set.mat'],...
     'ps_id',...
     'ps_az',...
     'ps_r',...
     'ps_lat',...
     'ps_lon',...
     'ps_h',...
     'ps_rdx',...
     'ps_rdy',...
     'ps_rdh',...
     'ps_height',...
     'ps_amp_disp',...
     'ps_inc_angle',...
     'ps_defo_vert',...
     'ps_std_vert',...
     'ps_std_lin_vert',...
     'ps_ens_coh_new',...
     'ps_ens_coh_local',...
     'ps_stc_vert',...
     'ps_ts_vert',...
     'Btemp_new',...
     'dates_new',...
     'm2ph',...
     'map_to_vert',...
     'shift_to_mean',...
     'new_ref_cn','-v7.3');

if perio_flag
  save([project_id subcrop_id '_final_data_set.mat'],...
       'ps_perio_amp_vert',...
       'ps_perio_tshift_new',...
       '-append','-v7.3');
end

if valid_flag
  save([project_id subcrop_id '_final_data_set.mat'],...
       'ps_ts_valid_new',...
       'ps_phase_valid_new',...
       'ps_h2ph_valid_new',...
       'ps_atmo_valid_new',...
       'ps_phase_res_valid_new',...
       'ps_amp_valid',...
       'ps_atmo_slc_valid',...
       '-append','-v7.3');
end
