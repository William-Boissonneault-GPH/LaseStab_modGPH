function maxHeight = computeMaxAllowedViewHeight(obj)
%COMPUTEMAXALLOWEDVIEWHEIGHT Compute the height available for content after
%removing whitespaces and fixed controls' heights.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    appHeight = app.GUI.Position(4);
    remainingHeights = nonViewportHeights(app);
    maxHeight = appHeight - remainingHeights;
end

% -------------------------------------------------------------------------

function heights = nonViewportHeights(app)
    topPadding = app.MainGL.Padding(4);
    bottomPadding = app.MainGL.Padding(2);
    numMainGLRows = numel(app.MainGL.RowHeight);
    mainGLTotalRowSpacing = (numMainGLRows - 1) * app.MainGL.RowSpacing;
    controlsGLHeight = app.RunPauseResumeButton.Position(4);
    simControlsGLHeight = app.ScrollUpUIC.Position(4);

    heights = ...
        topPadding + ...
        simControlsGLHeight + ...
        mainGLTotalRowSpacing + ...
        controlsGLHeight + ...
        bottomPadding;
end
