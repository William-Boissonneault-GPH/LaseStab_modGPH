function guiCloseRequest(obj,~)
% Called when app is being closed, see if it is okay to close and offer to save the session.

%   Copyright 2022 The MathWorks, Inc.

    app = obj.App;

    % can't close if simulation is active
    simStatus = simulink.compiler.getSimulationStatus(app.modelData.modelName);
    if simStatus ~= slsim.SimulationStatus.Inactive
        uialert(app.GUI, ...
                message("simulinkcompiler:genapp:CannotCloseWhileRunning", char(simStatus)).string, ...
                'Error');
        return; % => force the user to stop sim first.
    end

    % if a sim was run, then ask if they want to save the session
    if ~isempty(app.modelData.simOut)
        opt = uiconfirm(app.GUI, ...
                        message("simulinkcompiler:genapp:SaveBeforeClosing").string, ...
                        message("simulinkcompiler:genapp:SaveBeforeClosingTitle").string, ...
                        'Options', {'Yes','No'});
        switch opt
          case "Cancel"
            return
          case "Yes"
            obj.saveSession();
        end % pass through if 'No' selected.
    end
    delete(app);

end
