function do_s1_crop(folder,crop_file)
    % Function to perform the cropping for Sentinel-1 output from DORIS 5.0.
    % Adapted from Floris Heuff, 2018
    % Created by Simon van Diepen, 02/2025

    % Get the list of images
    image_list = scan_directory();

    % Get the mother image index
    mother_idx = detect_mother_image(image_list);

    % Get the full link to the save file folder
    save_path = [fullfile(pwd),'/',folder];

    if ~(exist(save_path,'dir') == 7)
        mkdir(save_path);
    end

    % Read the resfile to extract the number of lines in the images
    fid = fopen(['stack/',image_list{mother_idx},'/master.res']);
    mdata =textscan(fid,'%s','delimiter',':');
    mdata = mdata{:};
    fclose(fid);

    ind = find(strcmp('Number_of_pixels_output_image',mdata));
    n_lines = str2double(char(mdata(ind+1)));

    % identify the bounding box
    if ~(exist([save_path,'/',image_list{mother_idx}],'dir')==7) | exist([save_path.'/nlines_crp.txt'],'file')==0
        % the mother date has not yet been cropped, so we need to crop from scratch
        [bounding_box_x,bounding_box_y] = estimate_shp_bounding_box(crop_file);

        % Read the lambda and phi files
        phi = freadbk(['stack/',image_list{mother_idx},'/phi.raw'],n_lines,'float32');
        lam = freadbk(['stack/',image_list{mother_idx},'/lam.raw'],n_lines,'float32');

        % identify the pixels inside the bounding box
        inliers = inpolygon(lam,phi,bounding_box_x,bounding_box_y);

        % convert to a bounding box in radar coordinates
        [indx(:,1),indx(:,2)] = ind2sub(size(inliers),find(inliers));
        bounding_box_radar = [min(indx) max(indx)];

        if (sum(sum(inliers))==0)
            error("WARNING: No overlap detected between requested crop and input stack! Aborting...")
        end

        % preserve the memory
        clearvars lam phi inliers;

        % write the crop files for n_lines and n_pixels
        fid = fopen([save_path,'/','nlines_crp.txt'],'w');
        fprintf(fid,'%i\n',bounding_box_radar(3) - bounding_box_radar(1) + 1);
        fprintf(fid,'%i\n',bounding_box_radar(1));
        fprintf(fid,'%i\n',bounding_box_radar(3));
        fclose(fid);

        fid = fopen([save_path,'/','npixels_crp.txt'],'w');
        fprintf(fid,'%i\n',bounding_box_radar(4) - bounding_box_radar(2) + 1);
        fprintf(fid,'%i\n',bounding_box_radar(2));
        fprintf(fid,'%i\n',bounding_box_radar(4));
        fclose(fid);

    else
        % the mother date has been cropped, so we can read the bounding box in radar coordinates from the saved files
        out = load([save_path,'/','nlines_crp.txt']);  % formatted as n_lines, min_line, max_line, we need the latter two
        bounding_box_radar(1) = out(2);
        bounding_box_radar(3) = out(3);
        out = load([save_path,'/','npixels_crp.txt']);  % formatted as n_pix, min_pix, max_pix, we need the latter two
        bounding_box_radar(2) = out(2);
        bounding_box_radar(4) = out(3);
    end

    % crop the images
    for i = 1:length(image_list)
        % single out the mother since its different
        if i == mother_idx
            % first check if the last crop file does not exist, otherwise we can skip
            if exist([save_path,'/',image_list{i},'/slc_srd.raw'],'file') == 0
                % check if the folder exists
                if ~(exist([save_path,'/',image_list{i}],'dir') == 7)
                    mkdir([save_path,'/',image_list{i}]);
                end

                % we need to crop the dem_radar, lambda and phi, slc_srd, and copy master.res
                crop(['stack/',image_list{i},'/dem_radar.raw'],n_lines,'float32',[save_path,'/',image_list{i},'/dem_radar.raw'],bounding_box_radar);
                crop(['stack/',image_list{i},'/lam.raw'],n_lines,'float32',[save_path,'/',image_list{i},'/lam.raw'],bounding_box_radar);
                crop(['stack/',image_list{i},'/phi.raw'],n_lines,'float32',[save_path,'/',image_list{i},'/phi.raw'],bounding_box_radar);
                crop(['stack/',image_list{i},'/slave_rsmp_reramped.raw'],n_lines,'cpxfloat32',[save_path,'/',image_list{i},'/slc_srd.raw'],bounding_box_radar);

                copyfile(['stack/',image_list{i},'/master.res'],[save_path,'/',image_list{i},'/master.res']);

                fprintf('Finished folder %s. \n',['stack/',image_list{i}])
            end
        else
            % first check if the last crop file does not exist, otherwise we can skip
            if exist([save_path,'/',image_list{i},'/h2ph.raw'],'file') == 0
                % check if the folder exists
                if ~(exist([save_path,'/',image_list{i}],'dir') == 7)
                    mkdir([save_path,'/',image_list{i}]);
                end
                % we need to crop cint_srd, h2ph and copy slave.res
                crop(['stack/',image_list{i},'/cint_srd.raw'],n_lines,'cpxfloat32',[save_path,'/',image_list{i},'/cint_srd.raw'],bounding_box_radar);
                crop(['stack/',image_list{i},'/h2ph_srd.raw'],n_lines,'float32',[save_path,'/',image_list{i},'/h2ph.raw'],bounding_box_radar);

                copyfile(['stack/',image_list{i},'/slave.res'],[save_path,'/',image_list{i},'/slave.res']);

                fprintf('Finished folder %s. \n',['stack/',image_list{i}])
            end
        end
    end

    % generate the daughter SLCs and their corresponding text files
    generate_slcs(image_list,mother_idx,save_path,bounding_box_radar)

    % generate the text files necessary for DePSI and DECADE
    system(['find ',save_path,'/*  -name ''*srd*.raw'' > ',save_path,'/path_images.txt']);
    system(['find ',save_path,'/*  -name ''*.res'' > ',save_path,'/path_res_files.txt']);
    system(['find ',save_path,'/*  -name ''phi','.raw'' > ',save_path,'/path_coords.txt']);
    system(['find ',save_path,'/*  -name ''lam','.raw'' >> ',save_path,'/path_coords.txt']);
    system(['find ',save_path,'/*  -name ''dem_radar','.raw'' >> ',save_path,'/path_coords.txt']);
    system(['cp stack/dir.txt ',save_path,'/dates.txt']);


end