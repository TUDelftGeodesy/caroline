
%% RUN THIS IN YOUR DORIS PROCESSING FOLDER

% name of new folder
folder = 'stitched_ifgs'; 
% id is used in filenaming
id = 'GH';

% required paths
% addpath(genpath('~/bin/StaMPS_v3.3b1')); % might not be needed
addpath(genpath('/home/pconroy/bin/floris/'));

croptype = 'poly'; % boundingbox, full or poly
cropparam = '/home/pconroy/projects/delft_asc_t088_philip/shapefiles/';    % croptype = boundingbox: specify bounding box (for example lon_bb = [4.22;4.66], lat_bb = [51.89;52.02])
                                % croptype = poly: give full path to shapefile, if none is given the shapefile used in DORIS is picked.

stamps = 'no'; % do stamps prep
depsi = 'yes';  % do depsi prep

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
