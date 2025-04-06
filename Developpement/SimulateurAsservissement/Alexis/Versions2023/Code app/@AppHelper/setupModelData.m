function modelData = setupModelData(obj)
%SETUPMODELDATA Load model data created at app generation time for use in
%the app.

%   Copyright 2021 The MathWorks, Inc.

    vars = load(fullfile(obj.getAssetsFolder(), 'data', 'modelData.mat'));
    modelData = vars.modelData;
    modelData.simOut = [];

    % keep track of parameter changes when simulation is paused, these will
    % be applied when simulation is resumed.
    modelData.modifiedTunableVariables = [];

    if ismcc || isdeployed
        load_simulink;
    else
        load_system(modelData.modelName);
    end
    
end
