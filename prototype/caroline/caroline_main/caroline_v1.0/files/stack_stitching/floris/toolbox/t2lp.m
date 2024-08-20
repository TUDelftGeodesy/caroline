function [line,pixel] = t2lp(t_azi,t_ran,image)
%T2LP    Convert azimuth and range time into radar line and pixel number.
%   [LINE,PIXEL]=LP2T(T_AZI,T_RAN,IMAGE) converts the radar azimuth time 
%   T_AZI and range time T_RAN into LINE and PIXEL coordinates. IMAGE 
%   contains image metadata read by the function METADATA.
%
%   See also METADATA and LP2T.
%
%   (c) Petar Marinkovic, Delft University of Technology, 2007-2014.

%   Created:    20 June 2007 by Petar Marinkovic
%   Modified:   14 March 2014 by Hans van der Marel
%                - added description    

% $$$ SLC.parameters
ta1 = image(1);    %second of day of first azimuth line
PRF = image(3);    %pulse repetition frequency
tr1 = image(2);    %one way time (s) to first range pixel
RSR = image(4);    %range sampling rate

line  = 1 + PRF*(t_azi - ta1);
pixel = 1 + RSR*(t_ran - tr1);

% $$$ EOF
