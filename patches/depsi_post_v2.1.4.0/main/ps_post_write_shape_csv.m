function ps_post_write_shape_csv(id_annot,file_out,proj,output)

ps_post_set_globals;

display('Load data ...');
load([project_id subcrop_id '_final_data_set.mat']);
N = size(ps_id,1);
Nslc = size(dates_new,1);

if exist('ps_perio_amp_vert')
  perio_flag = 1;
else
  perio_flag = 0;
end

if exist([project_id '_ps_amp_disp_valid.mat']);
  valid_flag = 1;
 else
  valid_flag = 0;
end

rd_prj = 'PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]';

wgs84_prj = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]';


if find(strcmp('shape',output))
%% shape

  switch proj
    case 'rd'
     if perio_flag
       fields = { 'Geometry','X','Y','ID','Azimuth','Range','X_RD','Y_RD','H_NAP','Lat_WGS84',...
                'Lon_WGS84','H_WGS84','Inc_angle','Defo','Ampl','Tshift','Std_lin','STC','Coherence','Std' };
     else
       fields = { 'Geometry','X','Y','ID','Azimuth','Range','X_RD','Y_RD','H_NAP','Lat_WGS84',...
               'Lon_WGS84','H_WGS84','Inc_angle','Defo','Std_lin','STC','Coherence','Std' };
     end
    case 'wgs84'
      if perio_flag
        fields = { 'Geometry','Lat','Lon','ID','Azimuth','Range','X_RD','Y_RD','H_NAP','Lat_WGS84',...
                 'Lon_WGS84','H_WGS84','Inc_angle','Defo','Ampl','Tshift','Std_lin','STC','Coherence','Std' };
      else
        fields = { 'Geometry','Lat','Lon','ID','Azimuth','Range','X_RD','Y_RD','H_NAP','Lat_WGS84',...
                   'Lon_WGS84','H_WGS84','Inc_angle','Defo','Std_lin','STC','Coherence','Std' };
      end
  end

  Nfields = length(fields);

  for k = 1:Nslc
    fields{Nfields+k} = ['ts' datestr(datenum(dates_new(k,:)),'yyyymmdd')];
    if valid_flag
      fields{Nfields+k+Nslc} = ['a' datestr(datenum(dates_new(k,:)),'yyyymmdd')];
    end
  end

  display('Create shape output array ...');

  data = zeros( N, Nfields + Nslc );

  switch proj
    case 'rd'
      if perio_flag
        data(:,[2:3 5:Nfields+Nslc]) = [ps_rdx ps_rdy ps_az ps_r ps_rdx ps_rdy ps_rdh ps_lat ps_lon ...
                          ps_h ps_inc_angle ps_defo_vert ps_perio_amp_vert ps_perio_tshift_new ps_std_lin_vert ...
                          ps_stc_vert ps_ens_coh_new ps_std_vert ps_ts_vert];
      else
        data(:,[2:3 5:Nfields+Nslc]) = [ps_rdx ps_rdy ps_az ps_r ps_rdx ps_rdy ps_rdh ps_lat ps_lon ...
                          ps_h ps_inc_angle ps_defo_vert ps_std_lin_vert ps_stc_vert ...
                          ps_ens_coh_new ps_std_vert ps_ts_vert];
      end

    case 'wgs84'
      if perio_flag
        data(:,[2:3 5:Nfields+Nslc]) = [ps_lat ps_lon ps_az ps_r ps_rdx ps_rdy ps_rdh ps_lat ps_lon ...
                          ps_h ps_inc_angle ps_defo_vert ps_perio_amp_vert ps_perio_tshift_new ps_std_lin_vert ...
                          ps_stc_vert ps_ens_coh_new ps_std_vert ps_ts_vert];
      else
        data(:,[2:3 5:Nfields+Nslc]) = [ps_lat ps_lon ps_az ps_r ps_rdx ps_rdy ps_rdh ps_lat ps_lon ...
                          ps_h ps_inc_angle ps_defo_vert ps_std_lin_vert ps_stc_vert ...
                          ps_ens_coh_new ps_std_vert ps_ts_vert];
      end

  end

  if valid_flag
    data = [data ps_amp_valid];
  end

  display('Create cell ...');

  data = num2cell( data );

  for v = 1:N
    data{v,1} = 'Point';
    data{v,4} = [id_annot num2str(v,'%0.6d')];
  end

  display('Create struct ...');
  S_rd = cell2struct( data, fields, 2 );

  %shape
  display('Write shape file ...');
  switch proj
    case 'rd'
      shapewrite(S_rd,[file_out '_rd_coordinates']);
      prj_fid = fopen([file_out '_rd_coordinates.prj'],'w');
      fprintf(prj_fid,'%s',rd_prj);
      fclose(prj_fid);
    case 'wgs84'
      shapewrite(S_rd,[file_out '_wgs84_coordinates']);
      prj_fid = fopen([file_out '_wgs84_coordinates.prj'],'w');
      fprintf(prj_fid,'%s',wgs84_prj);
      fclose(prj_fid);
  end

