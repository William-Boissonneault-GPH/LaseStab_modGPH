function runPauseResumeButtonPushed(obj, event)
%RUNPAUSERESUMEBUTTONPUSHED Callback for the button pushed event of the
%simulation start/pause/resume button.
%   This callback is responsible for running/pausing/continuing a
%   simulation. Based on the status of the simulation, states of multiple
%   app components are updated. Panes are also expanded/collapsed as
%   needed.

%   Copyright 2021-2022 The MathWorks, Inc.

    app = obj.App;

    disableMenusForActiveSimulation = @()setSimulationInactiveControls(obj,'off');
    enableMenusForInactiveSimulation = @()(setSimulationInactiveControls(obj,'on'));
    
    try
        
        app.simStatus = simulink.compiler.getSimulationStatus(app.modelData.modelName);

        switch (app.simStatus)
          case slsim.SimulationStatus.Inactive
            % Play button pressed => issue sim command
            assert(isequal(event.Source.Icon,fullfile(obj.getAssetsFolder(), 'images', 'icon_run.png')));
            caughtError = [];
            try
                obj.hidePlotContent();
                % 1. disable UI control, update label

                obj.setUIControlState('off');
                % disable Save/Load menus as simulation is going to be active
                disableMenusForActiveSimulation();

                app.StatusLabel.Text = message("simulinkcompiler:genapp:StartingStatusLabel").getString;
                app.RunPauseResumeButton.Icon = fullfile(obj.getAssetsFolder(), 'images', 'icon_pause.png');
                drawnow limitrate;
                % 2. get simulation input
                obj.createSimInp();
                % 3. start the timer and call sim
                start(app.refreshTimer);
                obj.debugTrace('Before sim');
                in = app.modelData.simInp;
                if isdeployed || app.ConfigureForDeploymentMenu.Checked
                    in = simulink.compiler.configureForDeployment(in);
                end
                app.modelData.simOut = sim(in);
                assignin('base', 'out', app.modelData.simOut);
                obj.debugTrace('After sim');
                % 4. process the simulation results
                obj.processSimOut();
                % 5. update plots
                obj.updateSigsAndAxesGL();
                % 6. Make sure the bottom panels are visible
                obj.showPanels(["signals", "plots"]);
            catch caughtError
            end

            stop(app.refreshTimer);
            app.StatusLabel.Text = '';
            app.SimTimeLabel.Text = '';
            if ~isempty(caughtError)
                if ~isempty(caughtError.cause), caughtError = caughtError.cause{1}; end
                if isa(caughtError, 'matlab.internal.validation.RuntimeArgumentException')
                    msg = regexprep(caughtError.getReport, '<.*?>', '');
                else
                    msg = caughtError.getReport('extended', 'hyperlinks', 'off');
                end
                % 2. show the uialert
                uialert(app.GUI, msg,'Error');
                app.StatusLabel.Text = message("simulinkcompiler:genapp:ErrorSimulatingStatusLabel").getString;
            end
            % reset UI control
            app.RunPauseResumeButton.Icon = fullfile(obj.getAssetsFolder(), 'images', 'icon_run.png');

            obj.setUIControlState('on');
            % simulation has finished, Simulation status will be Inactive. Re-enable Save/Load/Reset menu 
            % for Session and Parameters/Inputs
            enableMenusForInactiveSimulation();

            app.StopButton.Enable = 'off';
            drawnow limitrate;

          case slsim.SimulationStatus.Running
            % Pause button pressed => issue pause command
            assert(isequal(event.Source.Icon,fullfile(obj.getAssetsFolder(), 'images', 'icon_pause.png')));
            stop(app.refreshTimer);

            obj.setUIControlState('off');
            disableMenusForActiveSimulation();

            app.StatusLabel.Text = message("simulinkcompiler:genapp:PausingStatusLabel").getString;
            app.RunPauseResumeButton.Icon = fullfile(obj.getAssetsFolder(), 'images', 'icon_resume.png');
            drawnow limitrate;
            try
                obj.debugTrace('Before pausing');
                simulink.compiler.pauseSimulation(app.modelData.modelName);
                app.simStatus = slsim.SimulationStatus.Paused;
                app.StatusLabel.Text = message("simulinkcompiler:genapp:PausedStatusLabel").getString;
                % get the simulation output and update plots
                obj.debugTrace('Paused, getting simout');
                app.modelData.simOut = simulink.compiler.getSimulationOutput(app.modelData.modelName);
                % process the simulation results
                obj.processSimOut();
                % update plots
                obj.updateSigsAndAxesGL();
                % Make sure the bottom panels are visible
                obj.showPanels(["signals", "plots"]);

                obj.setUIControlState('on');
                % Keep the save/load/reset menus for Session as well as Parameters and Inputs disabled
                % as the simulation is still "active". 
                disableMenusForActiveSimulation();

                drawnow limitrate;
            catch
                % NOOP - this is for the edge case where, by the time the
                % call is made to pauseSimulation, the simulation has
                % already stopped.
            end

          case slsim.SimulationStatus.Paused
            % Resume button pressed
            assert(isequal(event.Source.Icon,fullfile(obj.getAssetsFolder(), 'images', 'icon_resume.png')));

            % First apply any pending parameter changes
            if ~isempty(app.modelData.modifiedTunableVariables)
                slVars = obj.tv2slsv(app.modelData.modifiedTunableVariables);
                simulink.compiler.modifyParameters(app.modelData.modelName, slVars);
                obj.debugTrace(['Modified ', ....
                                num2str(numel(app.modelData.modifiedTunableVariables)), ....
                                ' parameters']);
                app.modelData.modifiedTunableVariables = []; % reset
            end

            % and then issue resume command
            app.StatusLabel.Text = message("simulinkcompiler:genapp:ResumingStatusLabel").getString;
            app.RunPauseResumeButton.Icon = fullfile(obj.getAssetsFolder(), 'images', 'icon_pause.png');

            obj.setUIControlState('off');
            disableMenusForActiveSimulation();

            drawnow limitrate;
            start(app.refreshTimer);
            simulink.compiler.resumeSimulation(app.modelData.modelName);
            obj.debugTrace('Resumed sim');
            
          case slsim.SimulationStatus.Terminating
            % Clicked pause when simulation was terminating
            app.RunPauseResumeButton.Enable = 'off';
          otherwise
            assert(false, 'Invalid simulation status');
        end

    catch ME
        msg = ME.getReport('extended', 'hyperlinks', 'off');
        uialert(app.GUI, msg, 'Error');
    end

end

function setSimulationInactiveControls(helper, state)
    % Set the state of the following menu items based on the expected
    % simulation status:
    % "SaveMenu"                  
    % "SaveSession"               
    % "SaveParametersAndInputs"   
    % "LoadMenu"                  
    % "LoadSession"               
    % "LoadParametersAndInputs"   
    % "ResetParametersAndInputs"
    % "ConfigureForDeploymentMenu"
    app = helper.App;
    arrayfun(@(menuItem)(set(app.(menuItem),'Enable',state)),helper.SimulationInactiveControls);
end
% LocalWords:  uialert NOOP
