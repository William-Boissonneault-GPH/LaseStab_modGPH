function createSimInp(obj)
    % Create a Simulink.SimulationInput object for the model
    app = obj.App;

    % Prepare SimulationInput object
    si = Simulink.SimulationInput(app.modelData.modelName);

    % Push tunable variables from app data into SimulationInput
    for i = 1:numel(app.modelData.tunableVariables)
        paramName = app.modelData.tunableVariables(i).QualifiedName;
        paramValue = app.modelData.tunableVariables(i).Value;

        % If parameter is Simulink.Parameter, unwrap the value
        if isa(paramValue, 'Simulink.Parameter')
            paramValue = paramValue.Value;
        end

        % Inject directly into SimulationInput
        si = si.setVariable(paramName, paramValue);
    end

    % Apply external input if needed
    si.ExternalInput = app.modelData.inputSignals;

    % Optional: disable Rapid Accelerator if you want
    % si = si.setModelParameter('SimulationMode', 'normal');

    % Set simulation parameters
    si = si.setModelParameter('StopTime', num2str(app.StopTimeEditField.Value));
    si = si.setModelParameter('SignalLogging', 'on');

    % Store SimulationInput object
    app.modelData.simInp = si;

    disp('✅ SimulationInput created with all parameters injected.');
end
