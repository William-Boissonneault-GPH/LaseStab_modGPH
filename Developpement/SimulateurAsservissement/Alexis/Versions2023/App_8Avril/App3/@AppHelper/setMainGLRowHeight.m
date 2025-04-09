function setMainGLRowHeight(obj)
%SETMAINGLROWHEIGHT Proportionally set row heights of the main grid layout
%based on content so that the app looks aesthetically pleasing.
%   Use the Golden Ratio along with some heuristics to set the heights of
%   various app panes. This method also shows/hides panes based on scroll
%   button states.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    assert(app.initialized);
    
    if setupGLIsHidden(app)
        collapseTopRow(app);

    elseif resultsGLIsHidden(app)
        collapseBottomRow(app);

    else
        makeSetupAndResultsGLProportional(app);
    end

    app.Helper.reflowAxesGLContents();

    % Change data on the model view to initiate a fit-to-view action
    app.ModelHTML.Data = rand;
end

% -------------------------------------------------------------------------
% Local functions
% -------------------------------------------------------------------------

function TF = setupGLIsHidden(app)
    TF = ~app.ScrollUpUIC.Enable;
end

% -------------------------------------------------------------------------

function TF = resultsGLIsHidden(app)
    TF = ~app.ScrollDownUIC.Enable;
end

% -------------------------------------------------------------------------

function collapseTopRow(app)
    topRowHeight = AppHelper.SimControlsButtonSize;
    app.MainGL.RowHeight = {topRowHeight, 0,'fit','1x'};
end

% -------------------------------------------------------------------------

function collapseBottomRow(app)
    topRowHeight = AppHelper.SimControlsButtonSize;
    app.MainGL.RowHeight = {topRowHeight, '1x','fit',0};
end

% -------------------------------------------------------------------------

function makeSetupAndResultsGLProportional(app)
    hIdealForPrmsGL = app.Helper.computeGridLayoutHeights(app.PrmsGL);
    hIdealForSigsGL = app.Helper.computeGridLayoutHeights(app.SigsGL);
    hIdealForAxesGL = computeIdealAxesGLHeight(app);
    
    ensureWithinAppHeight(app, hIdealForPrmsGL, ...
        max(hIdealForAxesGL, hIdealForSigsGL));
end

% -------------------------------------------------------------------------

function ensureWithinAppHeight(app, prmsGLHeight, sigsOrAxesGLHeight)
    maxAllowedHeight = app.Helper.computeMaxAllowedViewHeight();
    halfHeight = maxAllowedHeight/2;
    heightSum = prmsGLHeight + sigsOrAxesGLHeight;

    if heightSum ~= maxAllowedHeight
        if sigsOrAxesGLHeight <= prmsGLHeight
            prmsGLHeight = halfHeight;
            sigsOrAxesGLHeight = halfHeight;
        else
            goldenRatio = ( 1 + sqrt(5) ) / 2;
            sigsOrAxesGLHeight = maxAllowedHeight/goldenRatio;
            prmsGLHeight = maxAllowedHeight - sigsOrAxesGLHeight;
        end
    end

    topRowHeight = AppHelper.SimControlsButtonSize;
    app.MainGL.RowHeight = {topRowHeight, prmsGLHeight, 'fit', sigsOrAxesGLHeight};
end

% -------------------------------------------------------------------------

function idealAxesGLHeight = computeIdealAxesGLHeight(app)
    numAxes= numel(findobj(app.AxesGL, 'Type', 'axes'));
    maxAllowedHeight = app.Helper.computeMaxAllowedViewHeight();
    goldenRatio = ( 1 + sqrt(5) ) / 2;

    idealAxesGLHeight = maxAllowedHeight - maxAllowedHeight/goldenRatio;
    if numAxes > 1
        idealAxesGLHeight = maxAllowedHeight;
    end
end
