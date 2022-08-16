function [] = stamps_prep(folder,amp,n_patch_azi,n_patch_range,overlap_azi,overlap_range)
% Script to generate all required files for running the Standford Method
% for Persistent Scatters (StaMPS) on Sentinel-1 data
% 
% Does the initial PS selection (requires C code included in StaMPS).
%
% https://homepages.see.leeds.ac.uk/~earahoo/stamps/
% Consult the StaMPS manual for more details.
%
% This script replaces mt_prep
%
% ADD STAMPS PATH BEFORE RUNNING
%
% INPUT:
% Folder:           Name of StaMPS processing folder
% amp:              Amplitude Dispersion Threshold
% n_patch_azi:      Number of ratches in azimuth
% n_patch_range:    Number of ratches in range
% overlap_azi:      Overlapping pixels between patches in azimuth
% overlap_range:    Overlapping pixels between patches in range
% The number of patches you choose will depend on the size of your area 
% and the memory on your computer
%
% Required scripts:
% - la_bp.m
% - metadata.m
% - orbitfit.m
% - lph2xyz.m
% - xyz2t.m

%   Floris Heuff - 03/2018

finput = fopen('doris_input.xml');
temp = textscan(finput,'%s'); doris_input = temp{1,1};
fclose(finput);

master_date = doris_input{17}(14:end - 14); master_date(5) = []; master_date(7) = [];
master_date = str2double(master_date);

if ~(exist(fullfile(pwd,['StaMPS_',folder]),'dir') == 7)
    mkdir(['StaMPS_',folder])
end

%% files with links to files:
% open slcs
fslcs = fopen([folder,'/path_slcs.txt']);temp = textscan(fslcs,'%n %s'); slcs = temp{1,2}; dates = temp{1,1}; fclose(fslcs);
% open ifgs
fifgs = fopen([folder,'/path_ifgs.txt']); temp = textscan(fifgs,'%n %n %s'); ifgs = temp{1,3}; fclose(fifgs);
% open resfiles
fres = fopen([folder,'/path_res_files.txt']); temp = textscan(fres,'%s'); resfiles = temp{1,1}; fclose(fres);
% open coordinates
fcoords = fopen([folder,'/path_coords.txt']); temp = textscan(fcoords,'%s %s'); coords = temp{1,1}; fclose(fcoords);
fnlines  = load([folder,'/nlines_crp.txt']);
fnpixels = load([folder,'/npixels_crp.txt']);


nlines = fnlines(1);
npixels = fnpixels(1);

fid = fopen(resfiles{1});
mdata =textscan(fid,'%s','delimiter',':'); mdata = mdata{:};
fclose(fid);

ind      = find(strcmp('Radar_wavelength (m)',mdata));
lambda   = str2double(char(mdata(ind+1)));

%% calculate look angle and baselines

fnlines_f  = load([folder,'/nlines_crp.txt']);
fnpixels_f  = load([folder,'/npixels_crp.txt']);
l_off = fnlines_f(2) - 1;
p_off = fnpixels_f(2) - 1;

fl = 1 + l_off;
ll = fnlines(1) + 1 + l_off;
fp = 1 + p_off;
lp = fnpixels(1) + 1 + p_off;

