function crop(input_path, n_lines, format, output_path, radar_bounding_box)
    % Crop the image in input_path (consisting of n_lines lines) with the radar_bounding_box, and write to output_path
    %
    % Output: the cropped image
    %
    % Floris Heuff - 03/2018
    %
    % Adapted and functionized by Simon van Diepen - 02/2025

    % Read the file
    data = freadbk(input_path,n_lines,format);

    % crop the data
    cropped_data = data(radar_bounding_box(1):radar_bounding_box(3),radar_bounding_box(2):radar_bounding_box(4));

    % write the data
    fwritebk(cropped_data,output_path,format);

end
