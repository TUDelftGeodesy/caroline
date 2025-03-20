clear all
close all

load **depsi_AoI_name**_**sensor**_**asc_dsc**_t**fill_track**_project.mat

if ~exist([project_id '_mrm_uint8_orig.raw'],'file');
  copyfile([project_id '_mrm_uint8.raw'],[project_id '_mrm_uint8_orig.raw']);
end

mrm_fid = fopen([project_id '_mrm_uint8_orig.raw'],'r');
temp = fread(mrm_fid,[Npixels Nlines],'*uint8')';
fclose(mrm_fid);

mrm_fid_in = fopen([project_id '_mrm.raw'],'r');
mrm = fread(mrm_fid_in,[Npixels Nlines],'*single')';
fclose(mrm_fid_in);

mrm2 = mrm;
mrm2(mrm == -Inf) = NaN;
mrm2(mrm == Inf) = NaN;

mrm_min = nanmin(mrm2(:));
mrm_max = nanmax(mrm2(:));
mrm_new = uint8(255*(mrm2-mrm_min)./(mrm_max-mrm_min));

figure;imagesc(temp);colormap(gray);colorbar
figure;imagesc(mrm);colormap(gray);colorbar
figure;imagesc(mrm_new);colormap(gray);colorbar

mrm_fid_out = fopen([project_id '_mrm_uint8.raw'],'w');
fwrite(mrm_fid_out,mrm_new','uint8');
fclose(mrm_fid_out);

