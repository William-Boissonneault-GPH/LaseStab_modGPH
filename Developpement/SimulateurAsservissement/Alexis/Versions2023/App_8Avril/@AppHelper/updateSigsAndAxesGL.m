function updateSigsAndAxesGL(obj, autoSelectFirstLoggedSignal)
%UPDATESIGSANDAXESGL Set up or update signal checkboxes using the mechanism
%the method creates for associating them with plots of the selected axes.
%   Ensure that signal checkboxes always reflect the signals plotted on the
%   currently selected axes.

%   Copyright 2021 The MathWorks, Inc.

    arguments
        obj
        autoSelectFirstLoggedSignal (1,1) logical = true
    end
    app = obj.App;

    lh = findobj(app.SigsGL,'Tag','signals_placeholder');
    if ~isempty(lh), delete(lh); end

    inpSigDS = app.modelData.inputSignals;
    logSigDS = app.modelData.loggedSignals;

    nRows = 0;
    if ~isempty(inpSigDS)
        inpSigHeading = message("simulinkcompiler:genapp:InputSignals").string;
        nRows = locSetupSigSelector(obj, nRows, inpSigDS, inpSigHeading);
    end

    isDataset = isa(logSigDS, 'Simulink.SimulationData.Dataset');
    isSupportedType = isDataset || isnumeric(logSigDS);
    
    if isSupportedType && ~isempty(logSigDS)
        obj.debugTrace('Updating plots');
        logSigHeading = message("simulinkcompiler:genapp:LoggedSignals").string;
        nRows = locSetupSigSelector(obj, nRows, logSigDS, logSigHeading);
    end

    if isempty(inpSigDS) && isempty(logSigDS)
        locCreateNoSignalsLabel(app);
        nRows = 1;
    end

    app.SigsGL.RowHeight = [repmat({'fit'},1,nRows), {'1x'}];

    if autoSelectFirstLoggedSignal
        % if there are logged signals and no signals have been selected then select the first logged
        % signal so that something interesting is plotted
        cbxes = findobj(app.SigsGL,'Type','uicheckbox');
        if ~isempty(cbxes) && ~any([cbxes.Value]) && ~isempty(logSigDS)
            sigTag = obj.getSignalTag(logSigHeading,1,1);
            cbx = findobj(app.SigsGL,'Type','uicheckbox','Tag',sigTag);
            cbx.Value = 1;
            selectionEvent.Source = cbx;
            locSigSelectionFcn(app, selectionEvent);
        end
    end
end

%%
function nRows = locSetupSigSelector(obj, nRows, sigDS, sectionTitle)

    import simulink.compiler.internal.getNamesForDatasetSignals
    import simulink.compiler.internal.util.plotTimeSeries

    app = obj.App;
    
    nRows = nRows+1;
    lbl = findobj(app.SigsGL,'Type','uilabel','Text',sectionTitle);
    if isempty(lbl)
        lbl = uilabel(app.SigsGL);
        lbl.Layout.Row = nRows;
        lbl.Layout.Column = 1;
        lbl.HorizontalAlignment = 'left';
        lbl.Text = sectionTitle;
        lbl.FontWeight = 'Bold';
    end

    axs = findobj(app.AxesGL, 'Type','axes');
    naxs = numel(axs);

    if isnumeric(sigDS)
        sigDS = locConvertNumericSignalsToDataset(sigDS);
    end

    nSigDS = numel(sigDS);
    for iDS = 1:nSigDS
        % TS and ts are abbreviations of "time series"

        dataset = sigDS(iDS);
        signalsAndNamesStruct = getNamesForDatasetSignals(dataset);

        for sIdx = 1:length(signalsAndNamesStruct)

            signalTS = signalsAndNamesStruct(sIdx).signalObject;
            signalNames = signalsAndNamesStruct(sIdx).signalNames;
            sigTag = obj.getSignalTag(sectionTitle, iDS, sIdx);

            % if this signal is plotted in any of the axes, delete the
            % corresponding lines and redraw with the new signalTS
            for iax=1:naxs
                lineHandles = findobj(axs(iax),'Tag',sigTag);
                if isempty(lineHandles), continue; end
                lineColors = lineHandles.Color;
                delete(lineHandles);
                lineHandles = plotTimeSeries(signalTS, axs(iax));
                set(lineHandles,'Color',lineColors);
                legend(axs(iax), 'Interpreter', 'none');

                % lh can be a non-scalar if the signal consists of multiple lines
                for lineHandle = reshape(lineHandles, 1, numel(lineHandles))
                    lineHandle.Tag = sigTag;
                end
            end
            
            nRows = nRows+1;
            cbx = findobj(app.SigsGL,'Type','uicheckbox','Tag', sigTag);
            if ~isempty(cbx)
                lbl = findobj(app.SigsGL,'Type','uilabel','Tag', sigTag);
                assert(~isempty(lbl));
                continue;
            end

            if isscalar(signalNames)
                sigName = signalNames;
            else
                % Multiline timeseries, i.e. all lines have same
                % unsubscripted name, hence use first.
                sigName = extractBefore(signalNames(1), '(1)');
            end

            lbl = uilabel(app.SigsGL);
            lbl.Layout.Row = nRows;
            lbl.Layout.Column = 1;
            lbl.HorizontalAlignment = 'left';
            lbl.Text = sigName;
            lbl.Tag = sigTag;
            
            cbx = uicheckbox(app.SigsGL);
            cbx.Text = '';
            cbx.Tag = sigTag;
            cbx.Layout.Row = nRows;
            cbx.Layout.Column = 2;
            cbx.ValueChangedFcn = app.createCallbackFcnProxy( ...
                @locSigSelectionFcn, true);
        end
    end
    for iax=1:naxs
        locUpdateAxesXLim(axs(iax));
    end
