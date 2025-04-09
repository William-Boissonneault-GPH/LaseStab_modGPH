function resetParametersAndInputs(obj)
% Reset the parameters and input signals to the default values when the app was generated.
    
%   Copyright 2022 The MathWorks, Inc.

    try
        vars = load(fullfile(obj.getAssetsFolder(), 'data', 'modelData.mat'));
        app = obj.App;
        % reset parameters
        app.modelData.tunableVariables = vars.modelData.tunableVariables;
        app.modelData.simInp.Variables = obj.tv2slsv(app.modelData.tunableVariables);
        obj.refreshPrms();

        if app.simStatus == slsim.SimulationStatus.Paused
            % Parameters have been reset while the simulation was paused, so 
            % for simplicity assume all the parameters have been modified and
            % update them when resuming
            app.modelData.modifiedTunableVariables = app.modelData.tunableVariables;
        end

        % reset input signals
        app.modelData.inputSignals = vars.modelData.inputSignals;
        if ~isempty(app.modelData.inputSignals)
            obj.createSimInp();
            app.modelData.simInp.ExternalInput = app.modelData.inputSignals;
            obj.updateSigsAndAxesGL(); % update plots of inputSignals
        end        
        obj.flashMsg(message("simulinkcompiler:genapp:SuccessfullyReset").string);
    catch ME
        msg = ME.getReport('extended', 'hyperlinks', 'off');
        uialert(app.GUI, msg, 'Error');
    end
end % resetParametersAndInputs
