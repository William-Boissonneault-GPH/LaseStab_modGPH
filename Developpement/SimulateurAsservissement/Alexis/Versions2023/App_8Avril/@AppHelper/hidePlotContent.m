function hidePlotContent(obj)
%HIDEPLOTCONTENT Hide the lines and legends of all app plots.
%   This utility method allows visually clearing the plots without having
%   to delete the contained line handles and legends. This makes updating
%   signal checkboxes based on the selected axes possible. When you press
%   the run button, the plots are visually cleared but you can maintain the
%   signals which are already selected for the active plot. Once the
%   simulation has completed, the updated values of the selected signals
%   are shown again.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    hideLines('line', app);
    hideLines('stair', app);

    allAxes = findobj(app.AxesGL, 'Type', 'axes');

    for axes = reshape(allAxes, 1, numel(allAxes))
        legend(axes, 'off');
    end
end

function hideLines(lineType, app)
    lines = findobj(app.AxesGL, 'Type', lineType);
    set(lines, 'LineStyle', 'none');
end
