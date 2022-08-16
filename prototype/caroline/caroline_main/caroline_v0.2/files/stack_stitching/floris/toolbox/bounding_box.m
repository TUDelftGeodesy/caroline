function [bb_ind] = bounding_box(x,y,x_p,y_p)
% Gives the bounding box of the polygon specified with x_p and y_p. If only
% two polygon coordinates are given, it is assumed the polygon is square
% with x_p and y_p the coordinates of the diagionally opposite corners.
%
%   INPUT:
%   x:          matrix with for example longitude values.
%   y:          matrix with for example latitude values.
%   x_p:        x coordinates of polygon
%   y_p:        y coordinates of polygon
%
%   OUTPUT
%   bb_ind:   returns the subscript values of the top left corner and bottom right
%   corner [top_left,bottom_right] of the bounding box.
%
%   Floris Heuff - 09/2017

if length(x_p) ~= length(y_p)
    error('x_p and y_p must be the same length')
end

if length(x_p) < 2
    error('specify atleast 2 points of the polygon')
end


if length(x_p) == 2

    if x_p(1) == x_p(2) || y_p(1) == y_p(2)
        error('top and bottom are not diagonally opposite')        
    end
    
    x_p=[min(x_p),max(x_p),max(x_p),min(x_p)];
    y_p=[min(y_p),min(y_p),max(y_p),max(y_p)];

end
    in = inpolygon(x,y,x_p,y_p);
    [ind(:,1),ind(:,2)] = ind2sub(size(in),find(in));
    bb_ind = [min(ind) max(ind)];   
    
end
