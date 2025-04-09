function plotRefreshRateHzSliderValueChanged(obj)
%PLOTREFRESHRATEHZSLIDERVALUECHANGED Callback for the refresh rate slider.
%   Set the period of the timer used for refreshing simulation button
%   states and time based on the value of the slider.

%   Copyright 2021 The MathWorks, Inc.
    app = obj.App;

    restartTimer = false;
    if isequal(app.refreshTimer.Running,'on')
        % need to stop the timer to change the period
        stop(app.refreshTimer);
        % may need to wait a bit for the timer to stop
        for cnt=1:5
            if ~isequal(app.refreshTimer.Running,'on'), break; end
            pause(1); % pause to give a chance for the timer to stop
        end
        if isequal(app.refreshTimer.Running,'on')
            % still has not stopped, give up,
            uialert(app.GUI, message("simulinkcompiler:genapp:UnableToChangeRefreshRate").string, 'info');
            return;
        end
        restartTimer = true;
    end
    assert(~isequal(app.refreshTimer.Running,'on'));
    
    value = app.PlotRefreshRateHzSlider.Value;
    % round to a millisecond, and note the range is in log scale
    app.refreshTimer.Period = round(1000/(10^value))/1000;
    
    if restartTimer
        % restart timer if we stopped it here to udpate the period
        start(app.refreshTimer);
    end
end
