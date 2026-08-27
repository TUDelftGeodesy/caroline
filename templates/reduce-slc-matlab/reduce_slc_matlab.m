%% RUN THIS IN A DIRECTORY WITH ALL CONTENTS OF THE DORIS DIRECTORY YOU AIM TO CROP SOFT LINKED
% Crops a DORIS 4.0 or 5.0 stack to the bounding box of a shapefile
% Adapted from and inspired by the stitch toolbox of F. Heuff, 2018
%
% By Simon van Diepen, 02/2025
%
% Support for other sensors by Simon van Diepen - 10/03/2025

% Link code
addpath(genpath('**caroline_install_directory**/scripts/crop'));

%%% USER SETTINGS %%%
% name of new folder
folder = 'cropped_stack';

% full path to crop shapefile
crop_file = '**general:shape-file:directory**/**general:shape-file:aoi-name**_shape.shp';

% which sensor was used
sensor = '**general:input-data:sensor**';

%%% END OF USER SETTINGS %%%

do_crop(folder,crop_file,sensor);

