function processSimOut(obj)
%PROCESSSIMOUT Process the output of a simulation run in the app.
%   Use the Simulink.SimulationOutput saved in app.modelData to extract and
%   append the output signals to app.modelData. If the output is in the
%   "StructWithTime" format, it is converted to a
%   Simulink.SimulationData.Dataset. The latter type is what the method
%   supports and is used to populate the loggedSignals field in
%   app.modelData.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    simOut = app.modelData.simOut;
    if isempty(simOut), return; end
    namesOfVarsInSimOut = simOut.who;
    logSigIdx = 0;
    loggedSignals = Simulink.SimulationData.Dataset;

    for varIdx = 1:length(namesOfVarsInSimOut)
        varName = namesOfVarsInSimOut{varIdx};
        var = simOut.(varName);
        if prvIsStructLogVar(var)
            % convert struct with time log vars to dataset
            var = Simulink.SimulationData.Dataset(var, 'DatasetName', varName);
        end
        varType = class(var);
        switch varType
            case 'Simulink.SimulationData.Dataset'
                logSigIdx = logSigIdx+1;
                loggedSignals(logSigIdx) = var;
            otherwise
                skipVarMessage = ...
                    message('simulinkcompiler:genapp:SkippingVariable', ...
                    varName, varType).getString;

                app.Helper.recordSessionLog(skipVarMessage);
        end
    end
    app.modelData.loggedSignals = loggedSignals;
end

%%
function answer = prvIsStructLogVar(slv)
    answer = false; % assume
    if ( isstruct(slv) && isfield(slv,'time') ...
            && isfield(slv,'signals') && isstruct(slv.signals) ...
            && isa(slv.time,'double') && isvector(slv.time) ...
            && isfield(slv.signals,'values') && ~isempty(slv.signals(1).values) ...
            && ismatrix(slv.signals(1).values) ...
            && size(slv.signals(1).values, 1) == length(slv.time) )
        answer = true;
    end
end

% LocalWords:  genapp
