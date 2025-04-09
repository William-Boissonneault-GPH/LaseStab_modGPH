function refreshTimerFcn(obj, ~, ~)
%REFRESHTIMERFCN Refresh timer's timer-function.
%   Used for updating simulation controls and time label based on
%   simulation status and time. 

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    app.simStatus = simulink.compiler.getSimulationStatus(app.modelData.modelName);
    switch (app.simStatus)
        case slsim.SimulationStatus.Inactive
            
        case slsim.SimulationStatus.Initializing
            app.StopButton.Enable = 'on';
            app.StatusLabel.Text = message("simulinkcompiler:genapp:InitializingStatusLabel").string;
        
        case slsim.SimulationStatus.Initialized
            app.StopButton.Enable = 'on';

        case slsim.SimulationStatus.Running

            obj.debugTrace('Getting simout');

            app.StopButton.Enable = 'on';
            app.RunPauseResumeButton.Enable = 'on';
            app.StatusLabel.Text = message("simulinkcompiler:genapp:RunningStatusLabel").string;
            
            % get the simulation output
            app.modelData.simOut = simulink.compiler.getSimulationOutput(app.modelData.modelName);
            % process the simulation results
            obj.processSimOut();
            % update plots
            obj.updateSigsAndAxesGL();
            % Make sure the plots are visible
            obj.showPanels(["plots"]); %#ok

        case slsim.SimulationStatus.Paused
            app.StopButton.Enable = 'on';
            app.RunPauseResumeButton.Enable = 'on';
            app.StatusLabel.Text = message("simulinkcompiler:genapp:PausedStatusLabel").string;

        case slsim.SimulationStatus.Stopped
            app.StopButton.Enable = 'off';
            app.RunPauseResumeButton.Enable = 'off';
            app.StatusLabel.Text = message("simulinkcompiler:genapp:StoppedStatusLabel").string;

        case slsim.SimulationStatus.Terminating
            app.StopButton.Enable = 'off';
            app.RunPauseResumeButton.Enable = 'off';
            app.StatusLabel.Text = message("simulinkcompiler:genapp:TerminatingStatusLabel").string;

        otherwise
            error(message("simulinkcompiler:genapp:UnknownStatusLabel"));
    end

    simTime = simulink.compiler.getSimulationTime(app.modelData.modelName);
    if isfinite(simTime)
        prefix = message("simulinkcompiler:genapp:SimulationTimePrefix").getString;
        simTimeStr = sprintf('%s %10.4e', prefix, simTime);
    else
        simTimeStr = '';
    end
    app.SimTimeLabel.Text = simTimeStr;

    drawnow limitrate;
end