end

%%
function locSigSelectionFcn(app, event)

    import simulink.compiler.internal.getNamesForDatasetSignals
    import simulink.compiler.internal.util.plotTimeSeries

    cbx = event.Source;
    inpSigHeading = message("simulinkcompiler:genapp:InputSignals").getString;
    logSigHeading = message("simulinkcompiler:genapp:LoggedSignals").getString;

    if cbx.Value
        tags = split(cbx.Tag,",");
        if isequal(tags{1}, inpSigHeading)
            sigDS = app.modelData.inputSignals;
            if isnumeric(sigDS)
                sigDS = locConvertNumericSignalsToDataset(sigDS);
            end
        else
            assert(isequal(tags{1}, logSigHeading));
            sigDS = app.modelData.loggedSignals;
        end
        iDS = eval(tags{2});
        sIdx = eval(tags{3});
        dataset = sigDS(iDS);

        signalsAndNamesStruct = getNamesForDatasetSignals(dataset);
        signalTS = signalsAndNamesStruct(sIdx).signalObject;
        signalNames = signalsAndNamesStruct(sIdx).signalNames;

        selAxesIndex = locGetSelectedAxesIndex(app);
        oldLegend = locGetLegendForAxes(app, selAxesIndex);

        if isempty(oldLegend)
            legendContent = signalNames;
        else
            legendContent = locGetUpdatedLegendContent(signalNames, oldLegend);
        end
        
        % Addresses the edge case where legendContent only consists of a
        % string equal to "position". "position" is interpreted as a legend
        % property name and the solution is to use a cell array instead.
        if isstring(legendContent)
            legendContent = cellstr(legendContent);
        end

        lineHandles = plotTimeSeries(signalTS, app.selectedAxes);
        if signalTS.Time(end) > app.selectedAxes.XLim(2)
            app.selectedAxes.XLim(2) = 10*ceil(signalTS.Time(end)/10);
        end
        set(lineHandles, 'Tag', cbx.Tag);
        legend(app.selectedAxes, legendContent, 'Interpreter', 'none');
        title(app.selectedAxes,'');
        xlabel(app.selectedAxes,'');
        ylabel(app.selectedAxes,'');
    else
        % delete the lines
        lineHandles = findobj(app.selectedAxes, 'Tag', cbx.Tag);
        delete(lineHandles);
        if isempty(app.selectedAxes.Children)
            legend(app.selectedAxes, 'off');
        end
    end
    locUpdateAxesXLim(app.selectedAxes);
    drawnow limitrate;
end

function locCreateNoSignalsLabel(app)
    lbl = uilabel(app.SigsGL);
    lbl.Layout.Row = 1;
    lbl.Layout.Column = 1;
    lbl.HorizontalAlignment = 'left';
    lbl.Text = message('simulinkcompiler:genapp:NoSignalsAvailable').getString();
    lbl.Tag = 'signals_placeholder';
    app.Helper.scroll(app.ScrollBottomLeftUIC);
end

function index = locGetSelectedAxesIndex(app)
    allAxes = findobj(app.GUI, 'type', 'axes');
    index = find(allAxes == app.selectedAxes);
end

function legendContent = locGetUpdatedLegendContent(signalNames, oldLegend)
    if isa(oldLegend, 'matlab.graphics.GraphicsPlaceholder')
        legendContent = signalNames;
    else
        legendContent = oldLegend.String;
        newLegend = cellstr(signalNames);
        legendContent = [legendContent newLegend];
        legendContent = unique(legendContent, 'stable');
    end
end

function lgnd = locGetLegendForAxes(app, axesIndex)
    legendsAndAxes = app.AxesGL.Children;
    numChildren = numel(legendsAndAxes);
    lgnd = [];
    currAxesIdx = 1;

    for childIdx = 1:numChildren
        if isa(legendsAndAxes(childIdx), 'matlab.ui.control.UIAxes')
            if currAxesIdx == axesIndex && ...
               childIdx + 1 <= numChildren && ...
               isa(legendsAndAxes(childIdx + 1), ...
                    'matlab.graphics.illustration.Legend')

                lgnd = legendsAndAxes(childIdx + 1);
                break;
            end
            currAxesIdx = currAxesIdx + 1;
        end
    end
end

function locUpdateAxesXLim(axs)
    lns = axs.Children;
    if ~isempty(lns)
        xLim = [inf -inf]; % app.selectedAxes.XLim;
        for iln =1:length(lns)
            if isempty(lns(iln).XData), continue; end
            if lns(iln).XData(1) < xLim(1), xLim(1) = lns(iln).XData(1); end
            if lns(iln).XData(end) > xLim(end), xLim(2) = lns(iln).XData(end); end
        end
        xRng = xLim(2)-xLim(1);
        xScl = 10^floor(log10(xRng));
        xLim(1) = xScl*floor(xLim(1)/xScl);
        xLim(2) = xScl*ceil(xLim(2)/xScl);
        if all(isfinite(xLim)) && xLim(2) > xLim(1)
            axs.XLim = xLim;
        end
    end
end

function dataset = locConvertNumericSignalsToDataset(numericSig)
    arguments
       numericSig {mustBeNumeric}
    end 

    numSigs = size(numericSig, 2);
    dataset = Simulink.SimulationData.Dataset();
    for sigIdx = 1:numSigs
        newSig = Simulink.SimulationData.Signal();
        newSig.Name = message("simulinkcompiler:genapp:SignalNamePrefix", sigIdx).getString();
        newSig.Values = timeseries(numericSig(:, sigIdx));
        dataset = dataset.addElement(newSig);
    end
end

% LocalWords:  uilabel lh uicheckbox unsubscripted genapp
