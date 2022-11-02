
%% RUN THIS IN YOUR DORIS PROCESSING FOLDER

% name of new folder
folder = 'Delft'; 
% id is used in filenaming
id = 'delft';

% required paths
addpath(genpath('~/bin/StaMPS_v3.3b1'));
addpath(genpath('~/matlab/stack_prep'));

f_lat=51.90; %%need to change
l_lat=52.02;
f_lon=4.23;
l_lon=4.46;


factor = 1;
n_latlon = [round(58)/factor round(72)/factor];

d_lat=(l_lat-f_lat)/(n_latlon(1)-1)/2;
d_lon=(l_lon-f_lon)/(n_latlon(2)-1)/2;

lon_bb = [4.23-d_lon;4.46+d_lon];
lat_bb = [51.90-d_lat;52.02+d_lat];

croptype = 'boundingbox'; % boundingbox, full or poly
cropparam = [lon_bb lat_bb];    % croptype = boundingbox: specify bounding box (for example lon_bb = [4.22;4.66], lat_bb = [51.89;52.02])
                                % croptype = poly: give full path to shapefile, if none is given the shapefile used in DORIS is picked.


%% stitch images

stitch_S1_stack(folder,croptype,cropparam);

%% make slcs

create_slcs(folder);

depsi_prep(folder);
