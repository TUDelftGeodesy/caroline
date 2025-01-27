function [la_interp, bp_interp] = la_bp_interp(X,Y,Z,Xq,Yq)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

master_date = load('Output_s1_asc_t088/master_date.txt');
dates = load('Output_s1_asc_t088/dates_raw_files.txt');
nslcs = length(dates);
npoly = length(Xq);

ver=version('-release');
ver=str2double(ver(1:4));

if exist('StaMPS_s1_asc_t088/look_angle.1.in','file') == 2
    bp_interp = zeros(npoly,nslcs);
    for i = 1:nslcs % bp for each slc
        if dates(i) == master_date
            continue % master, bp=0
        end
        bp_name = ['StaMPS_s1_asc_t088/bperp_' num2str(dates(i)) '.1.in'];
        bp_interp_tmp = load([bp_name]);
        bp_interp_tmp0 = reshape(bp_interp_tmp(1:2:end),50,50)';
        bp_interp_tmp1000 = reshape(bp_interp_tmp(2:2:end),50,50)';
        if ver <= 2009
            bp_interp0 = griddata(X,Y,bp_interp_tmp0,...
                Xq,Yq,'linear',{'QJ'});
            bp_interp1000 = griddata(X,Y,bp_interp_tmp1000,...
                Xq,Yq,'linear',{'QJ'});
            bp_interp(:,i) = bp_interp0+(bp_interp1000-bp_interp0).*Z/1000;
        else
            bp_interp0 = griddata(X,Y,bp_interp_tmp0,...
            Xq,Yq,'linear');
            bp_interp1000 = griddata(X,Y,bp_interp_tmp1000,...
            Xq,Yq,'linear');
            bp_interp(:,i) = bp_interp0+(bp_interp1000-bp_interp0).*Z/1000;
        end
    end

    la_interp_tmp = load('StaMPS_s1_asc_t088/look_angle.1.in');
    la_interp_tmp0 = reshape(la_interp_tmp(1:2:end),50,50)';
    la_interp_tmp1000 = reshape(la_interp_tmp(2:2:end),50,50)';
    if ver <= 2009
        la_interp0 = griddata(X,Y,la_interp_tmp0,Xq,Yq,'linear',{'QJ'});
        la_interp1000 = griddata(X,Y,la_interp_tmp1000,Xq,Yq,'linear',{'QJ'});
    else
        la_interp0 = griddata(X,Y,la_interp_tmp0,Xq,Yq,'linear');
        la_interp1000 = griddata(X,Y,la_interp_tmp1000,Xq,Yq,'linear');
    end
    %adjust bperp for local height
    la_interp = la_interp0+(la_interp1000-la_interp0).*Z/1000;
    
else
    
    fnlines = load('nlines_crp.txt'); 
    fnpixels = load('npixels_crp.txt'); 
    
    fl = fnlines(2);
    ll = fnlines(3) + 1;
    fp = fnpixels(2);
    lp = fnpixels(3) + 1;

    grid_l = repmat(linspace(fl,ll,50)',1,50)';
    grid_p = repmat(linspace(fp,lp,50),50,1)';

    grid_list(1:2:4999,1:3) = [grid_l(:) grid_p(:) zeros(2500,1)];
    grid_list(2:2:5000,1:3) = [grid_l(:) grid_p(:) repmat(1000,2500,1)];

    [la,bp] = la_bp(grid_list(:,1),grid_list(:,2),grid_list(:,3));
    
    bp_interp = zeros(npoly,nslcs);
    for i = 1:nslcs %bp for each slc
        if dates(i) == master_date
            continue %master, bp=0
        end
        bp_interp_tmp = bp;
        bp_interp_tmp0 = reshape(bp_interp_tmp(1:2:end),50,50)';
        bp_interp_tmp1000 = reshape(bp_interp_tmp(2:2:end),50,50)';
        if ver<=2009
            bp_interp0 = griddata(X,Y,bp_interp_tmp0,...
                Xq,Yq,'linear',{'QJ'});
            bp_interp1000=griddata(X,Y,bp_interp_tmp1000,...
                Xq,Yq,'linear',{'QJ'});
            bp_interp(:,i) = bp_interp0+(bp_interp1000-bp_interp0).*Z/1000;
        else
            bp_interp0=griddata(X,Y,bp_interp_tmp0,...
                Xq,Yq,'linear');
            bp_interp1000=griddata(X,Y,bp_interp_tmp1000,...
                Xq,Yq,'linear');
            bp_interp(:,i) = bp_interp0+(bp_interp1000-bp_interp0).*Z/1000;
        end
    end

    la_interp_tmp = la;
    la_interp_tmp0 = reshape(la_interp_tmp(1:2:end),50,50)';
    la_interp_tmp1000 = reshape(la_interp_tmp(2:2:end),50,50)';
    if ver<=2009
        la_interp0 = griddata(X,Y,la_interp_tmp0,Xq,Yq,'linear',{'QJ'});
        la_interp1000 = griddata(X,Y,la_interp_tmp1000,Xq,Yq,'linear',{'QJ'});
    else
        la_interp0 = griddata(X,Y,la_interp_tmp0,Xq,Yq,'linear');
        la_interp1000 = griddata(X,Y,la_interp_tmp1000,Xq,Yq,'linear');
    end
    
    la_interp = la_interp0 + (la_interp1000-la_interp0).*Z/1000;
    
end
master_ix = find(dates==master_date);
bp_interp(:,master_ix) = [];

end

