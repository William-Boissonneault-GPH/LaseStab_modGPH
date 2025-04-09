function fillVariableEditTab(obj, varName, var, mode)
%FILLVARIABLEEDITTAB Create or update a tabgroup tab for the specified
%variable name and top-most variable value.
%
%   Example:
%       foo.bar(1) = 1:3;
%       foo.bar(2) = 4:6;
%       foo.baz = "some string";
%       obj.fillVariableEditTab("foo.bar(2)", foo, 'Create');
%       % perform some operations then update the tab. This puts the tab
%       in focus and ensures that the displayed value is the most
%       up-to-date.
%       obj.fillVariableEditTab("foo.bar(2)", foo, 'Update');

%   Copyright 2021 The MathWorks, Inc.

    import matlab.internal.datatoolsservices.getWorkspaceDisplay;

    app = obj.App;
    tabGroup = app.ModelAndVariablesView;

    if isequal(mode, 'Create') && foundAndActivatedTab(tabGroup, varName)
        return;
    end

    if isequal(mode, 'Update') && ~varHasTab(varName, app)
        return;
    end

    subVar = evalSubVarValue(varName, var, obj);
    varTable = getVarTable(mode, varName, app);

    varData.mode = 'Create';
    varData.var = var;
    varData.varName = varName;
    varData.subVar = subVar;
    varData.varTable = varTable;
    varData.view = 'FieldValue';
    varData.fieldNames = {};
    varData.fieldValues = {};

    varDisplaydata = getWorkspaceDisplay({subVar});

    if varDisplaydata.IsSummary
        createDrillInVarView(varData, obj);
    else
        createEditVarView(varData, obj);
    end 
end

% -------------------------------------------------------------------------

function TF = varHasTab(varName, app)
    tabGroup = app.ModelAndVariablesView;
    tab = findobj(tabGroup, "Title", varName);
    TF = ~isempty(tab);
end

function createDrillInVarView(varData, appHelper)
    if isstruct(varData.subVar) || ...
        (isobject(varData.subVar) && isscalar(varData.subVar)) || ...
        isa(varData.subVar, "containers.Map")

      processStructVar(varData, appHelper);

    elseif istable(varData.subVar) || istimetable(varData.subVar)

        structArr = table2struct(varData.subVar);        
        vars = string(fields(structArr))';

        for v = vars
          strct.(v) = [structArr.(v)];
        end

        varData.subVar = strct;
        processStructVar(varData, appHelper);

    elseif iscategorical(varData.subVar)
        processCategoricalVar(varData, appHelper);
    
    elseif iscell(varData.subVar) 
        processCellVar(varData, appHelper);

    elseif ismatrix(varData.subVar) || iscategorical(varData.subVar)
        processMatrixVar(varData, appHelper);
    end
end

% -------------------------------------------------------------------------

function processStructVar(varData, appHelper)
    import matlab.internal.datatoolsservices.getWorkspaceDisplay;
    varData.view = 'FieldValue';

    if isscalar(varData.subVar)
        [varData.fieldNames, varData.fieldValues] = ...
            exctractStructVars(varData.subVar);
    else
        for idx = 1:numel(varData.subVar)
            [structArrElmNames, structArrElmValues] = ...
                exctractStructVars(varData.subVar);
            varData.fieldNames = [varData.fieldNames; structArrElmNames];
            varData.fieldValues = [varData.fieldValues; structArrElmValues];
        end
    end

    varData = setStructVarData(varData);
    varData.varTable.SelectionChangedFcn = @(table, event) btnDnCbk( ...
        event, varData, appHelper);
end

% -------------------------------------------------------------------------

function varData = setStructVarData(varData)
    isStructArrayField = numel(varData.fieldValues) > 1 && ...
        numel(unique(varData.fieldNames)) == 1;

    if isStructArrayField
        varData = setStructArrayFieldVarData(varData);
    else
        varData = setStructFieldVarData(varData);
    end
end

% -------------------------------------------------------------------------

