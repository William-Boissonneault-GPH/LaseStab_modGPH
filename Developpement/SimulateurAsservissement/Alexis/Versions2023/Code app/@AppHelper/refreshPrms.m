function refreshPrms(obj)
% Refresh the Parameters list and their values.
   app = obj.App;

    % Clean grid layout
    delete(app.PrmsGL.Children);

    % Rebuild the parameter grid
    tunableVars = app.modelData.tunableVariables;
    obj.setupPrmsGL(tunableVars);

    % Log message
    fprintf('✅ UI parameter fields have been refreshed!\n');

disp('=== Debug obj.App ===');
disp(class(obj.App));
disp(obj.App);
disp('=== End Debug ===');

    if ~isempty(app.lastLoadedParameters)
        disp('🔄 Resetting to last loaded JSON parameters...');
        % Apply last loaded parameters
        data = app.lastLoadedParameters;

        % Apply to modelData
        for i = 1:numel(app.modelData.tunableVariables)
            paramName = app.modelData.tunableVariables(i).QualifiedName;
            if isfield(data, paramName)
                newValue = data.(paramName);
                originalSize = size(app.modelData.tunableVariables(i).Value);
                if isnumeric(newValue) && isvector(newValue) && ~isequal(size(newValue), originalSize)
                    newValue = reshape(newValue, originalSize);
                end
                app.modelData.tunableVariables(i).Value = newValue;
            end
        end

        % Apply to UI fields
        allComponents = findall(app.PrmsGL);
        for i = 1:numel(allComponents)
            comp = allComponents(i);
            if isa(comp, 'matlab.ui.control.NumericEditField') && ~isempty(comp.Tag)
                if isfield(data, comp.Tag)
                    comp.Value = data.(comp.Tag);
                end
            end
        end

        % Rebuild Simulink.SimulationInput
        app.Helper.createSimInp();
        disp('✅ Reset to last loaded JSON complete.');

    else
        % No JSON loaded, fallback to original values
        disp('🔄 Resetting to original snapshot parameters...');
        app.modelData.tunableVariables = app.modelData.originalParameters;
        app.Helper.refreshPrms();
        app.Helper.createSimInp();
        disp('✅ Reset to original parameters complete.');
    end

end % refreshPrms
