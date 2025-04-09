function success = loadSession(obj, fileSpec, loadPrmsAndInpsOnly)
% Load the session data from a mat-file
    
%   Copyright 2022 The MathWorks, Inc.


    arguments
        obj
        fileSpec (1,:) string = ["*.mat", "MAT-files (*.mat)"]
        loadPrmsAndInpsOnly (1,1) logical = false
    end

    app = obj.App;
    origModelData = app.modelData;
    success = false; % assume

    try

        [fileName, pathName] = uigetfile(fileSpec, message("simulinkcompiler:genapp:SelectMATFile").string);
        figure(app.GUI); % bring app to front
        if isequal(fileName,0) || isequal(pathName,0), return; end
        filePath = fullfile(pathName, fileName);

        varsLoaded = load(filePath);
        err = locValidateLoadedVars(varsLoaded, loadPrmsAndInpsOnly);

        if ~isempty(err)
          uialert(app.GUI, err.getString(), 'Error');
          app.modelData = origModelData; % restore
          return;
        end

        % load appData
        if ~loadPrmsAndInpsOnly
            app.GUI.Position = varsLoaded.appData.GUI.Position;

            % show all the panels
            obj.showPanels();
        end

        % load modelData
        if loadPrmsAndInpsOnly
            app.modelData.tunableVariables = varsLoaded.modelData.tunableVariables;
            app.modelData.inputSignals = varsLoaded.modelData.inputSignals;
        else
            app.modelData = varsLoaded.modelData;
        end

        % Create the simulation input and refresh the parameters panel
        obj.createSimInp();
        obj.refreshPrms();

        % Delete the current axes and create anew
        if ~loadPrmsAndInpsOnly
            delete(app.AxesGL.Children);
            app.selectedAxes = repmat(matlab.ui.control.UIAxes,0,0);
            app.NumAxesRows.Value = varsLoaded.appData.NumAxesRows.Value;
            app.NumAxesCols.Value = varsLoaded.appData.NumAxesCols.Value;
            app.AxesGL.RowHeight = repmat(app.Helper.MinAxesHeight, 1, app.NumAxesRows.Value);
            app.AxesGL.ColumnWidth = repmat({'1x'}, 1, app.NumAxesCols.Value);
            selAxesRow = varsLoaded.appData.selectedAxes.Layout.Row;
            selAxesCol = varsLoaded.appData.selectedAxes.Layout.Column;
            for ir=1:app.NumAxesRows.Value
                for jc=1:app.NumAxesCols.Value
                    axs = app.Helper.createAxes(ir, jc);
                    if ir == selAxesRow && jc == selAxesCol
                        selectedAxes = axs; % cache the selectedAxes to set
                    end
                    % create empty lines for each signal that should go into this axes
                    sigsInAxes = varsLoaded.appData.signalsInAxes(ir,jc);
                    for is=1:length(sigsInAxes.Tags)
                        sigTag = sigsInAxes.Tags{is};
                        sigClr = sigsInAxes.Colors{is};
                        if ~isempty(sigTag) && ~isempty(sigClr)
                            line(axs, 'XData',[], 'YData',[], 'Tag',sigTag, 'Color',sigClr);
                        end
                    end
                end
            end
            obj.fitAxesInNewView();
            obj.setMainGLRowHeight();
        end

        % update the signals selections and plots
        autoSelectFirstLoggedSignal = false;
        app.Helper.updateSigsAndAxesGL(autoSelectFirstLoggedSignal);

        if ~loadPrmsAndInpsOnly

            % set the selected axes after the plots have been updated
            obj.setSelectedAxes(selectedAxes);

            % restore the state of the panels
            if ~varsLoaded.appData.ScrollTopLeftUIC.Enable
                % hide the model panel
                app.Helper.scroll(app.ScrollTopLeftUIC);
            elseif  ~varsLoaded.appData.ScrollTopRightUIC.Enable
                % hide the params panel
                app.Helper.scroll(app.ScrollTopRightUIC);
            end
            
            if ~varsLoaded.appData.ScrollBottomLeftUIC.Enable
                % hide the signal panel
                app.Helper.scroll(app.ScrollBottomLeftUIC);
            elseif  ~varsLoaded.appData.ScrollBottomRightUIC.Enable
                % hide the axes panel
                app.Helper.scroll(app.ScrollBottomRightUIC);
            end
            
            if ~varsLoaded.appData.ScrollUpUIC.Enable
                % hide the top panels
                app.Helper.scroll(app.ScrollUpUIC);
            elseif  ~varsLoaded.appData.ScrollDownUIC.Enable
                % hide the bottom panels
                app.Helper.scroll(app.ScrollDownUIC);
            end

            app.StopTimeEditField.Value = varsLoaded.appData.StopTimeEditField.Value;
            app.PlotRefreshRateHzSlider.Value = varsLoaded.appData.PlotRefreshRateHzSlider.Value;
            app.ConfigureForDeploymentMenu.Checked = varsLoaded.appData.ConfigureForDeploymentMenu.Checked;
        end

        success = true;
        
    catch ME
        msg = ME.getReport('extended', 'hyperlinks', 'off');
        uialert(app.GUI, msg, 'Error');
        app.modelData = origModelData; % restore
    end
    
end % loadSession

function err = locValidateLoadedVars(varsLoaded, loadPrmsAndInpsOnly)

  err = [];
  requiredFieldMissing = ~isfield(varsLoaded, 'modelData');
  conditionallyRequiredFieldMissing = ~loadPrmsAndInpsOnly && ...
    ~isfield(varsLoaded, 'appData');

  if requiredFieldMissing || conditionallyRequiredFieldMissing
    modelDataFile = fullfile('assets', 'data', 'modelData.mat');
    err = message("simulinkcompiler:genapp:MissingFieldsInLoadedVariables", modelDataFile);
  end

end % locValidateLoadedVars
