function create_slcs(image_list,mother_index,save_path,bounding_box_radar)
    % Make SLCs from interferograms.
    % ifg = mother.*conj(daughter);
    % slave = mother.*conj(ifg)./abs(mother.^2);
    %
    % OUTPUT:
    % SLCs which can be combined to make different interferograms (N*(N-1)/2
    % combinations)
    % Textfiles with filepaths of the SLCs and interferograms
    %
    % Floris Heuff - 03/2018
    %
    % Adapted by P. Conroy - 2023
    %
    % Adapted to s1_crop by Simon van Diepen - 02/2025

    % calculate the number of lines in the crop
    n_lines_crop = bounding_box_radar(3) - bounding_box_radar(1) + 1

    % read the mother SLC
    mother = freadbk([save_path,'/',image_list{mother_index},'/slc_srd.raw'],n_lines_crop,'cpxfloat32');

    % open the text files to write the filenames
    fifg = fopen([save_path,'/path_ifgs.txt'],'w');
    fslc = fopen([save_path,'/path_slcs.txt'],'w');

    % loop over the image list
    for i = 1:length(image_list)

        % generate the SLC and interferogram names
        slc_name = [save_path,'/',image_list{i},'/slc_srd.raw'];
        cint_name = [save_path,'/',image_list{i},'/cint_srd.raw'];

        % PC: Generate a new SLC from the given interferogram, skipping the mother
        if exist(slc_name,'file') == 0 && i ~= mother_index
            ifg = freadbk(cint_name,n_lines_crop,'cpxfloat32');
            slc = mother.*conj(ifg)./(abs(mother).^2);
            slc(isnan(slc))=complex(0,0);
            fwritebk(slc,slc_name,'cpxfloat32');
        end

        % PC: write all ifg paths to a text file: mother_date daughter_date path
        if i ~= mother_index
            fprintf(fifg,'%s %s %s\n',image_list{mother_index},image_list{i},cint_name);
        end

        % PC: write all slc paths to a text file: slc_date path
        fprintf(fslc,'%s %s\n',image_list{i},slc_name);
    end

    % close the files
    fclose(fifg);
    fclose(fslc);
end