end


if find(strcmp('shape_conv',output))
  %shape_conv
  display('Write shape file ...');
  switch proj
    case 'rd'

      ps_rdx_new = ps_rdx(~isnan(ps_rdx));
      ps_rdy_new = ps_rdy(~isnan(ps_rdy));
      ch_index = convhull(ps_rdx_new,ps_rdy_new);
      Nch = length(ch_index);

      %figure;
      %plot(ps_rdx_new(ch_index),ps_rdy_new(ch_index));

      chull = zeros(1,3);
      chull = num2cell(chull);

      chull{1} = 'Polygon';
      chull{2} = ps_rdx_new(ch_index)';
      chull{3} = ps_rdy_new(ch_index)';

      fields_ch = {'Geometry','X','Y'};
      S_ch = cell2struct( chull, fields_ch, 2 );

      shapewrite(S_ch,[file_out '_conv_hull_rd_coordinates']);
      prj_fid = fopen([file_out '_conv_hull_rd_coordinates.prj'],'w');
      fprintf(prj_fid,'%s',rd_prj);
      fclose(prj_fid);

    case 'wgs84'

      ps_lat_new = ps_lat(~isnan(ps_lat));
      ps_lon_new = ps_lon(~isnan(ps_lon));
      ch_index = convhull(ps_lat_new,ps_lon_new);
      Nch = length(ch_index);

      %figure;
      %plot(ps_lon_new(ch_index),ps_lat_new(ch_index));

      chull = zeros(1,3);
      chull = num2cell(chull);

      chull{1} = 'Polygon';
      chull{2} = ps_lat_new(ch_index)';
      chull{3} = ps_lon_new(ch_index)';

      fields_ch = {'Geometry','Lat','Lon'};
      S_ch = cell2struct( chull, fields_ch, 2 );

      shapewrite(S_ch,[file_out '_conv_hull_wgs84_coordinates']);
      prj_fid = fopen([file_out '_conv_hull_wgs84_coordinates.prj'],'w');
      fprintf(prj_fid,'%s',wgs84_prj);
      fclose(prj_fid);
  end

end

