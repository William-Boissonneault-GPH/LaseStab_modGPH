function setSelectedAxes(obj, axs)
%SETSELECTEDAXES Select an axes and update the associated signal
%checkboxes to only represent plotted signals.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    if ~isempty(app.selectedAxes)
        app.selectedAxes.Selected = ~(app.selectedAxes.Selected);
    end
    app.selectedAxes = axs;
    axs.Selected = 'on';

    % uncheck all signal selections
    cbxes = findobj(app.SigsGL, 'Type', 'uicheckbox');
    set(cbxes, 'Value',false);

    % check only the signals plotted in the selected axes
    lhs = app.selectedAxes.Children;
    for ilh = 1:numel(lhs)
        sigTag = lhs(ilh).Tag;
        cbx = findobj(app.SigsGL, 'Type', 'uicheckbox', 'Tag', sigTag);
        assert(~isempty(cbx));
        cbx.Value = true;
    end
end

% LocalWords:  uicheckbox
