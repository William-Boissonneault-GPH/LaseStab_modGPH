function setUIControlState(obj, state)
%SETUICONTROLSTATE Helper method to disable/re-enable UI controls not
%intended to be active during a simulation.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    uics = findall(app.GUI);
    for idx = 1:length(uics)
        uic = uics(idx);
        if (isprop(uic, 'Type') && isequal(uic.Type, 'uilabel')) || ...
                (isprop(uic, 'Tag') && ismember(uic.Tag, AppHelper.NonSimUIControls))
            continue;
        end
        if isprop(uic, 'Enable')
            uic.Enable = state;
        end
    end
end

% LocalWords:  uilabel
