function satvec = orbitval(tazi,orbfit)
%ORBITVAL   Compute satellite state vector from orbit fit.
%   SATVEC=ORBITVAL(TAZI,ORBFIT) computes the satellite state vector SATVEC
%   at time TAZI from the orbit fit ORBFIT. ORBFIT must have been computed
%   with the function ORBITFIT. TAZI is a scalar or vector with the time 
%   in seconds (in the day). SATVEC is a matrix with in it's columns 
%   the position X(m), Y(m), Z(m) and velocity X_V(m/s), Y_V(m/s), Z_V(m/s),
%   with rows corresponding to time TAZI.
%
%   Examples:
%       orbfit = orbitfit(orbit);
%       satvec = orbitval(ta,orbfit);
%       residuals = orbitval(orbit(:,1),orbfit)-orbit(:,2:7)
%
%   See also METADATA, ORBITVAL, XYZ2LP, XYZ2T and LPH2XYZ.
%
%   (c) Hans van der Marel, Delft University of Technology, 2014.

%   Created:    14 March 2014 by Hans van der Marel
%   Modified:   

% Input argument checking and default values

if nargin ~=2 
   error('incorrect number of arguments')
end
if ~isstruct(orbfit)
   error('ORBFIT must be a structure')
end

if size(tazi,1) == 1 && size(tazi,2) ~= 1
   tazi=tazi';
end
if size(tazi,2) ~= 1
   error('TAZI must be scalar or vector')
end

% Get the polynomial coefficients

t0=orbfit.t0;

coef_x=orbfit.coef_x;
coef_y=orbfit.coef_y;
coef_z=orbfit.coef_z;

coef_vx=polyder(coef_x);
coef_vy=polyder(coef_y);
coef_vz=polyder(coef_z);

% Compute state vector

satvec = [ ...
    polyval(coef_x,tazi-t0)   polyval(coef_y,tazi-t0)  polyval(coef_z,tazi-t0) ...
    polyval(coef_vx,tazi-t0)  polyval(coef_vy,tazi-t0) polyval(coef_vz,tazi-t0) ];

return
