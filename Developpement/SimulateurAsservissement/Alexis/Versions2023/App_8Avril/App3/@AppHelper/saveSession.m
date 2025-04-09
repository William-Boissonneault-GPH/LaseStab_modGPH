function success = saveSession(obj, fileSpec, savePrmsAndInpsOnly)

    arguments
        obj
        fileSpec (1,:) string = ["*.mat", "MAT-files (*.mat)"]
        savePrmsAndInpsOnly (1,1) logical = false
    end

    success = false; % assume
    try
        app = obj.App;

        [fileName, pathName] = uiputfile(fileSpec, message("simulinkcompiler:genapp:SaveToMATFile").string);
        figure(app.GUI); % bring app to front
        if isequal(fileName,0) || isequal(pathName,0), return; end
        filePath = fullfile(pathName, fileName);

        if savePrmsAndInpsOnly
            mdlDataToSave.tunableVariables = app.modelData.tunableVariables;
            mdlDataToSave.inputSignals = app.modelData.inputSignals;
            varsToSave.modelData = mdlDataToSave;
        else
            varsToSave.modelData = app.modelData;

            varsToSave.appData.GUI.Position = app.GUI.Position;

            varsToSave.appData.ScrollTopRightUIC.Enable = app.ScrollTopRightUIC.Enable;
            varsToSave.appData.ScrollTopLeftUIC.Enable = app.ScrollTopLeftUIC.Enable;
            varsToSave.appData.ScrollDownUIC.Enable = app.ScrollDownUIC.Enable;
            varsToSave.appData.ScrollUpUIC.Enable = app.ScrollUpUIC.Enable;
            varsToSave.appData.ScrollBottomRightUIC.Enable = app.ScrollBottomRightUIC.Enable;
            varsToSave.appData.ScrollBottomLeftUIC.Enable = app.ScrollBottomLeftUIC.Enable;

            varsToSave.appData.NumAxesRows.Value = app.NumAxesRows.Value;
            varsToSave.appData.NumAxesCols.Value = app.NumAxesCols.Value;
            varsToSave.appData.selectedAxes.Layout.Row = app.selectedAxes.Layout.Row;
            varsToSave.appData.selectedAxes.Layout.Column = app.selectedAxes.Layout.Column;

            axs = findobj(app.AxesGL, 'Type','axes');
            naxs = numel(axs);
            for iax=1:naxs
                ir = axs(iax).Layout.Row;
                jc = axs(iax).Layout.Column;
                lns = axs(iax).Children;
                sigTags = get(lns,'Tag');
                if ~iscell(sigTags), sigTags = {sigTags}; end
                varsToSave.appData.signalsInAxes(ir,jc).Tags = sigTags;
                sigCols = get(lns,'Color');
                if ~iscell(sigCols), sigCols = {sigCols}; end
                varsToSave.appData.signalsInAxes(ir,jc).Colors = sigCols;
            end
            
            varsToSave.appData.StopTimeEditField.Value = app.StopTimeEditField.Value;
            varsToSave.appData.PlotRefreshRateHzSlider.Value = app.PlotRefreshRateHzSlider.Value;
            varsToSave.appData.ConfigureForDeploymentMenu.Checked = app.ConfigureForDeploymentMenu.Checked;
        end
        
        save(filePath,'-struct','varsToSave');
        success = true;
        
    catch ME
        msg = ME.getReport('extended', 'hyperlinks', 'off');
        uialert(app.GUI, msg, 'Error');
    end
end
