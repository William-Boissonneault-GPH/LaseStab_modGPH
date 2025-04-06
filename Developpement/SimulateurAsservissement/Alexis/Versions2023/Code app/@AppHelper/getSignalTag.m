function sigTag = getSignalTag(~, sectionTitle, datasetIdx, signalIdx)

%   Copyright 2021 The MathWorks, Inc.

    sigTag = join([string(sectionTitle) ...
                   string(num2str(datasetIdx)) ...
                   string(num2str(signalIdx))], ",");
    
end % getSignalTag
