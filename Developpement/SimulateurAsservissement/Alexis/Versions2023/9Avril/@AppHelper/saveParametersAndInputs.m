function saveParametersAndInputs(obj, fileSpec)
% Save the current parameter and input signals to a mat-file
    
%   Copyright 2022 The MathWorks, Inc.

    arguments
        obj
        fileSpec (1,:) string = ["*.mat", "MAT-files (*.mat)"]
    end

    savePrmsAndInpsOnly = true;
    success = obj.saveSession(fileSpec, savePrmsAndInpsOnly);
    if success
        obj.flashMsg(message("simulinkcompiler:genapp:SuccessfullySaved").string);
    end
    
end % saveParametersAndInputs
