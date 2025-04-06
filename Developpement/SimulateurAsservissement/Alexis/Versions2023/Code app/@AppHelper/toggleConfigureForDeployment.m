function toggleConfigureForDeployment(obj)
%TOGGLECONFIGUREFORDEPLOYMENT Toggle the Configure for Deployment option in
%the Settings menu.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    app.ConfigureForDeploymentMenu.Checked = matlab.lang.OnOffSwitchState( ...
        ~app.ConfigureForDeploymentMenu.Checked);
end