function [line,pixel,satvec] = xyz2lp(xyz_vec,image,orbfit,varargin)
%XYZ2LP   Convert Cartesian coordinates into radar line and pixel numbers.
%   [LINE,PIXEL]=XYZ2LP(XYZ,IMAGE,ORBFIT) converts the Cartesian coordinates
%   XYZ into LINE and PIXEL coordinates for the SAR image. IMAGE contains
%   the image metadata read from a corresponding DORIS result file using
%   the METADATA function. ORBFIT contains an orbit fit produced by
%   ORBITFIT from the ORBIT data read by the METADATA function.
%
%   [LINE,PIXEL,SATVEC]=XYZ2LP(XYZ,IMAGE,ORBFIT) also outputs the corresponding
%   satellite position and velocity. SATVEC is a matrix with in it's 
%   columns the position X(m), Y(m), Z(m) and velocity X_V(m/s), Y_V(m/s), 
%   Z_V(m/s), with rows corresponding to LINE and PIXEL.
%
%   [...]=XYZ2LP(...,'VERBOSE',0,'MAXITER',10,'CRITERPOS',1e-10) includes 
%   optional input arguments VERBOSE, MAXITER and CRITERPOS to override 
%   the default verbosity level and interpolator exit criteria. The defaults 
%   are MAXITER=10, CRITERPOS=1e-10 and VERBOSE=0.
%
%   Example:
%       [image, orbit] = metadata('master.res');
%       orbfit = orbitfit(orbit);
%       [line,pixel] = xyz2lp(xyz,image,orbfit);
%
%   See also METADATA, ORBITFIT, ORBITVAL, XYZ2T and LPH2XYZ.
%
%   (c) Hans van der Marel, Delft University of Technology, 2007-2014.

%   Created:    20 June 2007 by Petar Marinkovic
%   Modified:   13 March 2014 by Hans van der Marel
%                - added description and input argument checking
%                - reworked function to use ORBITFIT
%                6 April 2014 by Hans van der Marel
%                - improved handling of optional parameters

% Input argument checking and default values

if nargin < 3
   error('This function must have at least three input arguments')
end

verbose=0;
for k=1:2:length(varargin)
   switch lower(varargin{k})
       case {'verbose','debug'}
          verbose=varargin{k+1};   
   end
end

% Check ORBFIT input argument, if necessary, compute

if ~isstruct(orbfit)
   if verbose > 0
     disp('Third agument ORBFIT must be astructure produced by ORBITFIT') 
     disp('We will compute it for you now...') 
   end
   orbfit=orbitfit(orbfit);    
end

% get times

[t_azi,t_ran,satvec] = xyz2t(xyz_vec,image,orbfit,varargin{:});

% SLC.parameters
ta1 = image(1);    %second of day of first azimuth line
PRF = image(3);    %pulse repetition frequency
tr1 = image(2);    %one way time (s) to first range pixel
RSR = image(4);    %range sampling rate

line  = 1 + PRF.*(t_azi - ta1);
pixel = 1 + RSR.*(t_ran - tr1);

return