function [list_of_images] = scan_directory()
    % Scan the directories of DORIS 5.0 output to detect all images.
    %
    % Output: a struct with the list of image dates
    % Floris Heuff - 03/2018
    %
    % Adapted and functionized by Simon van Diepen - 02/2025

    % Move into the stack directory
    workdir = pwd;
    cd('stack');

    % Collect the dates into dir.txt
    system('ls -d [1,2]* > dir.txt');

    % Scan the file and collect all images
    fdir = fopen('dir.txt');
    temp = textscan(fdir,'%s');
    list_of_images = temp{1,1};
    fclose(fdir);

    % Move back to the original directory
    cd(workdir);
end