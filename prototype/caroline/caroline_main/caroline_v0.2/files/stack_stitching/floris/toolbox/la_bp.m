function [la,bp,h2ph] = la_bp(l,p,h,master_date,dates,res_files)
% This script calculates the look angle, perpendicular baselines and height
% to phase factor (h2ph) using DORIS result files
%
% INPUT:
% l:        array of line coordinates
% p:        array of pixel coordinates
% h:        array of heights of (l,p) above the ellipsoid
%
% OUTPUT:
% la:       array of lookangles at location (l,p,h).
% bp:       array of perpendicular baselines at (l,p,h).
% h2ph:     array of height to phase factors at (l,p,h).
%
% Floris Heuff - 03/2018

m_ind = master_date==dates;
[m_image,m_orbit] = metadata(res_files{m_ind});
m_orbfit=orbitfit(m_orbit,4,'verbose',0);

[m_xyz,m_satvec] = lph2xyz(l,p,h,m_image,m_orbfit);
m_sat_xyz = m_satvec(:,1:3);
m_r = m_sat_xyz - m_xyz;

R1 = sqrt(sum(m_r.^2,2));
rho1 = sqrt(sum(m_sat_xyz.^2,2));
Re = sqrt(sum(m_xyz.^2,2));

la = acosd((rho1.^2-Re.^2+R1.^2)./(2*rho1.*R1));
inc = 180-acosd((-rho1.^2+Re.^2+R1.^2)./(2*R1.*Re));

s_dates = dates(~m_ind);
s_res_files = res_files(~m_ind);
bp = zeros(length(l),length(s_dates));
h2ph = zeros(length(l),length(s_dates));
fprintf('Calculating baselines for %i ifgs...\n',length(s_dates));
for i = 1:length(s_dates)
    
    [s_image,s_orbit] = metadata(s_res_files{i});
    s_orbfit=orbitfit(s_orbit,4,'verbose',0);

    [~,~,s_satvec] = xyz2t(m_xyz,s_image,s_orbfit);
    s_sat_xyz = s_satvec(:,1:3);
    s_r = s_sat_xyz-m_xyz;
    
    R2 = sqrt(sum(s_r.^2,2));
    rho2 = sqrt(sum(s_sat_xyz.^2,2));
        
    gamma1 = acosd((-rho1.^2+Re.^2+R1.^2)./(2*Re.*R1));
    gamma2 = acosd((-rho2.^2+Re.^2+R2.^2)./(2*Re.*R2));    
    test1= gamma1 < gamma2;
    test2= gamma1 >= gamma2;
    sign= test1-test2;
    
    b = sqrt(sum((m_sat_xyz-s_sat_xyz).^2,2));
    bpar = R1 - R2;
    bp(:,i) = sign.*sqrt(b.^2-bpar.^2);
    h2ph(:,i) = bp(:,i)./(R1.*sind(inc));
    if floor(i/10) == i/10
        fprintf('Finished %i / %i ifgs\n',i,length(s_dates))
    end    

end

