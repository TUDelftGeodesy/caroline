function [image, orbit] = metadata(result_file)
%METADATA   Get meta and orbit data from DORIS result file.
%   [IMAGE,ORBIT]=METADATA(RESULT_FILE) reads meta and orbit data from 
%   the DORIS result file RESULT_FILE, and returns the meta data in the
%   vector IMAGE and the orbit data in the matrix ORBIT. The IMAGE vector
%   contains the following information
%
%      1     First_pixel_azimuth_time (UTC) (in seconds)
%      2     Range_time_to_first_pixel (one way in seconds)
%      3     Pulse_Repetition_Frequency (computed, Hz) corrected for multilook factor
%      4     Range_sampling_rate (computed, Hz), one way, corrected for multilook factor
%      5     Sensor wavelength [m]
%      6     Scene_centre_latitude
%      7     Scene_centre_longitude
%      8     Oversamplingfactor_azimuth_direction  (reciprocal of multilookfactor)
%      9     Oversamplingfactor_range_direction (reciprocal of multilookfactor)
%     10     Number_of_lines_original corrected for multilook factor
%     11     Number_of_pixels_original corrected for multilook factor
%     12     First_line (w.r.t. original_image) corrected for multilook factor
%     13     Last_line (w.r.t. original_image) corrected for multilook factor
%     14     First_pixel (w.r.t. original_image) corrected for multilook factor
%     15     Last_pixel (w.r.t. original_image) corrected for multilook factor
%     16     Center line (w.r.t. original_image) corrected for multilo
%     17     DC_constant [Hz]
%     18     DC_linear [Hz/s]
%     19     DC_quadratic [Hz/s/s]
%
%   The ORBIT matrix has 7 columns with respectively t(s), X(m), Y(m), Z(m),
%   X_V(m/s), Y_V(m/s), and Z_V(m/s).
%
%   The function first reads all data into a character cell array using
%   the colon as delimiter, which works nice on small size files.
%
%   Example:
%       [image, orbit] = metadata('master.res');
%       orbfit = orbitfit(orbit);
%       [line,pixel] = xyz2lp(xyz,image,orbfit);
%
%   See also ORBITFIT, ORBITVAL, XYZ2LP, XYZ2T and LPH2XYZ. 
%
%   (c) Petar Marinkovic, Hans van der Marel, Delft University of Technology, 2007-2014.

%   Created:    20 June 2007 by Petar Marinkovic
%   Modified:   13 March 2014 by Hans van der Marel
%                - added description and input argument checking
%               19 March 2014 by Hans van der Marel
%                - made image consistent with container used later by the
%                  original author; image_old=image([1:4 6:9 16 12:13]) 

% Input argument checking    

if nargin ~=1 || ~ischar(result_file)
   error('This function must have one input argument of type character')
end
if ~exist(result_file,'file')
   error('Input DORIS result file does not exist.')
end

% $$$ IMAGE --------------------------------------------

% $$$ result_file='19014.res';

image = zeros(1,19); % initalize

% acquisition start time
mdata = textread(result_file,'%s','delimiter',':');

%%% ovs.factor: AZIMUTH
ind = strmatch('Multilookfactor_azimuth_direction',mdata);
if isempty(ind);
    image(8) = 1;
else
    image(8) = 1/str2num(char(mdata(ind+1)));
end;

%%% ovs.factor: RANGE
ind = strmatch('Multilookfactor_range_direction',mdata);
if isempty(ind);
    image(9)=1;
else
    image(9) = 1/str2num(char(mdata(ind+1)));
end;

% UTC time in secs for first pixel
ind = strmatch('First_pixel_azimuth_time (UTC)', mdata);
ddhr = char(mdata(ind+1)); % date and hour

hms  = [str2num(ddhr(end-1:end)) str2num(char(mdata(ind+2))) ...
        str2num(char(mdata(ind+3)))]; % hh mm ss

image(1) = hms(1)*3600 + hms(2)*60 + hms(3);

% 1way range time to 1st pix in [sec]
ind      = strmatch('Range_time_to_first_pixel (2way) (ms)',mdata);
image(2) = (str2num(char(mdata(ind+1)))/2)/1000; % one way in seconds

