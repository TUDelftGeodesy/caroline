function [xyz,satvec] = lph2xyz(line,pixel,height,image,orbfit,varargin)
%LPH2XYZ   Convert radar line/pixel coordinates into Cartesian coordinates.
%   XYZ=LPH2XYZ(LINE,PIXEL,HEIGHT,IMAGE,ORBFIT) converts the radar coordinates
%   LINE and PIXEL into Cartesian coordinates XYZ. HEIGHT contains the height
%   of the pixel above the ellipsoid. IMAGE contains the image metadata
%   and ORBFIT the orbit fit, proceduced respectively by the METADATA and
%   ORBITFIT functions. 
%   
%   [XYZ,SATVEC]=LPH2XYZ(...) also outputs the corresponding satellite 
%   position and velocity, with SATVEC a matrix with in it's columns the 
%   position X(m), Y(m), Z(m) and velocity X_V(m/s), Y_V(m/s), Z_V(m/s), 
%   with rows corresponding to rows of XYZ.
%
%   [...]=LPH2XYZ(...,'VERBOSE',0,'MAXITER',10,'CRITERPOS',1e-6,'ELLIPSOID',
%   [6378137.0 6356752.3141]) includes optional input arguments VERBOSE, 
%   MAXITER, CRITERPOS and ELLIPSOID  to overide the default verbosity level,  
%   interpolator exit criteria and ellipsoid. The defaults are the WGS-84
%   ELLIPSOID=[6378137.0 6356752.3141], MAXITER=10, CRITERPOS=1e-6 and 
%   VERBOSE=0.
%
%   Example:
%       [image, orbit] = metadata('master.res');
%       orbfit = orbitfit(orbit);
%       xyz = lph2xyz(line,pixel,0,image,orbfit);
%
%   See also METADATA, ORBITFIT, ORBITVAL, XYZ2LP and XYZ2T.
%
%   (c) Petar Marinkovic, Hans van der Marel, Delft University of Technology, 2007-2014.

%   Created:    20 June 2007 by Petar Marinkovic
%   Modified:   13 March 2014 by Hans van der Marel
%                - added description and input argument checking
%                - use orbit fitting procedure
%                - added output of satellite position and velocity
%                - original renamed to LPH2XYZ_PM
%                6 April 2014 by Hans van der Marel
%                - improved handling of optional parameters

% Constants 

SOL = 299792458;

% Input argument checking 

if nargin < 5 
   error('This function must have at least five input arguments')
end
if ~isstruct(orbfit)
   error('ORBFIT must be a structure, make sure you call ORBITFIT first.')
end

% Defaults and optional value processing

ellipsoid = [6378137.0 6356752.3141];   % WGS84 ellipsoid
MAXITER=10;                             % Max number of iterations
CRITERPOS=1e-6;                         % Stop criterion for iterations
verbose=0;                              % Verbosity level

for k=1:2:length(varargin)
   switch lower(varargin{k})
       case {'verbose','debug'}
          verbose=varargin{k+1};   
       case {'ellipsoid'}
          ellipsoid=varargin{k+1};   
       case {'maxiter'}
          MAXITER=varargin{k+1};   
       case {'criterpos'}
          CRITERPOS=varargin{k+1};   
       otherwise
          error('unknown option')        
   end
end

% Initialization

num_points = numel(line);
xyz = zeros(num_points,3);
satvec = zeros(num_points,6);

% Image parameters

ta1          = image(1); % start time in UTC [sec]
tr1          = image(2); % one.way range time [sec]
PRF          = image(3); % [Hz]
RSR          = image(4); % one.way in [Hz]
centerphi    = image(6); 
centerlambda = image(7);


% Compute reference surface: WGS84

ell_a=ellipsoid(1);                 % semimajor of the ellipsoid
ell_b=ellipsoid(2);                 % semiminor of the ellipsoid
ell_e2=(ell_a^2-ell_b^2)/ell_a^2;   % squared first eccentricity(derived)
% ell_e2b=(ell_a^2-ell_b^2)/ell_b^2;  % squared second eccentricity(derived)

