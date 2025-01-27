function [t_azi,t_ran,satvec] = xyz2t(xyz_vec,image,orbfit,varargin)
%XYZ2T   Convert Cartesian coordinates into radar azimuth and range time.
%   [T_AZI,T_RAN]=XYZ2T(XYZ,IMAGE,ORBFIT) converts the Cartesian coordinates
%   XYZ into radar azimuth time T_AZI and range time T_RAN. IMAGE contains
%   image metadata and ORBFIT the satellite orbit data computed using the
%   function ORBITFIT using the ORBIT data from the DORIS result file. 
%   IMAGE and ORBIT are read by the function METADATA.
%
%   [T_AZI,T_RAN,SATVEC]=XYZ2T(XYZ,IMAGE,ORBFIT) also outputs the position
%   and veclocity of the satellite at T_AZI. SATVEC is a matrix with in it's 
%   columns the position X(m), Y(m), Z(m) and velocity X_V(m/s), Y_V(m/s), 
%   Z_V(m/s), with rows corresponding to time T_AZI.
%
%   [...]=XYZ2T(...,'VERBOSE',0,'MAXITER',10,'CRITERPOS',1e-10) includes 
%   optional input arguments VERBOSE, MAXITER and CRITERPOS to override 
%   the default verbosity level and interpolator exit criteria. The defaults 
%   are MAXITER=10, CRITERPOS=1e-10 and VERBOSE=0.
%
%   Example:
%       [image, orbit] = metadata('master.res');
%       orbfit = orbitfit(orbit);
%       [t_azi,t_ran] = xyz2t(xyz,image,orbfit);
%
%   See also METADATA, ORBITFIT, ORBITVAL, XYZ2LP and LPH2XYZ.
%
%   (c) Hans van der Marel, Delft University of Technology, 2014.

%   Created:    20 June 2007 by Petar Marinkovic
%   Modified:   13 March 2014 by Hans van der Marel
%                - added description and input argument checking
%                - completely reworked orbit fitting procedure
%                - added output of satellite position and velocity
%                - original renamed to XYZ2T_PM
%                6 April 2014 by Hans van der Marel
%                - improved handling of optional parameters

% Constants

SOL = 299792458;                     % speed of light

% Input argument checking 

if nargin < 3
   error('This function must have at least three input arguments')
end
if ~isstruct(orbfit)
   error('ORBFIT must be a structure, make sure you call ORBITFIT first.')
end

% Defaults and optional value processing

MAXITER=10;                             % Max number of iterations
CRITERPOS=1e-10;                        % Stop criterion for iterations
verbose=0;                              % Verbosity level

for k=1:2:length(varargin)
   switch lower(varargin{k})
       case {'verbose','debug'}
          verbose=varargin{k+1};   
       case {'maxiter'}
          MAXITER=varargin{k+1};   
       case {'criterpos'}
          CRITERPOS=varargin{k+1};   
       otherwise
          error('unknown option')        
   end
end

% Initialize the output

np    = size(xyz_vec,1);

t_azi = zeros(np,1);
t_ran = zeros(np,1);
satvec = zeros(np,6);

% Get orbit coefficients and derivatives for velocity and acceleration

t0=orbfit.t0;

coef_x=orbfit.coef_x;
coef_y=orbfit.coef_y;
coef_z=orbfit.coef_z;

coef_vx=polyder(coef_x);
coef_vy=polyder(coef_y);
coef_vz=polyder(coef_z);
coef_ax=polyder(coef_vx);
coef_ay=polyder(coef_vy);
coef_az=polyder(coef_vz);

% Initial value for tazi

% ta1         = image(1);    % second of day of first azimuth line
% PRF         = image(3);    % pulse repetition frequency
% line_center = image(16);

tazi = (image(16)-1)/image(3)+image(1);

% Compute solution for tazi

for k = 1 : np;
    
    pos = xyz_vec(k,:);
    
    for iter = 1 : MAXITER;
        
        % update equations
        possat(1) = polyval(coef_x,tazi-t0);  %orbit corresponding to the azimuth time
        possat(2) = polyval(coef_y,tazi-t0);
        possat(3) = polyval(coef_z,tazi-t0);
        velsat(1) = polyval(coef_vx,tazi-t0);  
        velsat(2) = polyval(coef_vy,tazi-t0);
        velsat(3) = polyval(coef_vz,tazi-t0);
        accsat(1) = polyval(coef_ax,tazi-t0);  
        accsat(2) = polyval(coef_ay,tazi-t0);
        accsat(3) = polyval(coef_az,tazi-t0);

        delta = pos - possat;
        
        % update solution
        solution = -(velsat(1)*delta(1)+velsat(2)*delta(2)+velsat(3)* ...
                     delta(3))/(accsat(1)*delta(1)+accsat(2)*delta(2)+ ...
                                accsat(3)*delta(3)-velsat(1)^2-velsat(2)^2- ...
                                velsat(3)^2);

        tazi = tazi + solution;
        
        % check convergence
        if(abs(solution) < CRITERPOS)
            break;
        elseif ( iter >= MAXITER )
            fprintf('xyz2t did NOT converge after %d iterations (eps=%g)\n',iter,solution)
            warning(['Maximum number of iterations (' num2str(MAXITER) ') exceeded'])
        end
        
    end

    if verbose > 0
       fprintf('xyz2t converged after %d iterations (eps=%g)\n',iter,solution)
    end
    
    t_azi(k) = tazi; % azimuth time
    
    possat(1) = polyval(coef_x,tazi-t0);  %orbit corresponding to the azimuth time
    possat(2) = polyval(coef_y,tazi-t0);
    possat(3) = polyval(coef_z,tazi-t0);

    delta = pos - possat;

    t_ran(k) = sqrt(delta(1)^2+delta(2)^2+delta(3)^2)/SOL;  %range time, tran

    velsat(1) = polyval(coef_vx,tazi-t0);  
    velsat(2) = polyval(coef_vy,tazi-t0);
    velsat(3) = polyval(coef_vz,tazi-t0);

    satvec(k,:) = [ possat velsat ] ;
   
    % % correction for fdc
    % lambda=image(5)
    % fdc=image(17)
    % dt_azi= (lambda/2)*fdc*sqrt(delta(1).^2+delta(2).^2+delta(3).^2) / ... 
    %         (accsat(1)*delta(1)+accsat(2)*delta(2)+ accsat(3)*delta(3) - ...
    %          velsat(1)^2-velsat(2)^2- velsat(3)^2);
    % dline=dt_azi*image(3)

end

return
