function scroll(obj, control)
%SCROLL Expand or collapse a pane or a pane group horizontally or
%vertically based on the direction of the provided control.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    controlData = getControlData(app, control);
    siblingControl = getControlSibling(controlData);

    % assumption parent ctrlsGL is [1x, pullLeftCtlr, pullRightCtrl, 1x]
    
    if isequal(controlData.layoutRow, "middle") % vertical scroll
    
        if isequal(siblingControl.Enable, 'on')
            control.Enable = 'off';
            paneGroupId = controlData.paneGroups.(controlData.direction);
            app.(paneGroupId).Visible = 'off';
        else
            siblingControl.Enable = 'on';
            paneGroupId = controlData.paneGroups.(controlData.siblingDirection);
            app.(paneGroupId).Visible = 'on';
        end
    
        app.Helper.fitAxesInNewView();
        app.Helper.setMainGLRowHeight();

    else % horizontal scroll
        % assumption: shuttersGL is [leftObj, ctrlsGL, rightObj]    
        if isequal(siblingControl.Enable,'on')
            control.Enable = 'off';
            paneId = controlData.panes.(controlData.direction);
            paneToHide = app.(paneId);
            paneToHide.Visible = 'off';
            controlData.shuttersGL.ColumnWidth = ...
                columnWidthForCollapasedControl(controlData);
        else
            siblingControl.Enable = 'on';  
            paneId = controlData.panes.(controlData.siblingDirection);
            paneToShow = app.(paneId);
            paneToShow.Visible = 'on';
            controlData.shuttersGL.ColumnWidth = ...
                columnWidthInSplitView(controlData);
        end
    end

    % Change data on the model view to initiate a fit-to-view action
    app.ModelHTML.Data = rand;
end

function sibling = getControlSibling(controlData)
    sibling = findobj(controlData.parent, 'Tag', controlData.siblingTag);
    assert(~isempty(sibling));
end

function data = getControlData(app, control)
    data.parent = control.Parent;
    data.shuttersGL = control.Parent.Parent;

    idxTop = find(app.Helper.TopScrollButtons == control.Tag);

    if ~isempty(idxTop)
        siblingIdx = 3-idxTop;
        data.direction = app.Helper.HorizontalDirections(idxTop);
        data.siblingDirection = app.Helper.HorizontalDirections(siblingIdx);
        data.layoutRow = app.Helper.LayoutRows(1);
        data.tag = app.Helper.TopScrollButtons(idxTop);
        data.siblingTag = app.Helper.TopScrollButtons(siblingIdx);
        data.panes.left = app.Helper.TopPanes(1);
        data.panes.right = app.Helper.TopPanes(2);
        return;
    end

    idxMiddle = find(app.Helper.MiddleScrollButtons == control.Tag);

    if ~isempty(idxMiddle)
        siblingIdx = 3-idxMiddle;
        data.direction = app.Helper.VerticalDirections(idxMiddle);
        data.siblingDirection = app.Helper.VerticalDirections(siblingIdx);
        data.layoutRow = app.Helper.LayoutRows(2);
        data.tag = app.Helper.MiddleScrollButtons(idxMiddle);
        data.siblingTag = app.Helper.MiddleScrollButtons(siblingIdx);
        data.paneGroups.up = app.Helper.PaneGroups(1);
        data.paneGroups.down = app.Helper.PaneGroups(2);
        return;
    end

    idxBottom = find(app.Helper.BottomScrollButtons == control.Tag);
    siblingIdx = 3-idxBottom;
    data.direction = app.Helper.HorizontalDirections(idxBottom);
    data.siblingDirection = app.Helper.HorizontalDirections(siblingIdx);
    data.layoutRow = app.Helper.LayoutRows(3);
    data.tag = app.Helper.BottomScrollButtons(idxBottom);
    data.siblingTag = app.Helper.BottomScrollButtons(siblingIdx);
    data.panes.left = app.Helper.BottomPanes(1);
    data.panes.right = app.Helper.BottomPanes(2);
end

function columnWidth = columnWidthForCollapasedControl(controlData)
    row = controlData.layoutRow;
    col = controlData.direction;

    columnWidths.top.left = {0,'fit','1x'};
    columnWidths.top.right = {'1x','fit',0};
    columnWidths.bottom.left = {0,'fit','1x'};
    columnWidths.bottom.right = {'1x','fit',0};

    columnWidth = columnWidths.(row).(col);
end

function columnWidth = columnWidthInSplitView(controlData)
    row = controlData.layoutRow;
    col = controlData.direction;

    columnWidths.top.left = {'1x','fit','fit'};
    columnWidths.top.right = {'1x','fit','fit'};
    columnWidths.bottom.left = {'fit','fit','1x'};
    columnWidths.bottom.right = {'fit','fit','1x'};

    columnWidth = columnWidths.(row).(col);
end

% LocalWords:  ctrls GL Ctlr
