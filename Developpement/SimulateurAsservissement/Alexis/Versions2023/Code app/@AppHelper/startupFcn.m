function startupFcn(obj)
%STARTUPFCN Callback called when the app starts and is responsible for
%initializing the app.
%   Initialize the app by showing/hiding relevant panes, setting up icon
%   image paths, loading model data, initializing UI controls, creating
%   tunable parameters list, creating plot axes, and starting the refresh
%   timer.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    app.GUI.Visible = 'off';

    % localize
    obj.localize();

    % resultsGL are minimized by default
    app.ResultsGL.Visible = 'off';
    app.ScrollDownUIC.Enable = 'off';
    app.MainGL.RowHeight = {'fit','1x','fit',0};

    obj.setImagePaths();

    app.modelData = obj.setupModelData();

    app.StopTimeEditField.Value = app.modelData.modelParameters.StopTime;

    app.ModelHTML.HTMLSource = fullfile(obj.getAssetsFolder(), app.modelData.modelHTMLSource);

    % Change data on the model view to initiate a fit-to-view action
    app.ModelHTML.Data = rand;
    obj.setupPrmsGL(app.modelData.tunableVariables);
    obj.updateSigsAndAxesGL();

    %% AxesGL
    app.AxesGL.RowHeight = repmat(obj.MinAxesHeight, 1, app.NumAxesRows.Value);
    app.AxesGL.ColumnWidth = repmat({'1x'}, 1, app.NumAxesCols.Value);
    app.AxesGL.Scrollable = 'on';
    for ir=1:app.NumAxesRows.Value
        for ic=1:app.NumAxesCols.Value
            obj.createAxes(ir, ic);
        end
    end

    app.GUI.Name = message("simulinkcompiler:genapp:SimulationAppTitle",app.modelData.modelName).string;
    uniqueTag = [strrep(tempname,tempdir,''), ' ', char(app.modelData.modelName)];
    app.GUI.Tag = uniqueTag;
    app.GUI.DeleteFcn = @(src,ev) locAppDeleteFcn(src, ev);
    
    %% Refresh Timer
    app.refreshTimer = timer( ...
        'Tag', app.GUI.Tag, ...
        'Name','refreshTimer', ...
        'ObjectVisibility','off', ...
        'ExecutionMode','fixedSpacing', ...
        'Period',1/(2^app.PlotRefreshRateHzSlider.Value), ...
        'TimerFcn', @(timerObj, timerEvent) obj.refreshTimerFcn(timerObj, timerEvent), ...
        'ErrorFcn', @(timerObj, timerEvent) obj.refreshTimerErrorFcn(timerObj, timerEvent), ...
        'StartFcn', @(timerObj, timerEvent) obj.refreshTimerStartFcn(timerObj, timerEvent), ...
        'StopFcn', @(timerObj, timerEvent) obj.refreshTimerStopFcn(timerObj, timerEvent));

    %% FlashMsg Timer
    app.flashMsgTimer = timer('Tag', app.GUI.Tag, ...
                              'Name','flashMsgTimer', ...
                              'ObjectVisibility','off');

    % Pre-load simlation libraries to pay the one time cost at the start in deployed,
    % otherwise load the model
    if ismcc || isdeployed
        app.ConfigureForDeploymentMenu.Enable = 'off';
        app.SettingsMenu.Visible = 'off';
        load_simulink;
    else
        load_system(app.modelData.modelName);
    end

    %% Setup done, now make the GUI visible
    app.GUI.Visible = 'on';
    app.initialized = true;
end

function locAppDeleteFcn(src, ~)

    % at this point app and app helper objects are deleted, so we need use tags to find objects to cleanup
    uniqueTag = src.Tag;
    uniqueTagParts = split(uniqueTag);
    mdlName = uniqueTagParts{2};
    
    % delete the timers
    tmrs = timerfindall('Tag', uniqueTag);
    for it = 1:numel(tmrs)
        if tmrs(it).Running
            stop(tmrs(it));
        end
    end
    delete(tmrs);

    % stop the simulation if it is active
    simStatus = simulink.compiler.getSimulationStatus(mdlName);
    if simStatus ~= slsim.SimulationStatus.Inactive
        simulink.compiler.stopSimulation(mdlName);
    end

end % locAppDeleteFcn


% LocalWords:  GL