if find(strcmp('csv',output))
  % csv
  display('Write csv file ...');

  csv_fid = fopen([file_out '.csv'],'w');

  if perio_flag
    headers = {'ID','X (RD) [m]','Y (RD) [m]','H (NAP) [m]','Lat (WGS84) [deg]',...
               'Lon (WGS84) [deg]','h (WGS84) [m]','Azimuth','Range','Inc angle [deg]',...
               'Defo [mm/y]','Amplitude [mm]','Tshift [0-1]',...
               'Std linear [mm/y]','STC [mm]','Coherence [0-1]','Std [mm]'};
  else
    headers = {'ID','X (RD) [m]','Y (RD) [m]','H (NAP) [m]','Lat (WGS84) [deg]',...
               'Lon (WGS84) [deg]','h (WGS84) [m]','Azimuth','Range','Inc angle [deg]',...
               'Defo [mm/y]','Std linear [mm/y]','STC [mm]','Coherence [0-1]','Std [mm]'};
  end

  Nheaders = length(headers);

  for k = 1:Nslc
    headers{Nheaders+k} = [datestr(datenum(dates_new(k,:)),'yyyymmdd')];
    if valid_flag
      headers{Nheaders+k+Nslc} = ['a_' datestr(datenum(dates_new(k,:)),'yyyymmdd')];
    end
  end
  Nheaders = length(headers);

  for v = 1:Nheaders
    if v==Nheaders
      fprintf(csv_fid,'%s\n',char(headers(v)));
    else
      fprintf(csv_fid,'%s,',char(headers(v)));
    end
  end

  if perio_flag

    if valid_flag
      for v = 1:N
        ps_data = [ps_rdx(v) ps_rdy(v) ps_rdh(v) ps_lat(v) ps_lon(v) ps_h(v) ps_az(v) ps_r(v) ps_inc_angle(v) ...
                   ps_defo_vert(v) ps_perio_amp_vert(v) ps_perio_tshift_new(v) ps_std_lin_vert(v) ps_stc_vert(v) ...
                   ps_ens_coh_new(v) ps_std_vert(v) ps_ts_vert(v,:) ps_amp_valid(v,:)];
        fprintf(csv_fid,'%s,',[id_annot num2str(v,'%0.6d')]);
        fprintf(csv_fid,['%8.2f,%8.2f,%8.1f,%12.8f,%12.8f,%8.1f,%8.2f,%8.2f,%6.2f,%8.2f,%8.2f,%8.2f,%8.3f,%8.2f,%8.2f,%8.2f,' ...
                       repmat('%8.2f,',1,2*Nslc-1) '%8.2f\n'],ps_data);
      end
    else
        ps_data = [ps_rdx(v) ps_rdy(v) ps_rdh(v) ps_lat(v) ps_lon(v) ps_h(v) ps_az(v) ps_r(v) ps_inc_angle(v) ...
                   ps_defo_vert(v) ps_perio_amp_vert(v) ps_perio_tshift_new(v) ps_std_lin_vert(v) ps_stc_vert(v) ...
                   ps_ens_coh_new(v) ps_std_vert(v) ps_ts_vert(v,:)];
        fprintf(csv_fid,'%s,',[id_annot num2str(v,'%0.6d')]);
        fprintf(csv_fid,['%8.2f,%8.2f,%8.1f,%12.8f,%12.8f,%8.1f,%8.2f,%8.2f,%6.2f,%8.2f,%8.2f,%8.2f,%8.3f,%8.2f,%8.2f,%8.2f,' ...
                       repmat('%8.2f,',1,Nslc-1) '%8.2f\n'],ps_data);
    end
  else
    if valid_flag
      for v = 1:N
        ps_data = [ps_rdx(v) ps_rdy(v) ps_rdh(v) ps_lat(v) ps_lon(v) ps_h(v) ps_az(v) ps_r(v) ps_inc_angle(v) ...
                   ps_defo_vert(v) ps_std_lin_vert(v) ps_stc_vert(v) ps_ens_coh_new(v) ps_std_vert(v) ...
                   ps_ts_vert(v,:)  ps_amp_valid(v,:)];
        fprintf(csv_fid,'%s,',[id_annot num2str(v,'%0.6d')]);
        fprintf(csv_fid,['%8.2f,%8.2f,%8.1f,%12.8f,%12.8f,%8.1f,%8.2f,%8.2f,%6.2f,%8.2f,%8.3f,%8.2f,%8.2f,%8.2f,' ...
                       repmat('%8.2f,',1,2*Nslc-1) '%8.2f\n'],ps_data);
      end
    else
      for v = 1:N
        ps_data = [ps_rdx(v) ps_rdy(v) ps_rdh(v) ps_lat(v) ps_lon(v) ps_h(v) ps_az(v) ps_r(v) ps_inc_angle(v) ...
                   ps_defo_vert(v) ps_std_lin_vert(v) ps_stc_vert(v) ps_ens_coh_new(v) ps_std_vert(v) ps_ts_vert(v,:)];
        fprintf(csv_fid,'%s,',[id_annot num2str(v,'%0.6d')]);
        fprintf(csv_fid,['%8.2f,%8.2f,%8.1f,%12.8f,%12.8f,%8.1f,%8.2f,%8.2f,%6.2f,%8.2f,%8.3f,%8.2f,%8.2f,%8.2f,' ...
                       repmat('%8.2f,',1,Nslc-1) '%8.2f\n'],ps_data);
      end
    end
  end
  fclose(csv_fid);

