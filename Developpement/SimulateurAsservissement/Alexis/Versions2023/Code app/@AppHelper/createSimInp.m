function createSimInp(obj)
%CREATESIMINP Create a Simulink.SimulationInput object to be applied to the
%model during the later call to sim function.
%
%   The created Simulink.SimulationInput object is cached in the app and
%   reused in subsequent calls. If you (app user) change variable values or
%   load external input signals, their values are captured on creation and
%   in these subsequent calls.
%
%   When run from MATLAB, the app configures the Simulink.SimulationInput
%   object for deployment if the "Configure for Deployment" option, in the
%   "Settings" menu, is checked.
%
%   In deployed apps, the object is automatically configured for deployment
%   regardless of what the value of the "Configure for Deployment" option
%   was before deploying the app.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;

    si = Simulink.SimulationInput(app.modelData.modelName);

    si.Variables = app.Helper.tv2slsv(app.modelData.tunableVariables);

    si.ExternalInput = app.modelData.inputSignals;

    si = si.setModelParameter('StopTime', num2str(app.StopTimeEditField.Value));
    si = si.setModelParameter('SignalLogging', 'on');

    app.modelData.simInp = si;

end
