function assetsFolder = getAssetsFolder()
%GETASSETSFOLDER Get the assets folder path.

%   Copyright 2021 The MathWorks, Inc.

    directoryLevel = 2;
    assetsParentDirectory = getParentDirectory(mfilename("fullpath"), directoryLevel);
    assetsFolder = fullfile(assetsParentDirectory, 'assets');
end

function parentDir = getParentDirectory(path, dirLevel)
    parentDir = path;
    for idx = 1 : dirLevel
        parentDir = fileparts(parentDir);
    end
end