grid_l=repmat(linspace(fl,ll,50)',1,50)';
grid_p=repmat(linspace(fp,lp,50),50,1)';

grid_list(1:2:4999,1:3)=[grid_l(:) grid_p(:) zeros(2500,1)];
grid_list(2:2:5000,1:3)=[grid_l(:) grid_p(:) repmat(1000,2500,1)];

[la,bp] = la_bp(grid_list(:,1),grid_list(:,2),grid_list(:,3),master_date,dates,resfiles);
bp_avg = mean(bp,1);

current_folder=pwd;
cd(['StaMPS_',folder])
addpath(current_folder);

%% calculate heading
% 
% calculate the exact heading (based on
% http://www.movable-type.co.uk/scripts/latlong.html)
lat_crop = freadbk(coords{1},nlines,'float32');
lon_crop = freadbk(coords{2},nlines,'float32');

lat_hw_u=lat_crop(1,floor(npixels/2));
lat_hw_d=lat_crop(end,floor(npixels/2));
% 
lon_hw_u=lon_crop(1,floor(npixels/2));
lon_hw_d=lon_crop(end,floor(npixels/2));
% 
a=sind(lon_hw_d-lon_hw_u)*cosd(lat_hw_d);
b=cosd(lat_hw_u)*sind(lat_hw_d)-sind(lat_hw_u)*cosd(lat_hw_d)*cosd(lon_hw_d-lon_hw_u);
% 
heading=atan2(a,b)*180/pi;

%% amplitude calibration
% make inputfile
fid = fopen('calamp.in','w');
fprintf(fid,'%s\n',slcs{:});
fclose(fid);

calamp=['!calamp calamp.in ',int2str(npixels),' calamp.out'];
eval(calamp)
%% patches

n_patch = 1;
p_npixels = round(npixels/n_patch_range);
p_nlines = round(nlines/n_patch_azi);
patch_id = fopen('patch.list','w');
for i = 1:n_patch_azi
    for j = 1:n_patch_range
        
        start_azi1 = p_nlines*(i-1)+1;
        start_azi = start_azi1 - overlap_azi;
        if start_azi < 0
            start_azi = 1;            
        end
        
        end_azi1 = p_nlines*i;
        end_azi = end_azi1 + overlap_azi;
        if end_azi > nlines
            end_azi = nlines;            
        end        
        
        start_range1 = p_npixels*(j-1)+1;
        start_range = start_range1 - overlap_range;
        if start_range < 0
            start_range = 1;            
        end
        
        end_range1 = p_npixels*j;
        end_range = end_range1 + overlap_range;
        if end_range > npixels
            end_range = npixels;            
        end
        
        patch = [start_range;end_range;start_azi;end_azi];
        patch1 = [start_range1;end_range1;start_azi1;end_azi1];
        
        dir_name = ['PATCH_',num2str(n_patch)];
        if ~(exist(fullfile(pwd,dir_name),'dir') == 7); mkdir(dir_name);end
        fprintf(patch_id,'%s\n',dir_name);
        cd(dir_name)
        fid = fopen('patch.in','w');
        fprintf(fid,'%i\n',patch);
        fclose(fid);
        fid = fopen('patch_noover.in','w');
        fprintf(fid,'%i\n',patch1);
        fclose(fid);
        n_patch = n_patch + 1; 
        cd ..        
    end
end
fclose(patch_id);



%% create input files

fid = fopen('len.txt','w');
fprintf(fid,'%i \n',nlines);
fclose(fid);

fid=fopen('width.txt','w');
fprintf(fid,'%i \n',npixels);
fclose(fid);

fid = fopen('heading.1.in','w');
fprintf(fid,'%f',heading);
fclose(fid);

fid = fopen('pscdem.in','w');
fprintf(fid,'%i \n',npixels);
fprintf(fid,coords{3});
fclose(fid);

fid = fopen('psclonlat.in','w');
fprintf(fid,'%i \n',npixels);
fprintf(fid,[coords{2},'\n']);
fprintf(fid,coords{1});
fclose(fid);

fid1=fopen('calamp.out');
fid2 = fopen('selpsc.in','w');
string = [num2str(amp),'\n',int2str(npixels),'\n'];
fprintf(fid2,string);
while 1
    text=fgetl(fid1);
    if ~ischar(text), break, end
    fprintf(fid2,'%s\n',text);
end
fclose(fid1);
fclose(fid2);

fid=fopen('pscphase.in','w');
fprintf(fid,'%i \n',npixels);
for i=1:length(ifgs)
    fprintf(fid,'%s \n',ifgs{i,:});
end;
fclose(fid);

%% run stamps ps selection

for i = 1 : n_patch_azi*n_patch_range
    workdir = pwd;
    dir_name = ['PATCH_',num2str(i)];
    cd(dir_name)
    
    eval(['!selpsc_patch ',workdir,'/selpsc.in patch.in pscands.1.ij pscands.1.da mean_amp.flt'])
    eval(['!psclonlat ',workdir,'/psclonlat.in pscands.1.ij pscands.1.ll'])
    eval(['!pscdem ',workdir,'/pscdem.in pscands.1.ij pscands.1.hgt'])
    eval(['!pscphase ',workdir,'/pscphase.in pscands.1.ij pscands.1.ph'])
    
    cd(workdir); 
end

fid=fopen('look_angle.1.in','w');
fprintf(fid,'%f\n',la);
fclose(fid);

sdates = dates(dates~=master_date);
for i = 1:length(sdates)
    name=['bperp_',int2str(sdates(i)),'.1.in'];
    fid=fopen(name,'w');
    fprintf(fid,'%f\n',bp(:,i));
    fclose(fid);
end

fid = fopen('len.txt','w');
fprintf(fid,'%i \n',nlines);
fclose(fid);

fid=fopen('width.txt','w');
fprintf(fid,'%i \n',npixels);
fclose(fid);

fid=fopen('master_day.1.in','w');
fprintf(fid,'%i \n',master_date);
fclose(fid);

fid=fopen('day.1.in','w');
fprintf(fid,'%i \n',sdates);
fclose(fid);

fid = fopen('slc_osfactor.1.in','w');
fprintf(fid,'%i',1);
fclose(fid);

fid = fopen('bperp.1.in','w');
fprintf(fid,'%i \n',bp_avg);
fclose(fid);

fid = fopen('lambda.1.in','w');
fprintf(fid,'%i \n',lambda);
fclose(fid);

fid = fopen('rho.1.in','w');
fprintf(fid,'%i \n',945);
fclose(fid);

fid = fopen('NLrate.1.in','w');
fprintf(fid,'%i \n',2.330);
fclose(fid);


diary('ps_parm_initial.log')
ps_parms_initial
diary off

cd(current_folder);
end

