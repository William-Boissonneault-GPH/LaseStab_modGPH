function [hIdeal, hActual] = computeGridLayoutHeights(~, gridLayoutObject)
%COMPUTEGRIDLAYOUTHEIGHTS Compute the ideal and actual heights of the
%grid layout component based on the child components.
%   Ideal: the height that ensures all child components are visible
%   Actual: the actual height (usually shorter), which uses a scrollbar

%   Copyright 2021 The MathWorks, Inc.

    childObjects = gridLayoutObject.Children;
    
    minY = inf;
    maxY = -inf;
    minPosY = inf;
    
    for childIdx = length(childObjects):-1:1
        bottom = childObjects(childIdx).Position(2);
        height = childObjects(childIdx).Position(4);

        top = bottom + height;
        
        if top > maxY
            maxY = top;
        end
        
        if bottom < minY
            minY = bottom;
        end
        
        if (bottom > 0 && bottom < minPosY)
            minPosY = bottom;
        end
    end
    
    hIdeal = maxY - minY + 1;
    hActual = maxY - minPosY + 1;
end