end

if find(strcmp('csv_web_portal',output))
  % csv web portal
  display('Write csv web portal file ...');

  csv_fid = fopen([file_out '_portal.csv'],'w');

  headers = {'pnt_id','pnt_lat','pnt_lon','pnt_demheight','pnt_height',...
             'pnt_azimuth','pnt_range','pnt_quality','pnt_linear'};

  Nheaders = length(headers);

  for k = 1:Nslc
    headers{Nheaders+k} = ['d_' datestr(datenum(dates_new(k,:)),'yyyymmdd')];
    if valid_flag
      headers{Nheaders+k+Nslc} = ['a_' datestr(datenum(dates_new(k,:)),'yyyymmdd')];
    end
  end
  Nheaders = length(headers);

  for v = 1:Nheaders
    if v==Nheaders
      fprintf(csv_fid,'%s\n',char(headers(v)));
    else
      fprintf(csv_fid,'%s,',char(headers(v)));
    end
  end

  if valid_flag
    for v = 1:N
      ps_data = [ps_lat(v) ps_lon(v) ps_h(v) ps_h(v) ...
                 ps_az(v) ps_r(v) ps_ens_coh_local(v) 0.001*ps_defo_vert(v) 0.001*ps_ts_vert(v,:) ps_amp_valid(v,:)];
      fprintf(csv_fid,'%s,',[id_annot 'az' num2str(ps_az(v),'%0.8d') 'r' num2str(ps_r(v),'%0.8d')]);
      fprintf(csv_fid,['%12.8f,%12.8f,%8.2f,%8.2f,%8.2f,%8.2f,%4.2f,%8.4f,' ...
                       repmat('%8.4f,',1,Nslc) repmat('%8.2f,',1,Nslc-1) '%8.2f\n'],ps_data);
    end
  else
    for v = 1:N
      ps_data = [ps_lat(v) ps_lon(v) ps_h(v) ps_h(v) ...
                 ps_az(v) ps_r(v) ps_ens_coh_local(v) 0.001*ps_defo_vert(v) 0.001*ps_ts_vert(v,:)];
      fprintf(csv_fid,'%s,',[id_annot 'az' num2str(ps_az(v),'%0.8d') 'r' num2str(ps_r(v),'%0.8d')]);
      fprintf(csv_fid,['%12.8f,%12.8f,%8.2f,%8.2f,%8.2f,%8.2f,%4.2f,%8.4f,' ...
                       repmat('%8.4f,',1,Nslc-1) '%8.4f\n'],ps_data);
    end
  end

  fclose(csv_fid);

  if ~shift_to_mean
    ref_point_index = find(sum(abs(ps_ts_vert),2)==0);
  %  if length(ref_point_index)~=1
  %    error('Did not identify the reference point correctly');
  %  end
  end

  if map_to_vert
    direction = 'vertical';
  else
    direction = 'line of sight';
  end

  json_fid = fopen([file_out '_portal.json'],'w');
  fprintf(json_fid,'{\n');
  fprintf(json_fid,'\t"acquisition_period": "%s - %s",\n', datestr(datenum(dates_new(1,:)),'yyyy-mm-dd'), datestr(datenum(dates_new(Nslc,:)),'yyyy-mm-dd'));
  fprintf(json_fid,'\t"number_of_observations_in_time": %i,\n', Nslc);
  fprintf(json_fid,'\t"number_of_measurements_in_AoI": %i,\n', N);
  fprintf(json_fid,'\t"resolution": "%3.1f x %3.1f m",\n', az_spacing, r_spacing);
  fprintf(json_fid,'\t"deformation_direction": "%s",\n', direction);
  fprintf(json_fid,'\t"DEM": "SRTM",\n');
  if shift_to_mean
    fprintf(json_fid,'\t"reference_point_location": "Mean velocity",\n');
  else
    fprintf(json_fid,'\t"reference_point_location": "');
    for i = 1:length(ref_point_index)
      fprintf(json_fid,'%12.8f, %12.8f', ps_lat(ref_point_index(i)), ps_lon(ref_point_index(i)));
      if i < length(ref_point_index)
        fprintf(json_fid,' ; ');
      end
    end
    fprintf(json_fid,'",\n');
  end
  fprintf(json_fid,'\t"satellite_name": "%s",\n', sensor);
  fprintf(json_fid,'\t"satellite_incidence_angle": "%3.1f [deg]",\n', mean(ps_inc_angle));
  fprintf(json_fid,'\t"satellite_pass_direction": "%s",\n', orbit);
  fprintf(json_fid,'\t"processing_id": "",\n');
  fprintf(json_fid,'\t"DePSI_version": "DePSI",\n');
  fprintf(json_fid,'\t"description": "",\n');
  fprintf(json_fid,'\t"estimated_models_for_time_series": "linear"\n');
  fprintf(json_fid,'}');

  fclose(json_fid);
