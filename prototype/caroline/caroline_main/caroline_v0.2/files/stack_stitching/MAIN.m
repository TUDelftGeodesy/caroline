
%% RUN THIS IN YOUR DORIS PROCESSING FOLDER

% name of new folder
folder = '{AoI_name}_cropped_stack';

% id is used in filenaming
id = '{AoI_name}';

addpath(genpath('{caroline_dir}/caroline_v{version}/files/stack_stitching/floris'));

% croptype = boundingbox: specify bounding box (for example lon_bb = [4.22;4.66], lat_bb = [51.89;52.02])
% croptype = poly: give full path to shapefile, if none is given the shapefile used in DORIS is picked.
croptype = 'poly'; % boundingbox, full or poly
cropparam = '{shape_dir}/{AoI_name}_shape.shp';    

%% stitch images
stitch_S1_stack(folder,id,croptype,cropparam);

%% make slcs
create_slcs(folder,id);

%% depsi_prep
depsi_prep(folder,id);

