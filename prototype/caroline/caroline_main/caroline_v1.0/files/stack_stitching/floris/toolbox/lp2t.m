function [t_azi,t_ran] = lp2t(line,pixel,image)
%LP2T    Convert radar line and pixel number into azimuth and range time.
%   [T_AZI,T_RAN]=LP2T(LINE,PIXEL,IMAGE) converts the radar LINE and 
%   PIXEL coordinates into azimuth time T_AZI and range time T_RAN. IMAGE 
%   contains image metadata read by the function METADATA.
%
%   The function assumes [LINE,PIXEL] are in "absolute image" coordinates, 
%   not cropped.
%
%   See also METADATA and T2LP.
%
%   (c) Petar Marinkovic, Delft University of Technology, 2007-2014.

%   Created:    20 June 2007 by Petar Marinkovic
%   Modified:   14 March 2014 by Hans van der Marel
%                - added description
    
% $$$ parmeters of the image
ta1          = image(1); % start time in UTC [sec]
tr1          = image(2); % one.way range time [sec]
PRF          = image(3); % [Hz]
RSR          = image(4); % one.way in [Hz]

t_azi = ta1 + (line - 1.0)./PRF; 
t_ran = tr1 + (pixel - 1.0)./RSR;
    
   
% $$$ EOF
