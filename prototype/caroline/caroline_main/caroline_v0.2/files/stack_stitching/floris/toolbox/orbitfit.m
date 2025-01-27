function orbfit = orbitfit(orbit,degree,varargin)
%ORBITFIT   Fit low degree polynomial to short segment of satellite orbit.
%   ORBFIT=ORBITFIT(ORBIT,DEGREE) fits a polynomial of degree DEGREE to
%   the orbit state vector ORBIT. ORBIT is matrix with 4 or 7 columns,
%   with respectively t(s), X(m), Y(m), Z(m), and optionally X_V(m/s), 
%   Y_V(m/s), and Z_V(m/s). ORBIT is an output structure which contains
%   the coefficients of the polynomial fits. The default value for 
%   DEGREE is 3.
%
%   ORBFIT=ORBITFIT(ORBIT) fits a degree 3 polynomial to the orbit.
%
%   ORBFIT=ORBITFIT(ORBIT,DEGREE,'VERBOSE',1) increases the verbosity 
%   level. With VERBOSE is 0 nothing is printed,  with VERBOSE is 1
%   a short message is printed and with VERBOSE is 2 plots are made of
%   the orbit fit residuals.
%
%   Example:
%       [image, orbit] = metadata('master.res');
%       orbfit = orbitfit(orbit);
%       statevec = orbitval(ta,orbfit);
%
%   See also METADATA, ORBITVAL, XYZ2LP, XYZ2T and LPH2XYZ. .
%
%   (c) Hans van der Marel, Delft University of Technology, 2014.

%   Created:    14 March 2014 by Hans van der Marel
%   Modified:   

% Input argument checking and default values

if nargin < 1 
   error('This function must have at least one input argument')
end
if nargin < 2
   degree=3;
end
verbose=0;
for k=1:2:length(varargin)
   switch lower(varargin{k})
       case {'verbose','debug'}
          if  k+1 <= length(varargin)
             verbose=varargin{k+1};   
          else
             verbose=2;
          end
       otherwise
          error('unknown option')        
   end
end

% Compute time argument px (centered around mid interval)

px = orbit(:,1); 
t0 = ( min(px) + max(px) )/2;
px=px-t0;

% Orbit fit

coef_x = polyfit(px,orbit(:,2),degree);
coef_y = polyfit(px,orbit(:,3),degree);
coef_z = polyfit(px,orbit(:,4),degree);

% Prepare output structure

orbfit.t0=t0;
orbfit.range=[ min(px) max(px) ];
orbfit.degree=degree;
orbfit.coef_x=coef_x;
orbfit.coef_y=coef_y;
orbfit.coef_z=coef_z;
orbfit.orgdata=orbit;

% Evaluate the fit

pos_x = polyval(orbfit.coef_x,px);
pos_y = polyval(orbfit.coef_y,px);
pos_z = polyval(orbfit.coef_z,px);

posres=[pos_x pos_y pos_z] - orbit(:,2:4);
orbfit.stdposfit=std(posres);

if verbose > 0
  fprintf('St.dev. position fit (degree=%d): X %6.3f [m], Y %6.3f [m], Z %6.3f [m]\n',degree,std(posres));
end

% Optionally plot the position residuals

if verbose > 1
  figure
  plot(px,posres)
  title(['orbit fit position error (degree=' num2str(degree) ')'])
  ylabel('X,Y,Z [m]')
  xlabel('time [s]')
  legend('X','Y','Z')
end

% In case we have velocities we can check the velocity fit

if size(orbit,2) > 4
 
    
  vel_x = polyval(polyder(coef_x),px);
  vel_y = polyval(polyder(coef_y),px);
  vel_z = polyval(polyder(coef_z),px);

  velres=[vel_x vel_y vel_z] - orbit(:,5:7);
  orbfit.stdvelfit=std(velres);

  if verbose > 0
    fprintf('St.dev. velocity fit (degree=%d): vx %6.3f [m/s], vy %6.3f [m/s], vz %6.3f [m/s]\n',degree,std(velres));
  end
  
  % Optionally plot the velocity residuals

  if verbose > 1
    figure
    plot(px,velres)
    title(['orbit fit velocity error (degree=' num2str(degree) ')'])
    ylabel('vx,vy,vz [m/s]')
    xlabel('time [s]')
    legend('vx','vy','vz')
  end
  
end

% Optionally plot the acceleration and acceleration rate

if verbose > 1

  acc_x = polyval(polyder(polyder(coef_x)),px);
  acc_y = polyval(polyder(polyder(coef_y)),px);
  acc_z = polyval(polyder(polyder(coef_z)),px);

  acc=[acc_x acc_y acc_z];

  figure
  plot(px,acc)
  title(['orbit fit acceleration (degree=' num2str(degree) ')'])
  ylabel('ax,ay,az [m/s2]')
  xlabel('time [s]')
  legend('ax','ay','az')

  accdot_x = polyval(polyder(polyder(polyder(coef_x))),px);
  accdot_y = polyval(polyder(polyder(polyder(coef_y))),px);
  accdot_z = polyval(polyder(polyder(polyder(coef_z))),px);

  accdot=[accdot_x accdot_y accdot_z];

  figure
  plot(px,accdot)
  title(['acceleration rate (degree=' num2str(degree) ')'])
  ylabel('adotx,adoty,adotz [m/s3]')
  xlabel('time [s]')
  legend('adotx','adoty','adotz')

end

return