function setImagePaths(obj)
%SETIMAGEPATHS Dynamically set paths of images used by the app buttons.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    app.ScrollTopLeftUIC.Icon = locImagePath('ArrowLeft.svg');
    app.ScrollTopRightUIC.Icon = locImagePath('ArrowRight.svg');
    
    app.ScrollUpUIC.Icon = locImagePath('ArrowUp.svg');
    app.ScrollDownUIC.Icon = locImagePath('ArrowDown.svg');

    app.ScrollBottomLeftUIC.Icon = locImagePath('ArrowLeft.svg');
    app.ScrollBottomRightUIC.Icon = locImagePath('ArrowRight.svg');

    app.RunPauseResumeButton.Icon = locImagePath('icon_run.png');
    app.StopButton.Icon = locImagePath('icon_stop.png');

end

function path = locImagePath(image)
    imagesPath = fullfile(AppHelper.getAssetsFolder(), 'images');
    path = fullfile(imagesPath, image);
end

% LocalWords:  svg
