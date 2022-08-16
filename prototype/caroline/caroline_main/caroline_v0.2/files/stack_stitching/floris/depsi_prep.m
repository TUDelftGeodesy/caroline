function depsi_prep(folder,id)
% Script to make a DePSI input file and create h2ph files. 
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

if ~(exist(fullfile(pwd,['DePSI_',folder]),'dir') == 7)
    mkdir(['DePSI_',folder])
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

m_ix = master_date==dates;
slave_dates = dates(~m_ix);

%% calculate h2ph and bp

l_off = fnlines(2) - 1;
p_off = fnpixels(2) - 1;

fl = 1 + l_off;
ll = fnlines(1) + 1 + l_off;
fp = 1 + p_off;
lp = fnpixels(1) + 1 + p_off;

grid_l=repmat(linspace(fl,ll,50)',1,50)';
grid_p=repmat(linspace(fp,lp,50),50,1)';

grid_list(1:2:4999,1:3)=[grid_l(:) grid_p(:) zeros(2500,1)];
grid_list(2:2:5000,1:3)=[grid_l(:) grid_p(:) repmat(1000,2500,1)];

[la,bp,h2ph] = la_bp(grid_list(:,1),grid_list(:,2),grid_list(:,3),master_date,dates,resfiles);
bp_avg = mean(bp,1);

%% interpolate h2ph to full resolution

dem = freadbk(coords{3},fnlines(1));
Nifg = length(ifgs);
h2ph_list = cell(Nifg,1);
output_list = cell(Nifg,1);

for i = 1:Nifg
    h2ph_0 = h2ph(1:2:end,i);
    h2ph_1 = h2ph(2:2:end,i);

    [full_l,full_p] = ndgrid(fnlines(2):fnlines(3),fnpixels(2):fnpixels(3));

    F0 = griddedInterpolant(grid_l',grid_p',reshape(h2ph_0,50,50)');
    F1 = griddedInterpolant(grid_l',grid_p',reshape(h2ph_1,50,50)');
    
    h2ph_full_0 = F0(full_l,full_p);
    h2ph_full_1 = F1(full_l,full_p);

    h2ph_full = h2ph_full_0 + (h2ph_full_1 - h2ph_full_0).*dem/1000;
    

    finfo = dir(ifgs{i});
    fpath = finfo.folder;
    h2ph_name = [fpath,'/h2ph_',id,'.raw'];
    h2ph_list{i} = h2ph_name;
    output_list{i} = [fpath,'/'];
    fwritebk(h2ph_full,h2ph_name);    
end

%% Make different time formats

date = [slave_dates; master_date];
date_str = datestr(datenum(num2str(date),'yyyymmdd'),'dd-mm-yyyy');
Bt = -(datenum(num2str(master_date),'yyyymmdd') - datenum(num2str(slave_dates),'yyyymmdd'))/365;

%% Make remaining input 

slc_list = [slcs(~m_ix); slcs(m_ix)];
ifg_list = ifgs; ifg_list{end+1} = 'dummy';
h2ph_list{end+1} = 'dummy';
output_list{end+1} = 'dummy';

Bp_list = [bp_avg';0];
Bt_list = [Bt;0];
Bdop_list = zeros(Nifg+1,1);
% 
% fl_list = ones(Nifg+1,1);
% ll_list = repmat(fnlines(1),Nifg+1,1);
% fp_list = ones(Nifg+1,1);
% lp_list = repmat(fnpixels(1),Nifg+1,1);


fl_list = repmat(fnlines(2),Nifg+1,1);
ll_list = repmat(fnlines(3),Nifg+1,1);
fp_list = repmat(fnpixels(2),Nifg+1,1);
lp_list = repmat(fnpixels(3),Nifg+1,1);

prnt = [date string(date_str) string(slc_list) string(ifg_list) string(h2ph_list)... 
    string(output_list) Bp_list Bt_list Bdop_list fl_list ll_list fp_list lp_list];

fid = fopen(['DePSI_',folder,'/depsi_input.txt'],'w');
fprintf(fid,'%s %s %s %s %s %s %s %s %s %s %s %s %s\n',prnt');
fclose(fid);


end

