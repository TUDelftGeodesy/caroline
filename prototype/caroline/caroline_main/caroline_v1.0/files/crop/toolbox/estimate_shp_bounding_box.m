function [x_p,y_p] = bounding_box(shapefile)
    % Reads a shapefile and outputs the x and y coordinates of the bounding box.
    %
    %   Floris Heuff - 09/2017
    % Adapted and functionized by Simon van Diepen, 02/2025

    % Read the shapefile
    S = shaperead(shapefile);

    % get the bounding box
    bbox = S.BoundingBox;
    x_p = bbox(:,1);
    y_p = bbox(:,2);

    % format the bounding box to a box
    x_p=[min(x_p),max(x_p),max(x_p),min(x_p)];
    y_p=[min(y_p),min(y_p),max(y_p),max(y_p)];

end
