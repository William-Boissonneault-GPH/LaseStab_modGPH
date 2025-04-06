function debugTrace(obj, str)

%   Copyright 2022 The MathWorks, Inc.

    if ~obj.App.debugTrace, return; end
    dbg = dbstack; fprintf('%s @ %s:%d <%s>\n', datestr(now), dbg(2).file, dbg(2).line, str);

end
