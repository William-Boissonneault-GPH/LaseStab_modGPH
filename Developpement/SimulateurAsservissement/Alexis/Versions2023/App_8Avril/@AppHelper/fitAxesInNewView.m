function fitAxesInNewView(obj)
%FITAXESINNEWVIEW Adjust the heights of all plot axes to be evenly sized
%within the total available height.

%   Copyright 2021 The MathWorks, Inc.

    app = obj.App;
    app.AxesGL.Visible = 'off';
    app.AxesGL.RowHeight = repmat({'1x'}, 1, app.NumAxesRows.Value);
    app.Helper.reflowAxesGLContents();
    app.AxesGL.Visible = 'on';
end
