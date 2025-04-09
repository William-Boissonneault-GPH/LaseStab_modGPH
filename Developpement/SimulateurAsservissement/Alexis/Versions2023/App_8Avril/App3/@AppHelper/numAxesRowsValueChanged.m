function numAxesRowsValueChanged(obj, ~)
%NUMAXESROWSVALUECHANGED Callback for when the number of plot-grid rows
%changes.
%   Responsible for updating the plot-grid by adding/deleting plot rows
%   based on the old and new values of the associated control. The behavior
%   can be summarized as follows:
%       - Throw an error if number of rows has not changed
%       - Delete bottom-most row if number of rows decreased
%           > if the deleted row had an active plot, activate the one
%             closest to it in the newly-added row
%       - Add row to the bottom of the last row
%           > if the active plot is in the old last row, activate the
%           one closest to it in the newly-added row

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    
    newNumAxesRows = app.NumAxesRows.Value;
    currNumAxesRows = length(app.AxesGL.RowHeight);
    
    assert(currNumAxesRows ~= newNumAxesRows);
    app.AxesGL.Visible = 'off';
    if newNumAxesRows < currNumAxesRows
        selAxesCol = deleteBottomRows(app, newNumAxesRows);
        if isempty(app.selectedAxes) % selected axes was deleted
            selectAxesClosestToDeleted(app, newNumAxesRows, selAxesCol);
        end
    else
        addRowsAtTheBottom(app, currNumAxesRows, newNumAxesRows);
        selectClosestNewlyAddedAxes(app, currNumAxesRows);
    end
    
    app.Helper.reflowAxesGLContents();
    app.AxesGL.Visible = 'on';
end

% -------------------------------------------------------------------------
% Local functions
% -------------------------------------------------------------------------

function selAxesCol = deleteBottomRows(app, newNumAxesRows)
    selAxesCol = app.selectedAxes.Layout.Column;
    axs = findobj(app.AxesGL,'Type','axes');
    for ia = 1:length(axs)
        ir = axs(ia).Layout.Row;
        if (ir > newNumAxesRows)
            if axs(ia) == app.selectedAxes
                app.selectedAxes = matlab.ui.control.UIAxes.empty();
                selAxesCol = axs(ia).Layout.Column;
            end
            delete(axs(ia));
        end
    end
end

% -------------------------------------------------------------------------

function selectAxesClosestToDeleted(app, newNumAxesRows, selAxesCol)
    axs = findobj(app.AxesGL, 'Type','axes');
    for ia = 1:length(axs)
        if (axs(ia).Layout.Row == newNumAxesRows && ...
                axs(ia).Layout.Column == selAxesCol)
            app.Helper.setSelectedAxes(axs(ia));
            break;
        end
    end
end

% -------------------------------------------------------------------------

function addRowsAtTheBottom(app, currNumAxesRows, newNumAxesRows)
    app.AxesGL.RowHeight = repmat({'1x'}, 1, newNumAxesRows);
    for ir = currNumAxesRows+1:newNumAxesRows
        for ic = 1:app.NumAxesCols.Value
            app.Helper.createAxes(ir,ic);
        end
    end
end

% -------------------------------------------------------------------------

function selectClosestNewlyAddedAxes(app, currNumAxesRows)
    axs = findobj(app.AxesGL,'Type','axes');
    for ia = 1:length(axs)
        if (axs(ia).Layout.Row == currNumAxesRows + 1 && ...
                axs(ia).Layout.Column == app.selectedAxes.Layout.Column)
            app.Helper.setSelectedAxes(axs(ia));
            break;
        end
    end
end

% -------------------------------------------------------------------------
