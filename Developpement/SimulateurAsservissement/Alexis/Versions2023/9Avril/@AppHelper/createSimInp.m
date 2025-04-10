function createSimInp(obj)
    app = obj.App;

    si = Simulink.SimulationInput(app.modelData.modelName);

    si.Variables = app.Helper.tv2slsv(app.modelData.tunableVariables);

    si.ExternalInput = app.modelData.inputSignals;

    % ✅ Force normal mode to avoid Rapid Accelerator issues
    si = si.setModelParameter('SimulationMode', 'normal');

    si = si.setModelParameter('StopTime', num2str(app.StopTimeEditField.Value));
    si = si.setModelParameter('SignalLogging', 'on');

    app.modelData.simInp = si;
end