function varData = setStructArrayFieldVarData(varData)
    varData.view = 'Field';
    varData.varTable.ColumnName = varData.fieldNames(1);
    varData.varTable.Data = varData.fieldValues;
end

% -------------------------------------------------------------------------

function varData = setStructFieldVarData(varData)
    varData.varTable.Data = [varData.fieldNames, varData.fieldValues];
    field = message("simulinkcompiler:genapp:Field").string;
    value = message("simulinkcompiler:genapp:Value").string;
    varData.varTable.ColumnName = [field, value];
end

% -------------------------------------------------------------------------

function [fieldNames, fieldValues] = exctractStructVars(topStruct)
    import matlab.internal.datatoolsservices.getWorkspaceDisplay;

    structFields = fields(topStruct);
    varsCount = numel(structFields);
    fieldNames = cell(varsCount, 1);
    fieldValues = cell(varsCount, 1);

    for idx = 1:varsCount
        field = structFields{idx};
        childVar = topStruct.(field);
        varDisplaydata = getWorkspaceDisplay({childVar});
        fieldNames{idx} = field;
        fieldValues{idx} = char(varDisplaydata.Value);
    end
end

% -------------------------------------------------------------------------

function processCellVar(varData, appHelper)

    import matlab.internal.datatoolsservices.getWorkspaceDisplay;

    varData.view = 'Cell';
    cellIdx = numel(varData.subVar);
    cellValues(cellIdx) = "";

    while cellIdx > 0
        elem = varData.subVar(cellIdx);
        elemDisplaydata = getWorkspaceDisplay(elem);
        cellValues(cellIdx) = elemDisplaydata.Value;
        cellIdx = cellIdx - 1;
    end

    varData.varTable.Data = reshape(cellValues, size(varData.subVar));
    varData.varTable.ColumnEditable = true(1, size(varData.subVar, 2));

    varData.varTable.SelectionChangedFcn = @(table, event) btnDnCbk( ...
        event, varData, appHelper);
end

% -------------------------------------------------------------------------

function processMatrixVar(varData, appHelper)

    import matlab.internal.datatoolsservices.getWorkspaceDisplay;

    if ~isnumeric(varData.subVar) && ~isStringScalar(varData.subVar)
      varSize = size(varData.subVar);
      dispData = getWorkspaceDisplay({varData.subVar});
      vals = repmat("1x1 " + dispData.Class, varSize);
      varData.varTable.Data = vals;

      varData.var = varData.var;
    else

      varData.varTable.Data = varData.subVar;
      app = appHelper.App;
      varData.varTable.CellEditCallback = @(table, event) varValueChanged( ...
        table, event, app);
      varData.varTable.ColumnEditable = true(1, size(varData.subVar, 2));
      varData.view = 'Edit';
    end
        
    varData.varTable.SelectionChangedFcn = @(table, event) btnDnCbk( ...
        event, varData, appHelper);
end

% -------------------------------------------------------------------------

function processCategoricalVar(varData, appHelper)
    strVar = string(varData.subVar);
    varData.varTable.Data = strVar;
    cat = categories(varData.subVar);
    varData.varTable.ColumnFormat = {reshape(cat, 1, numel(cat))};
    varData.varTable.ColumnEditable = true;

    varData.varTable.CellEditCallback = @(table, event) varValueChanged( ...
        table, event, appHelper.App);
end

% -------------------------------------------------------------------------

function createEditVarView(varData, appHelper)
    varData.view = 'Edit';
    app = appHelper.App;

    if ischar(varData.subVar)
        varData.subVar = string(varData.subVar);
    end

    try
      varData.varTable.Data = varData.subVar;
    catch
      tab = varData.varTable.Parent;
      rawVarValue = evalc("varData.subVar");
      delete(varData.varTable);
      text = uitextarea(tab);
      text.Value = regexprep(rawVarValue, "(<([^>]+)>)", "");
      return;
    end
      
    varData.varTable.ColumnEditable = true(1, numel(varData.subVar));
    varData.varTable.CellEditCallback = @(table, event) varValueChanged( ...
        table, event, app);

    varData.varTable.SelectionChangedFcn = @(table, event) btnDnCbk( ...
        event, varData, appHelper);
