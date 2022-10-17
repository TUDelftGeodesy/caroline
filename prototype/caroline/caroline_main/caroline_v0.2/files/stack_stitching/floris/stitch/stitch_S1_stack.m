function stitch_S1_stack(folder,croptype,cropparam)
% Stitch together Sentinel 1 bursts processed using DORIS 5.0. If
% specified, images will be cropped.
% 
% INPUT:
% folder:       Name of folder where stitched images will be saved
% croptype:     Specify boundingbox, full or poly
% cropparam:    croptype = boundingbox: specify bounding box (for example lon_bb = [4.22;4.66], lat_bb = [51.89;52.02])
%               croptype = poly: give full path to shapefile, if none is
%               given the shapefile of the region of interest used in DORIS is
%               picked
%
% OUTPUT:
% Textfiles with filepaths to the different images, result files and a list
% of dates.
%
% Required scripts: 
% - stitch_master_image.m
% - stitch_slave_image.m
% - bounding_box.m
% - freadbk.m
% - fwritebk.m
%
% Floris Heuff - 03/2018

% EDITS
% Philip Conroy - 17.10.2022 Removed "id" parameter to keep generic
% filenames

workdir = pwd;
cd('stack');
system('ls -d [1,2]* > dir.txt');
fdir = fopen('dir.txt');
temp = textscan(fdir,'%s');dir = temp{1,1};
fclose(fdir);
cd(workdir);   

finput = fopen('doris_input.xml');
temp = textscan(finput,'%s'); doris_input = temp{1,1};
fclose(finput);

shp_file_path = doris_input{6}(18:end - 18);
master_date = doris_input{17}(14:end - 14); master_date(5) = []; master_date(7) = []; 


if strcmp(croptype,'poly')
    if nargin < 4 || isempty(cropparam)
        crop_in = shp_file_path;
    else
        crop_in = cropparam;
    end
end

if strcmp(croptype,'boundingbox')
    if nargin < 4
        error('No boudingbox specified')
    end
    crop_in = cropparam;
end

if strcmp(croptype,'full')
    crop_in = [];
end

master_ix = find(strcmp(master_date,dir));
bb = stitch_master_image(['stack/',dir{master_ix}],folder,crop_in);
fprintf('Finished folder %s. \n',['stack/',dir{master_ix}])

dir(master_ix) = [];

for d = 1:length(dir)    
    stitch_slave_image(['stack/',dir{d}],folder,bb);    
    fprintf('Finished folder %s. \n',['stack/',dir{d}])    
end

system(['find "$(pwd -P)/',folder,'"/*  -name ''*srd*.raw'' > ',folder,'/path_images.txt']);
system(['find "$(pwd -P)/',folder,'"/*  -name ''*.res'' > ',folder,'/path_res_files.txt']);
system(['find "$(pwd -P)/',folder,'"/*  -name ''phi.raw'' > ',folder,'/path_coords.txt']);
system(['find "$(pwd -P)/',folder,'"/*  -name ''lam.raw'' >> ',folder,'/path_coords.txt']);
system(['find "$(pwd -P)/',folder,'"/*  -name ''dem_radar.raw'' >> ',folder,'/path_coords.txt']);
system(['cp stack/dir.txt ',folder,'/dates.txt']);
end

