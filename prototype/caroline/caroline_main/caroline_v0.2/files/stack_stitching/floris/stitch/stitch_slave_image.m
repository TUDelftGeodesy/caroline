function stitch_slave_image(folder,new_folder,id,bb)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here

    %% Reading of slave files
    
    system(['find "$(pwd -P)/',folder,'"/*/*  -name ''*cint_srd.raw'' > image_path_',folder(7:end),'.txt']);
    fimg = fopen(['image_path_',folder(7:end),'.txt']);
    temp = textscan(fimg,'%s'); img = temp{1,1};
    fclose(fimg);
    delete(['image_path_',folder(7:end),'.txt']);
    
    system(['find "$(pwd -P)/',folder,'"/*/*  -name ''*master.res'' > res_path_',folder(7:end),'.txt']);
    fres = fopen(['res_path_',folder(7:end),'.txt']);
    temp = textscan(fimg,'%s'); res = temp{1,1};
    fclose(fres);
    delete(['res_path_',folder(7:end),'.txt']);
    
    fid = fopen(res{1});
    mdata =textscan(fid,'%s','delimiter',':'); mdata = mdata{:};
    fclose(fid);
    
    %% Size of concatenated bursts
    
    ind      = find(strcmp('Number_of_lines_output_image',mdata));
    tl      = str2double(char(mdata(ind+1)));
    ind      = find(strcmp('Number_of_pixels_output_image',mdata));
    tp      = str2double(char(mdata(ind+1)));
    
    %% check if already done
    
    save_path = fullfile(pwd);
    save_path = [save_path,'/',new_folder];   
    
    if ~(exist([save_path,'/',folder(7:end)],'dir')==7)
        mkdir([save_path,'/',folder(7:end)])
    elseif ~(exist([save_path,'/',folder(7:end),'/cint_srd_',id,'.raw'],'file') == 0)
       return       
    end
    
    %% Stitch them together
    
    ifg_stitch = zeros(tl,tp);    
    n_img = length(img);    
    for i = 1:n_img
        
        fid = fopen(res{i});
        mdata =textscan(fid,'%s','delimiter',':'); mdata = mdata{:};
        fclose(fid);    

        ind      = find(strcmp('First_line (w.r.t. output_image)',mdata));
        fl      = str2double(char(mdata(ind+1))) + 20;
        ind      = find(strcmp('Last_line (w.r.t. output_image)',mdata));
        ll      = str2double(char(mdata(ind+1))) - 20;
        ind      = find(strcmp('First_pixel (w.r.t. output_image)',mdata));
        fp      = str2double(char(mdata(ind+1))) + 50;
        ind      = find(strcmp('Last_pixel (w.r.t. output_image)',mdata));
        lp      = str2double(char(mdata(ind+1))) - 50;

        nlines = ll - fl + 41;        
        ifg = freadbk(img{i},nlines,'cpxfloat32');
        ifg_stitch(fl:ll,fp:lp) = ifg(21:end-20,51:end-50);       
        
    end
    
    if ~(exist(['../',new_folder],'dir')==7)
        mkdir(['../',new_folder]);
    end  
    
    %% Write new file

    
    ifg_crp = ifg_stitch(bb(1):bb(3),bb(2):bb(4));    
    fwritebk(ifg_crp,[save_path,'/',folder(7:end),'/cint_srd_',id,'.raw'],'cpxfloat32');
    
    system(['find "$(pwd -P)/',folder,'" -maxdepth 2 -name ''*slave.res'' -exec cp {} ',save_path,'/',folder(7:end),'/ \;']);
   
end