% [lat,long,h] of scene center to [x,y,z]

h            = mean(height); % this is only for initial values
centerphi    = centerphi*pi/180;
centerlambda = centerlambda*pi/180;
Ncenter      = ell_a/sqrt(1-ell_e2*(sin(centerphi)^2)); % eccentricity
scenecenterx = (Ncenter+h)*cos(centerphi)*cos(centerlambda);
scenecentery = (Ncenter+h)*cos(centerphi)*sin(centerlambda);
scenecenterz = (Ncenter+h-ell_e2*Ncenter)*sin(centerphi);

% loop throug points

for n = 1 : num_points

    posonellx = scenecenterx;
    posonelly = scenecentery;
    posonellz = scenecenterz;
    
    % convert line and pixel to time: from Doris
    % aztime = line2ta(line,image.t_zai1,image.prf)
    % ratime = pix2tr(pixel,image.t_range1,image.rsr2x)

    aztime = ta1 + (line(n) -1.0)/PRF; 
    ratime = tr1 + (pixel(n)-1.0)/RSR;
    
    %get position and velocity of the satellite

    satvec(n,:) = orbitval(aztime,orbfit);

    possatx = satvec(n,1);
    possaty = satvec(n,2);
    possatz = satvec(n,3);
    velsatx = satvec(n,4);
    velsaty = satvec(n,5);
    velsatz = satvec(n,6);
    
    for iter=1:MAXITER
        
        %update equations and slove system
        dsat_Px = posonellx - possatx;   %vector of 'satellite to P on ellipsoid'
        dsat_Py = posonelly - possaty;
        dsat_Pz = posonellz - possatz;
        
        equationset(1,1) = -(velsatx*dsat_Px+velsaty*dsat_Py+velsatz* ...
                             dsat_Pz);
        
        equationset(2,1) = -(dsat_Px*dsat_Px+dsat_Py*dsat_Py+dsat_Pz* ...
                             dsat_Pz-(SOL*ratime).^2);
        
        equationset(3,1) = -((posonellx*posonellx+posonelly*posonelly)/ ...
                             ((ell_a+height(n)).^2)+(posonellz/(ell_b+ ...
                                                          height(n)))^2-1.0);

        partialsxyz(1,1) = velsatx;
        partialsxyz(1,2) = velsaty;
        partialsxyz(1,3) = velsatz;
        partialsxyz(2,1) = 2*dsat_Px;
        partialsxyz(2,2) = 2*dsat_Py;
        partialsxyz(2,3) = 2*dsat_Pz;
        partialsxyz(3,1) = (2*posonellx)/((ell_a+height(n))^2);
        partialsxyz(3,2) = (2*posonelly)/((ell_a+height(n))^2);
        partialsxyz(3,3) = (2*posonellz)/((ell_b+height(n))^2);
        
        % solve system [NOTE] orbit_normalized, otherwise close to
        % singular
        solpos = partialsxyz\equationset;
        solx = solpos(1);
        soly = solpos(2);
        solz = solpos(3);
        
        % update solution
        posonellx = posonellx + solx;
        posonelly = posonelly + soly;
        posonellz = posonellz + solz;
        
        % check convergence
        if (abs(solx)<CRITERPOS && abs(soly)<CRITERPOS && abs(solz)<CRITERPOS)
            break;
        elseif (iter>=MAXITER)
            fprintf('lph2xyz did NOT converge after %d iterations (eps=%g,%g,%g)\n',iter,solx,soly,solz)
            warning(['Maximum number of iterations (' num2str(MAXITER) ') exceeded'])
        end
        
    end
    
    if verbose > 0
      fprintf('lph2xyz converged after %d iterations (eps=%g,%g,%g)\n',iter,solx,soly,solz)
    end
    
    % final solution: array of XYZ coordinates
    xyz(n,:)=[posonellx posonelly posonellz];
    
end

return
