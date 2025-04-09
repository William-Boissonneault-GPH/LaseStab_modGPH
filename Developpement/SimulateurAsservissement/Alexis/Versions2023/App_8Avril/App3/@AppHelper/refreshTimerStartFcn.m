function refreshTimerStartFcn(obj, ~, ~)
%REFRESHTIMERSTARTFCN Refresh timer's start-function.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    app.simStatus = simulink.compiler.getSimulationStatus( ...
        app.modelData.modelName);
end