end

% -------------------------------------------------------------------------

function varTable = createNewTabWithTable(tabGroup, varName, app)
    newTab = uitab(tabGroup, "Title", varName, "Scrollable", "on");
    newTab.ContextMenu = uicontextmenu(app.GUI);
    tabGroup.SelectedTab = newTab;
    addCloseMenuToTab(newTab);

    grid = uigridlayout(newTab, ...
        "ColumnWidth", {'1x'}, ...
        "RowHeight", {'1x'}, ...
        "Padding", [0,0,0,0]);

    varTable = uitable(grid);
end

% -------------------------------------------------------------------------

function TF = foundAndActivatedTab(tabGroup, varName)
    TF = false;
    tab = findobj(tabGroup, "Title", varName);

    if ~isempty(tab)
        tabGroup.SelectedTab = tab;
        TF = true;
    end
end

% -------------------------------------------------------------------------

function addCloseMenuToTab(newTab)
    menuItem = uimenu(newTab.ContextMenu, 'Text', 'Close');
    menuItem.MenuSelectedFcn = @(src, event) delete(newTab);
end

% -------------------------------------------------------------------------

function btnDnCbk(event, varData, appHelper)
    varData.varTable.Selection = [];
    if isDoubleClick() && ~isequal(varData.view, 'Edit')
        drillInTriggered(event, varData, appHelper);
    end
end

% -------------------------------------------------------------------------

function TF = isDoubleClick()
    persistent chk; TF = false;

    if isempty(chk)
        chk = 1;
        pause(0.5);
        if chk == 1 % single-click
            chk = []; TF = false;
        end
    else % double-click
        chk = []; TF = true;
    end
end

% -------------------------------------------------------------------------

function drillInTriggered(event, varData, appHelper)
    switch(varData.view)
        case 'FieldValue'
            spawnFieldValueView(event, varData, appHelper);

        case 'Field'
            spawnFieldView(event, varData, appHelper);

        case 'Cell'
            spawnCellView(event, varData, appHelper);
    end
end

% -------------------------------------------------------------------------

function spawnFieldValueView(event, varData, appHelper)
    row = event.Selection(1);
    col = event.Selection(2);

    if isequal(event.SelectionType, 'cell') && col == 2
        vName = varData.varTable.Data(row, 1);
    else
        vName = varData.varTable.Data(row, col);
    end

    if isvarname(string(vName))
      appHelper.fillVariableEditTab(varData.varName + "." + vName, ...
        varData.var, varData.mode);
    else
      idx = "("+row+","+col+")";
      appHelper.fillVariableEditTab(varData.varName + idx, ...
        varData.var, varData.mode);
    end
end

% -------------------------------------------------------------------------

function spawnFieldView(event, varData, appHelper)
    import matlab.internal.datatoolsservices.getWorkspaceDisplay;

    row = event.Selection(1);
    qualifiedSubVarName = varData.subVar(row).(varData.fieldNames(1));
    subVarDisplayData = getWorkspaceDisplay({qualifiedSubVarName});
    varData.varTable.ColumnEditable = ~subVarDisplayData.IsSummary;
    
    if subVarDisplayData.IsSummary
        varData.varTable.CellEditCallback = [];
        arrayIndex = "(" + row + ")";
        newTabVarName = varData.varName + arrayIndex + "." + ...
            varData.fieldNames(1);
        appHelper.fillVariableEditTab(newTabVarName, varData.var, ...
            varData.mode);
    else
        app = appHelper.App;
        varData.varTable.CellEditCallback = ...
            @(table, event) varValueChanged(table, event, app);
    end
end

% -------------------------------------------------------------------------

