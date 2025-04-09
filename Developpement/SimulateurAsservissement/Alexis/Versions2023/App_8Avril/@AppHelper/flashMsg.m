function flashMsg(obj, text)
% Utility to briefly flash a short message on the status field

%   Copyright 2022 The MathWorks, Inc.

    app = obj.App;
    app.StatusLabel.Text = text;
    app.StatusLabel.FontColor = [0 0.3922 0];
    drawnow limitrate;

    % start the one shot timer to clear the message after 2 seconds
    app.flashMsgTimer.TimerFcn = @(to, te) locClearStatusMsg(obj,to, te);
    app.flashMsgTimer.StartDelay = 2;
    app.flashMsgTimer.start;
end

function locClearStatusMsg(obj, ~, ~)
    app = obj.App;
    app.StatusLabel.Text = "";
    app.StatusLabel.FontColor = [0 0 0];
    drawnow limitrate;
end
