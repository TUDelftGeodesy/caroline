function create_slcs(folder,id)
% Make SLCs from interferograms. 
% ifg = master.*conj(slave);
% slave = master.*conj(ifg)./abs(master.^2);
%
% OUTPUT:
% SLCs which can be combined to make different interferograms (N*(N-1)/2
% combinations)
% Textfiles with filepaths of the SLCs and interferograms
% 
% Floris Heuff - 03/2018

fid = fopen([folder,'/path_images.txt']);
temp = textscan(fid,'%s');
ifgs = temp{1,1};
fclose(fid);
dates = load([folder,'/dates.txt']);

finput = fopen('doris_input.xml');
temp = textscan(finput,'%s'); doris_input = temp{1,1};
fclose(finput);
master_date = doris_input{17}(14:end - 14); master_date(5) = []; master_date(7) = [];
master_date = str2double(master_date);

nifgs = length(dates) - 1;
m_ind = find(dates == master_date);
s_ind = 1:length(dates);    
s_ind(m_ind)=[];
ifg_inds = [repmat(m_ind,nifgs,1) s_ind'];   

fifg = fopen([folder,'/path_ifgs.txt'],'w');
fslc = fopen([folder,'/path_slcs.txt'],'w');
master = freadbk([pwd,'/',folder,'/',num2str(master_date),'/slc_srd_',id,'.raw'],1,'cpxfloat32'); % PC: Where does this come from?
for i = 1:length(dates)
    slc_name = [pwd,'/',folder,'/',num2str(dates(i)),'/slc_srd_',id,'.raw'];
    cint_name = [pwd,'/',folder,'/',num2str(dates(i)),'/cint_srd_',id,'.raw'];
    
    % PC: Generate a new SLC from the given interferogram
    if exist(slc_name,'file') == 0 && i ~= m_ind
        ifg = freadbk(ifgs{i},1,'cpxfloat32');
        slc = master.*conj(ifg)./(abs(master).^2);
        slc(isnan(slc))=complex(0,0);
        fwritebk(slc,slc_name,'cpxfloat32');        
    end
    
    % PC: write all ifg paths to a text file: master_date slave_date path
    if i~=m_ind
        fprintf(fifg,'%i %i %s\n',master_date,dates(i),cint_name); 
    end
    
    % PC: write all slc paths to a text file: slc_date path
    fprintf(fslc,'%i %s\n',dates(i),slc_name);
end
fclose(fifg);       
fclose(fslc);       
    

end

