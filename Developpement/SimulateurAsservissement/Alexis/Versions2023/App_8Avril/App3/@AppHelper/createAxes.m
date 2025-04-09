function axes = createAxes(obj, row, column)
%CREATEAXES Add plot axes at the specified row and column and set it as the
%app's selected axes.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    locClearOldAxes(app, row, column);
    axes = uiaxes(app.AxesGL);
    axes.Layout.Row = row;
    axes.Layout.Column = column;
    axes.Box = 'on';
    axes.SelectionHighlight = 'on';
    axes.NextPlot = 'add';

    % set xlim based on  stop time, and if stop time is inf, use 10 because axes limits need to be finite
    st = eval(app.StopTimeEditField.Value);
    if ~isfinite(st), st = 10; end
    axes.XLim = [0 st];

    axes.ButtonDownFcn = app.createCallbackFcnProxy(@locAxesButtonDownFcn, true);
    if isempty(app.selectedAxes), app.Helper.setSelectedAxes(axes); end
    drawnow;
end

function locAxesButtonDownFcn(app, event)
    app.Helper.setSelectedAxes(event.Source);
end

function locClearOldAxes(app, row, column)
  allAxes = findall(app.AxesGL, 'type', 'axes');
  for axs = reshape(allAxes, 1, numel(allAxes))
    if axs.Layout.Row == row && axs.Layout.Column == column
      % Only empty selected axes if it happens to be the one being cleared.
      % A newly created axes is selected only if there are no axes selected
      % or if the one being replaced was already selected (for the latter,
      % this is accomplished by clearing the selected axes).
      if app.selectedAxes == axs
        app.selectedAxes = matlab.ui.control.UIAxes.empty();
      end
      delete(axs);
      break;
    end
  end
end

% LocalWords:  app's
