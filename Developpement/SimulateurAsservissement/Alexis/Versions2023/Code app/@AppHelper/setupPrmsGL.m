function setupPrmsGL(obj, tunableVariables)
%SETUPPRMSGL Create a tunable variables list with the associated edit
%fields or drill-in buttons.
%   Scalar types get a UI control (e.g. edit field or checkbox) for
%   in-place editing while more complex and nonscalar types get an edit
%   button, which opens a new tab for editing the variable.

%   Copyright 2021 The MathWorks, Inc.

    import matlab.internal.datatoolsservices.getWorkspaceDisplay;

    app = obj.App;
    simVars = obj.tv2slsv(tunableVariables);
    nTV = length(simVars);
    app.PrmsGL.RowHeight = repmat({'fit'},1,nTV+1);

    lbl = uilabel(app.PrmsGL);
    lbl.Layout.Row = 1;
    lbl.Layout.Column = 1;
    lbl.HorizontalAlignment = 'left';
    lbl.Text = message("simulinkcompiler:genapp:Parameter").getString;
    lbl.FontWeight = 'Bold';

    lbl = uilabel(app.PrmsGL);
    lbl.Layout.Row = 1;
    lbl.Layout.Column = 2;
    lbl.HorizontalAlignment = 'right';
    lbl.Text = message("simulinkcompiler:genapp:Value").getString;
    lbl.FontWeight = 'Bold';

    %altBGC = false;
    for iTV = 1:nTV
        paramName = simVars(iTV).Name;
        lbl = uilabel(app.PrmsGL);
        lbl.Layout.Row = iTV+1;
        lbl.Layout.Column = 1;
        lbl.HorizontalAlignment = 'left';
        %if altBGC, lbl.BackgroundColor = '#FFFFEE'; end
        paramValue = simVars(iTV).Value;

            %  Extract Simulink.Parameter value early
        if isa(paramValue, 'Simulink.Parameter')
            paramValue = paramValue.Value;
        end

        lbl.Text = paramName;

        if ~isscalar(paramValue) || isstruct(paramValue) || isobject(paramValue)
            displayData = getWorkspaceDisplay({paramValue});

            wgt = uipanel(app.PrmsGL, 'BorderType', 'none');
            wgtGL = uigridlayout(wgt);
            wgtGL.ColumnWidth = {'1x', 'fit'};
            wgtGL.RowHeight = {'1x'};
            wgtGL.Padding = [0,0,0,0];

            chWgt1 = uilabel(wgtGL);
            chWgt1.Text = displayData.Size + " " + displayData.Class;
            chWgt1.Layout.Column = 1;

            imagesPath = fullfile(obj.getAssetsFolder(), 'images');
            iconPath = fullfile(imagesPath, 'penCursor.svg');

            chWgt2 = uibutton(wgtGL);
            chWgt2.Text = '';
            chWgt2.Icon = iconPath;
            chWgt2.Layout.Column = 2;
            chWgt2.ButtonPushedFcn = {@varEditBtnPushedFcn, app, iTV};

        elseif isnumeric(paramValue)
            wgt = uieditfield(app.PrmsGL, 'numeric');
            wgt.Value = double(paramValue);
            wgt.Tag = paramName;
        
        elseif islogical(paramValue)
            wgt = uipanel(app.PrmsGL, 'BorderType', 'none');
            wgtGL = uigridlayout(wgt);
            wgtGL.ColumnWidth = {'1x', 'fit'};
            wgtGL.RowHeight = {'1x'};
            wgtGL.Padding = [0,0,0,0];

            chWgt = uicheckbox(wgtGL);
            chWgt.Layout.Column = 2;
            chWgt.Text = '';
            chWgt.Value = paramValue;
            chWgt.Tag = paramName;
        else 
            paramValType = class(paramValue);
            wgt = uilabel(app.PrmsGL);
            msgId = "simulinkcompiler:genapp:VariableTypeNotHandled";
            wgt.Text = message(msgId, paramValType).getString;
            wgt.HorizontalAlignment = 'left'; 
        end
        wgt.Layout.Row = iTV+1;
        wgt.Layout.Column = 2;
        
        wgtToCreateCBFor = wgt;
        wgtCheckbox = findobj(wgt, 'Type', 'uicheckbox');
        if ~isempty(wgtCheckbox)
            wgtToCreateCBFor = wgtCheckbox;
        end

        if isprop(wgtToCreateCBFor, 'ValueChangedFcn')
            wgtToCreateCBFor.ValueChangedFcn = app.createCallbackFcnProxy( ...
                @(src, ev) obj.prmValueChangedFcn(ev), true);
        end

        %if altBGC, wgt.BackgroundColor = '#FFFFEE'; end
        %altBGC = ~altBGC; % uncomment to alternate row colors
    end
    app.PrmsGL.ColumnWidth = {'1x','fit'};
end

function varEditBtnPushedFcn(~, ~, app, varIndex)
    simVars = app.Helper.tv2slsv(app.modelData.tunableVariables);
    paramName = simVars(varIndex).Name;
    paramValue = simVars(varIndex).Value;
    app.Helper.fillVariableEditTab(paramName, paramValue, 'Create');
end

% LocalWords:  BGC lbl svg uicheckbox wgt