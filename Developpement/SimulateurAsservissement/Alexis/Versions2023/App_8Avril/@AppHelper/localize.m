function localize(obj)
    %LOCALIZE Localize all user facing strings
    %   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    msgIdPrefix = 'simulinkcompiler:genapp:';

    app.FileMenu.Text = string(message([msgIdPrefix 'File']));
    app.SaveMenu.Text = string(message([msgIdPrefix 'Save']));
    app.SaveSession.Text = string(message([msgIdPrefix 'SaveSession']));
    app.SaveParametersAndInputs.Text = string(message([msgIdPrefix 'SaveParametersAndInputs']));
    app.LoadMenu.Text = string(message([msgIdPrefix 'Load']));
    app.LoadSession.Text = string(message([msgIdPrefix 'LoadSession']));
    app.LoadParametersAndInputs.Text = string(message([msgIdPrefix 'LoadParametersAndInputs']));

    app.SettingsMenu.Text = string(message([msgIdPrefix 'Settings']));
    app.ConfigureForDeploymentMenu.Text = string(message([msgIdPrefix 'ConfigureForDeployment']));
    app.ResetParametersAndInputs.Text = string(message([msgIdPrefix 'ResetParametersAndInputs']));

    app.PlotRefreshRateHzSliderLabel.Text = string(message([msgIdPrefix 'RefreshRateHz']));
    app.PlotLayoutLabel.Text = string(message([msgIdPrefix 'PlotLayout']));
    app.ModelTab.Title = string(message([msgIdPrefix 'Model']));
    app.StopTimeEditFieldLabel.Text = string(message([msgIdPrefix 'StopTime']));
end