end

if ~exist([file_out '_matlab'])
  mkdir([file_out '_matlab'])
end

save([file_out '_matlab/ps_rdx.mat'],'ps_rdx');
save([file_out '_matlab/ps_rdy.mat'],'ps_rdy');
save([file_out '_matlab/ps_rdh.mat'],'ps_rdh');
save([file_out '_matlab/ps_lat.mat'],'ps_lat');
save([file_out '_matlab/ps_lon.mat'],'ps_lon');
save([file_out '_matlab/ps_h.mat'],'ps_h');
save([file_out '_matlab/ps_amp_disp.mat'],'ps_amp_disp');
save([file_out '_matlab/ps_inc_angle.mat'],'ps_inc_angle');
save([file_out '_matlab/ps_defo_vert.mat'],'ps_defo_vert');
save([file_out '_matlab/ps_std_lin_vert.mat'],'ps_std_lin_vert');
save([file_out '_matlab/ps_stc_vert.mat'],'ps_stc_vert');
ps_ens_coh = ps_ens_coh_new;
save([file_out '_matlab/ps_ps_ens_coh.mat'],'ps_ens_coh');
save([file_out '_matlab/ps_std_vert.mat'],'ps_std_vert');
save([file_out '_matlab/ps_ts_vert.mat'],'ps_ts_vert');

if perio_flag
  save([file_out '_matlab/ps_perio_amp_vert.mat'],'ps_perio_amp_vert');
  ps_perio_tshift = ps_perio_tshift_new;
  save([file_out '_matlab/ps_perio_tshift.mat'],'ps_perio_tshift');
end

if valid_flag
  save([file_out '_matlab/ps_ts_valid_new.mat'],'ps_ts_valid_new');
  save([file_out '_matlab/ps_phase_valid_new.mat'],'ps_phase_valid_new');
  save([file_out '_matlab/ps_h2ph_valid_new.mat'],'ps_h2ph_valid_new');
  save([file_out '_matlab/ps_atmo_valid_new.mat'],'ps_atmo_valid_new');
  save([file_out '_matlab/ps_phase_res_valid_new.mat'],'ps_phase_res_valid_new');
  save([file_out '_matlab/ps_amp_valid.mat'],'ps_amp_valid');
  save([file_out '_matlab/ps_atmo_slc_valid.mat'],'ps_atmo_slc_valid');
end

Btemp = Btemp_new;
dates = dates_new;
save([file_out '_matlab/Btemp.mat'],'Btemp');
save([file_out '_matlab/dates.mat'],'dates');
save([file_out '_matlab/m2ph.mat'],'m2ph');

command = ['zip -r ' file_out '_matlab.zip ' file_out '_matlab'];
unix(command);