function spawnCellView(event, varData, appHelper)
    row = event.Selection(1);
    col = event.Selection(2);
    varData.varTable.CellEditCallback = [];
    cellIndex = "{" + row + ", " + col + "}";
    appHelper.fillVariableEditTab(varData.varName + cellIndex, ...
        varData.var, varData.mode);
end

% -------------------------------------------------------------------------

function varValueChanged(table, event, app)
    if isequal(event.PreviousData, event.NewData)
        return;
    end

    vName = table.Parent.Parent.Title;
    newValue = table.Data;

    fullyQualVars = string({app.modelData.tunableVariables.QualifiedName});
    search = cellfun(@(var) contains(vName, var), fullyQualVars);
    qualVar = app.modelData.tunableVariables(search).QualifiedName;
    updateVarValue(qualVar, vName, newValue, search, app);

    app.Helper.createSimInp();
    simInVarNames = [app.modelData.simInp.Variables.Name];
    
    topVarName = app.Helper.extractTopVarName(vName);
    topVar = app.modelData.simInp.Variables( ...
        simInVarNames == topVarName).Value;

    if ~isequal(qualVar, vName)
      % it is a sub-variable; update all tabs with having the associated
      % top-var 
      updateTabsForTopVar(topVar, qualVar, vName, app);
    end

    app.Helper.fillVariableEditTab(topVarName, topVar, 'Update');
    assignin('base', string(qualVar), app.modelData.tunableVariables(search).Value);
end

% -------------------------------------------------------------------------

function updateVarValue(varName, tabName, newValue, search, app)
    try
      if isequal(varName, tabName)
        updateTopVarValue(newValue, search, app)
      else
        updateSubVarValue(varName, tabName, newValue, search)
      end
    catch mE
      msg = mE.getReport('basic');
      title = message("simulinkcompiler:genapp:FailedToUpdateVariable").string;
      app.Helper.showMessage(msg, title);
    end
end

% -------------------------------------------------------------------------

function updateTopVarValue(newValue, search, app)
    varClass = class(app.modelData.tunableVariables(search).Value);
    
    if varClass == "categorical"
      app.modelData.tunableVariables(search).Value = categorical(newValue);
    else
      app.modelData.tunableVariables(search).Value = cast(newValue, varClass);
    end
end

% -------------------------------------------------------------------------

function updateSubVarValue(varName, tabName, newValue, search) %#ok<INUSD>
    suffix = extractAfter(tabName, varName);
    cmd = sprintf("app.modelData.tunableVariables(search).Value%s", suffix);
    var = eval(cmd);
    varClass = class(var); %#ok<NASGU>
    eval(cmd + " = cast(newValue, varClass);");
end

% -------------------------------------------------------------------------

function updateTabsForTopVar(topVar, varName, tabName, app)
    suffix = extractAfter(tabName, varName);
    if contains(suffix, ".")
      parts = split(suffix, ".");
      topVarName = extractBefore(tabName, "." + parts(2));
    end
    
    tabGroup = app.ModelAndVariablesView;
    tabs = tabGroup.Children;
    
    for tab = reshape(tabs, [1, numel(tabs)])
      tabVarName = tab.Title;
      if ~startsWith(tabVarName, topVarName)
        continue;
      end
      app.Helper.fillVariableEditTab(tabVarName, topVar, 'Update');
    end
end

% -------------------------------------------------------------------------

function varTable = getVarTable(mode, varName, app)
    tabGroup = app.ModelAndVariablesView;
    if isequal(mode, 'Create')
        varTable = createNewTabWithTable(tabGroup, varName, app);
    else
        tab = findobj(tabGroup, "Title", varName);
        varTable = findobj(tab, "Type", 'uitable');
    end
end

% -------------------------------------------------------------------------

function subVar = evalSubVarValue(varName, var, appHelper) %#ok<INUSL>
    topVarName = appHelper.extractTopVarName(varName);
    subVar = eval("var" + extractAfter(varName, topVarName));
end

% -------------------------------------------------------------------------