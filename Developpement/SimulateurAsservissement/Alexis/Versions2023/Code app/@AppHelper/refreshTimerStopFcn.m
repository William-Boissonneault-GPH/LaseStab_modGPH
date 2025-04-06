function refreshTimerStopFcn(obj, ~, ~)
%REFRESHTIMERSTOPFCN Refresh timer's stop-function.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    app.simStatus = simulink.compiler.getSimulationStatus( ...
        app.modelData.modelName);
end
