function numAxesColsValueChanged(obj, ~)
%NUMAXESCOLSVALUECHANGED Callback for when the number of plot-grid columns
%changes.
%   Responsible for updating the plot-grid by adding/deleting plot columns
%   based on the old and new values of the associated control. The behavior
%   can be summarized as follows:
%       - Throw an error if number of columns has not changed
%       - Delete right-most column if number of columns decreased
%           > if the deleted column had an active plot, activate the one
%             closest to it in the newly-added column
%       - Add column to the right of the last column
%           > if the active plot is in the old last column, activate the
%           one closest to it in the newly-added column

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    
    newNumAxesCols = app.NumAxesCols.Value;
    currNumAxesCols = length(app.AxesGL.ColumnWidth);
    
    assert(currNumAxesCols ~= newNumAxesCols);
    app.AxesGL.Visible = 'off';
    if newNumAxesCols < currNumAxesCols
        selAxesRow = deleteRightMostColumns(app, newNumAxesCols);
        if isempty(app.selectedAxes) % selected axes was deleted
            selectAxesClosestToDeleted(app, newNumAxesCols, selAxesRow);
        end
        app.AxesGL.ColumnWidth = repmat({'1x'}, 1, newNumAxesCols);
    else
        addColumnsOnTheRight(app, currNumAxesCols, newNumAxesCols);
        selectClosestNewlyAddedAxes(app, currNumAxesCols);
    end
    app.AxesGL.Visible = 'on';
end

% -------------------------------------------------------------------------
% Local functions
% -------------------------------------------------------------------------

function selAxesRow = deleteRightMostColumns(app, newNumAxesCols)
    selAxesRow = app.selectedAxes.Layout.Row;
    axs = findobj(app.AxesGL,'Type','axes');
    for ia = 1:length(axs)
        ic = axs(ia).Layout.Column;
        if (ic > newNumAxesCols)
            if axs(ia) == app.selectedAxes
                app.selectedAxes = matlab.ui.control.UIAxes.empty();
                selAxesRow = axs(ia).Layout.Row;
            end
            delete(axs(ia));
        end
    end
end

% -------------------------------------------------------------------------

function selectAxesClosestToDeleted(app, newNumAxesCols, selAxesRow)
    axs = findobj(app.AxesGL, 'Type','axes');
    for ia = 1:length(axs)
        if (axs(ia).Layout.Column == newNumAxesCols && ...
            axs(ia).Layout.Row == selAxesRow)
            app.Helper.setSelectedAxes(axs(ia));
            break;
        end
    end
end

% -------------------------------------------------------------------------

function addColumnsOnTheRight(app, currNumAxesCols, newNumAxesCols)
    app.AxesGL.ColumnWidth = repmat({'1x'}, 1, newNumAxesCols);
    for ic = currNumAxesCols+1:newNumAxesCols
        for ir = 1:app.NumAxesRows.Value
            app.Helper.createAxes(ir,ic);
        end
    end
end

% -------------------------------------------------------------------------

function selectClosestNewlyAddedAxes(app, currNumAxesCols)
    axs = findobj(app.AxesGL,'Type','axes');
    for ia = 1:length(axs)
        if (axs(ia).Layout.Column == currNumAxesCols+1 && ...
            axs(ia).Layout.Row == app.selectedAxes.Layout.Row)
            app.Helper.setSelectedAxes(axs(ia));
            break;
        end
    end
end

% -------------------------------------------------------------------------
