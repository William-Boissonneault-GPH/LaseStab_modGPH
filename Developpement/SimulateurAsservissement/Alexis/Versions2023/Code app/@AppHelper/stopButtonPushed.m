function stopButtonPushed(obj, ~)
%STOPBUTTONPUSHED Callback for the stop simulation button.
%   Re-enable disabled controls, update simulation status label, stop
%   the simulation, and the refresh timer.

%   Copyright 2021-2022 The MathWorks, Inc.

    app = obj.App;
    stop(app.refreshTimer);
    app.Helper.setUIControlState('off');
    arrayfun(@(menuItem)(set(app.(menuItem),'Enable','off')),obj.SimulationInactiveControls);
    drawnow limitrate;
    obj.debugTrace('Before stop');
    simulink.compiler.stopSimulation(app.modelData.modelName);
    app.StatusLabel.Text = message("simulinkcompiler:genapp:TerminatingStatusLabel").getString();
    drawnow limitrate;
    obj.debugTrace('After stop');
end
