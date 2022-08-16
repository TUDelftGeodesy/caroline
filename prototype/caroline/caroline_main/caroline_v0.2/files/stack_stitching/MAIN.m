
%% RUN THIS IN YOUR DORIS PROCESSING FOLDER

% name of new folder
folder = '{AoI_name}_cropped_stack'; 
% id is used in filenaming
id = '{AoI_name}';

% required paths
% addpath(genpath('~/bin/StaMPS_v3.3b1')); % not needed
addpath(genpath('{caroline_dir}/caroline_v{version}/files/stack_stitching/floris'));

% croptype = boundingbox: specify bounding box (for example lon_bb = [4.830556;4.847222], lat_bb = [52.133333;52.143056])
% croptype = poly: give full path to shapefile, if none is given the shapefile used in DORIS is picked.
croptype = 'poly'; % boundingbox, full or poly
cropparam = '{shape_dir}/{AoI_name}_shape.shp';    


stamps = 'no'; % do stamps prep
depsi = 'yes'; % do depsi prep

%% stamps PS selection parameters
amp             = 0.4;      % amplitude dispersion
n_patch_azi     = 1;        % number of patches in azimuth (in case of large images)
n_patch_range   = 1;        % number of patches in range
overlap_azi     = 200;
overlap_range   = 50;


%% stitch images

stitch_S1_stack(folder,id,croptype,cropparam);

%% make slcs

create_slcs(folder,id);

%% stamps_prep
if strcmp(stamps,'yes')
    stamps_prep(folder,amp,n_patch_azi,n_patch_range,overlap_azi,overlap_range);
end

%% depsi_prep
if strcmp(depsi,'yes')
    depsi_prep(folder,id);
end
