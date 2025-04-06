function loadParametersAndInputs(obj, fileSpec)
% Load the parameters and input signals from a mat-file
    
%   Copyright 2022 The MathWorks, Inc.

    arguments
        obj
        fileSpec (1,:) string = ["*.mat", "MAT-files (*.mat)"]
    end

    loadPrmsAndInpsOnly = true;
    success = obj.loadSession(fileSpec, loadPrmsAndInpsOnly);
    if success
        % Make sure all the panels are visible
        obj.showPanels(["model", "params", 'signals', 'plots']);
        obj.flashMsg(message("simulinkcompiler:genapp:SuccessfullyLoaded").string);
    end
    
end % loadParametersAndInputs
