function [bb] = stitch_master_image(folder,new_folder,id,bounds)
% Stitch together the master image, as well as the coordinate and DEM
% files. The bounding box is also calculated. The bounding box is used in
% stitch_slave_image.m

% Floris Heuff - 03/2018
    
    %% Reading of master files

    system(['find "$(pwd -P)/',folder,'"/*/* -name ''*slave_iw_?_burst_?.raw'''...
        ' -o -name ''phi.raw'' -o -name ''lam.raw'' -o -name ''dem_radar.raw'' > image_path_',folder(7:end),'.txt']);
    fimg = fopen(['image_path_',folder(7:end),'.txt']);
    temp = textscan(fimg,'%s'); img = sort(temp{1,1});
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
    elseif ~(exist([save_path,'/',folder(7:end),'/slc_srd_',id,'.raw'],'file') == 0)
        out = load([save_path,'/','nlines_crp.txt']); 
        bb(1) = out(2); bb(3) = out(3);
        out = load([save_path,'/','npixels_crp.txt']);
        bb(2) = out(2); bb(4) = out(3);

       return       
    end

    
    %% Stitch them together
        
    slc_stitch = zeros(tl,tp);
    phi_stitch = zeros(tl,tp); 
    lam_stitch = zeros(tl,tp);
    dem_radar_stitch = zeros(tl,tp);
    n_img = length(img)/4;
   
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

        slc = freadbk(img{4*i-0},nlines,'cpxint16');
        phi = freadbk(img{4*i-1},nlines,'float32');
        lam = freadbk(img{4*i-2},nlines,'float32');
        dem_radar = freadbk(img{4*i-3},nlines,'float32');

        slc_stitch(fl:ll,fp:lp) = slc(21:end-20,51:end-50);
        phi_stitch(fl:ll,fp:lp) = phi(21:end-20,51:end-50);
        lam_stitch(fl:ll,fp:lp) = lam(21:end-20,51:end-50);
        dem_radar_stitch(fl:ll,fp:lp) = dem_radar(21:end-20,51:end-50);       
    end
    
    %% Crop image
    if ischar(bounds)
        S = shaperead(bounds);                
        x_p = S.BoundingBox(:,1); y_p = S.BoundingBox(:,2);
        bb = bounding_box(lam_stitch,phi_stitch,x_p,y_p);
    elseif isnumeric(bounds) && ~isempty(bounds)
        x_p = bounds(:,1);
        y_p = bounds(:,2);
        bb = bounding_box(lam_stitch,phi_stitch,x_p,y_p);
    else
        bb = [1 1 tl tp];
    end
    
  
    slc_crp = slc_stitch(bb(1):bb(3),bb(2):bb(4));
    dem_radar_crp = dem_radar_stitch(bb(1):bb(3),bb(2):bb(4)); 
    phi_crp = phi_stitch(bb(1):bb(3),bb(2):bb(4)); 
    lam_crp = lam_stitch(bb(1):bb(3),bb(2):bb(4)); 
    
    
    %% Write new files

    
    fwritebk(slc_crp,[save_path,'/',folder(7:end),'/slc_srd_',id,'.raw'],'cpxfloat32');
    fwritebk(dem_radar_crp,[save_path,'/',folder(7:end),'/dem_radar_',id,'.raw'],'float32');
    fwritebk(phi_crp,[save_path,'/',folder(7:end),'/phi_',id,'.raw'],'float32');
    fwritebk(lam_crp,[save_path,'/',folder(7:end),'/lam_',id,'.raw'],'float32');   
    
    fid = fopen([save_path,'/','nlines_crp.txt'],'w');
    fprintf(fid,'%i\n',bb(3) - bb(1) +1);
    fprintf(fid,'%i\n',bb(1));
    fprintf(fid,'%i\n',bb(3));  
    fclose(fid);
    
    fid = fopen([save_path,'/','npixels_crp.txt'],'w');
    fprintf(fid,'%i\n',bb(4) - bb(2) +1);
    fprintf(fid,'%i\n',bb(2));
    fprintf(fid,'%i\n',bb(4));  
    fclose(fid);
    
    system(['find "$(pwd -P)/',folder,'" -maxdepth 2 -name ''*master.res'' -exec cp {} ',save_path,'/',folder(7:end),'/ \;']);    

end
