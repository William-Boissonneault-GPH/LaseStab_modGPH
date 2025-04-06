function data = showMessage(obj, msg, title, type)
%SHOWMESSAGE Present a message to the user in a dialog based on the
%provided message type and having the supplied title.

%   Copyright 2021 The MathWorks, Inc.

    arguments
        obj
        msg     (1,1) string
        title   (1,1) string
        type    (1,1) string {mustBeMember(type, ...
            {'info', 'warning', 'error', 'question'})} = "error"
    end
    
    switch type
        case {'info', 'warning', 'error'}
            uialert(obj.App.GUI, msg, title, "Icon", type,'Interpreter','html');
    
        case 'question'
            optionYes = message("simulinkcompiler:genapp:OptionYes").getString;
            optionNo = message("simulinkcompiler:genapp:OptionNo").getString;
            data = uiconfirm(obj.App.GUI, msg, title, ...
                'Options', {optionYes, optionNo}, ...
                'DefaultOption', 1, ...
                'CancelOption', 2, ...
                'Interpreter', 'html');
    end

end