function reflowAxesGLContents(obj)
%REFLOWAXESGLCONTENTS Update the heights of all plot axes in the app to fit
%the current view using some heuristics.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    useMinAxesHeightConditionally(app) || ...
    useSplitViewMinAxesHeightConditionally(app) || ...
    useDefaultAxesHeight(app); %#ok<VUNUS>
end

% -------------------------------------------------------------------------
% Local functions
% -------------------------------------------------------------------------

function TF = containerHeightBelowTotalAxesMinHeight(app)
    containerHeight = computedResultsGLHeight(app);
    totalAxesMinHeight = activeViewTotalAxesMinHeight(app);

    TF = containerHeight < totalAxesMinHeight;
end

% -------------------------------------------------------------------------

function TF = numAxesRowsAboveCountThreshold(app)
    numAxesRows = app.NumAxesRows.Value;    
    countThreshold = maxRowsBeforeScroll(app);

    TF = numAxesRows > countThreshold;
end

% -------------------------------------------------------------------------

function useMinAxesHeight = useMinAxesHeightConditionally(app)

    chk1 = containerHeightBelowTotalAxesMinHeight(app);
    chk2 = splitViewIsActive(app) && numAxesRowsAboveCountThreshold(app);
    chk3 = ~splitViewIsActive(app);
    
    useMinAxesHeight = chk1 && (chk2 || chk3);

    if useMinAxesHeight
        updateAxesGLRowHeight(app, app.Helper.MinAxesHeight);
    end
end

% -------------------------------------------------------------------------

function useSplitViewMinAxesHeight = useSplitViewMinAxesHeightConditionally(app)

    chk1 = containerHeightBelowTotalAxesMinHeight(app);
    chk2 = splitViewIsActive(app);
    chk3 = ~numAxesRowsAboveCountThreshold(app);

    useSplitViewMinAxesHeight = (chk1 && chk2 && chk3);

    if useSplitViewMinAxesHeight
        updateAxesGLRowHeight(app, app.Helper.MinAxesHeightSplitView);
    end
end

% -------------------------------------------------------------------------

function TF = useDefaultAxesHeight(app)
    rowHeight = {'1x'};
    updateAxesGLRowHeight(app, rowHeight);
    TF = true;    
end

% -------------------------------------------------------------------------

function updateAxesGLRowHeight(app, rowHeight)
    app.AxesGL.RowHeight = repmat(rowHeight, 1, app.NumAxesRows.Value);
end

% -------------------------------------------------------------------------

function resultsGLHeight = computedResultsGLHeight(app)
    resultsGLHeight = app.MainGL.RowHeight{4};
    
    excludedResultsGLHeights = app.ResultsGL.RowSpacing + ...
            app.PlotRefreshRateHzSliderLabel.Position(4);

    if ~isequal(resultsGLHeight, '1x') % split-view case
        resultsGLHeight = resultsGLHeight - excludedResultsGLHeights;
        return;
    end

    resultsGLHeight = ...
        app.GUI.Position(4) - ... app height
        app.MainGL.Padding(4) - ... top padding
        app.MainGL.Padding(2) - ... bottom padding
        app.RunPauseResumeButton.Position(4) - ... ControlsGL height
        app.ScrollUpUIC.Position(4) - ... SimControlsGL height
        app.MainGL.RowSpacing - ... space between ControlsGL & ResultsGL
        excludedResultsGLHeights; % space between axes and PlotControlsGL
                                  % and height of PlotControlsGL
end

% -------------------------------------------------------------------------

function TF = splitViewIsActive(app)
    TF = app.ScrollDownUIC.Enable && app.ScrollUpUIC.Enable;
end

% -------------------------------------------------------------------------

function maxRows = maxRowsBeforeScroll(app)
    maxRows = app.Helper.MaxAxesRowsBeforeScroll;

    if splitViewIsActive(app)
        maxRows = app.Helper.MaxAxesRowsBeforeScrollSplitView;
    end
end

% -------------------------------------------------------------------------

function rowHeight = activeViewMinAxesHeight(app)
    rowHeight = app.Helper.MinAxesHeight;

    if splitViewIsActive(app)
        rowHeight = app.Helper.MinAxesHeightSplitView;
    end
end

% -------------------------------------------------------------------------

function totalAxesMinHeight = activeViewTotalAxesMinHeight(app)
    totalAxesMinHeight = ...
        totalAxesHeightWithSpaces(app, activeViewMinAxesHeight(app));
end

% -------------------------------------------------------------------------

function heightWithSpaces = totalAxesHeightWithSpaces(app, heightWithoutSpaces)
    heightWithSpaces = ...
        heightWithoutSpaces * app.NumAxesRows.Value + ...
        app.AxesGL.Padding(2) + app.AxesGL.Padding(4) + ...
        app.AxesGL.RowSpacing * (app.NumAxesRows.Value - 1);
end

% LocalWords:  GL