% PRF [Hz]
ind      = strmatch('Pulse_Repetition_Frequency (computed, Hz)',mdata);
image(3) = str2num(char(mdata(ind+1))) * image(8);

%%% RSR in [Hz]: computed from 2 way time, see definitions
ind      = strmatch('Range_sampling_rate (computed, MHz)',mdata);
image(4) = (str2num(char(mdata(ind+1)))*1e6)*2*image(9); % ONE! way in HZ

%%% sensor wavelength: 
ind      = strmatch('Radar_wavelength',mdata); 
image(5) = str2num(char(mdata(ind+1))); 

%%% lat.center
ind      = strmatch('Scene_centre_latitude',mdata);
image(6) = str2num(char(mdata(ind+1)));

%%% lon.center
ind      = strmatch('Scene_centre_longitude',mdata);
image(7) = str2num(char(mdata(ind+1)));

%%% number.of.lines[original]
ind = strmatch('Number_of_lines_original',mdata); 
image(10) = str2num(char(mdata(ind+1))) * image(8); 

%%% number.of.pixels[original]
ind = strmatch('Number_of_pixels_original',mdata); 
image(11) = str2num(char(mdata(ind+1))) * image(9); 

%%% first.crop.line
ind      = strmatch('First_line (w.r.t. original_image)',mdata);
first_l  = str2num(char(mdata(ind+1))) * image(8);

if image(8) > 1;
    image(12) = first_l - 1; 
else
    image(12) = first_l; 
end
    
%%% last.crop.line
ind      = strmatch('Last_line (w.r.t. original_image)',mdata);
last_l   = str2num(char(mdata(ind+1)))  * image(8);
image(13)= last_l;

%%% first.crop.pixel
ind      = strmatch('First_pixel (w.r.t. original_image)',mdata);
first_px = str2num(char(mdata(ind+1))) * image(9);

if image(9) > 1;
    image(14) = first_px - 1; 
else
    image(14) = first_px; 
end

%%% last.crop.pixel
ind      = strmatch('Last_pixel (w.r.t. original_image)',mdata);
last_px = str2num(char(mdata(ind+1))) * image(9);
image(15)= last_px;

%%% mid.crop.line
% $$$ image(9) = round((first_l + last_l)/2); % oversampled?
image(16) = (first_l + last_l)/2; % oversampled?

%%% Doppler info

ind = strmatch('Xtrack_f_DC_constant (Hz, early edge)',mdata);
image(17) = str2num(char(mdata(ind+1)));

ind = strmatch('Xtrack_f_DC_linear (Hz/s, early edge)',mdata);
image(18) = str2num(char(mdata(ind+1)));

ind = strmatch('Xtrack_f_DC_quadratic (Hz/s/s, early edge)',mdata);
image(19) = str2num(char(mdata(ind+1)));

ind = strmatch('First_line (w.r.t. output_image)',mdata);
if isempty(ind)
    image(20) = NaN;
else
    image(20) = str2num(char(mdata(ind+1)));
end

ind = strmatch('Last_line (w.r.t. output_image)',mdata);
if isempty(ind)
    image(21) = NaN;
else
    image(21) = str2num(char(mdata(ind+1)));
end

ind = strmatch('First_pixel (w.r.t. output_image)',mdata);
if isempty(ind)
    image(22) = NaN;
else
    image(22) = str2num(char(mdata(ind+1)));
end

ind = strmatch('Last_pixel (w.r.t. output_image)',mdata);
if isempty(ind)
    image(23) = NaN;
else
    image(23) = str2num(char(mdata(ind+1)));
end

ind = strmatch('Number_of_lines_output_image',mdata);
if isempty(ind)
    image(24) = NaN;
else
    image(24) = str2num(char(mdata(ind+1)));
end

ind = strmatch('Number_of_pixels_output_image',mdata);
if isempty(ind)
    image(25) = NaN;
else
    image(25) = str2num(char(mdata(ind+1)));
end



% $$$ Prec.ORBIT from RAS file ----------------------------------------

ind      = strmatch('NUMBER_OF_DATAPOINTS',mdata);
norb_pts = str2num(char(mdata(ind+1)));
orbit    = str2num(char(mdata(ind+2:ind+1+norb_pts)));

% EOF
