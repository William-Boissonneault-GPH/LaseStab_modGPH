function topVarName = extractTopVarName(~, varName)
%EXTRACTTOPVARNAME Extract the top-most variable name given a subscripted
%variable name.
%   This helper method is used by AppHelper.fillVariableEditTab to find the
%   name of the variable's base name excluding any indexing (e.g. array or
%   cell) and fields in case of a struct.
%
%   Examples:
%   "myStructArray(2).size.width" becomes "myStructArray"
%   "myStruct.a.b.c" becomes "myStruct"
%   "myArray(5)" becomes "myArray"
%   "myCell{3}.myArray(4)" becomes "myCell"

%   Copyright 2021 The MathWorks, Inc.

    arguments
        ~
        varName (1, 1) string
    end

    topVarName = varName;

    if contains(topVarName, '{')
        topVarName = extractBefore(topVarName, '{');
    end

    if contains(topVarName, '(')
        topVarName = extractBefore(topVarName, '(');
    end

    if contains(topVarName, '.')
        parts = split(topVarName, '.');
        topVarName = parts(1);
    end
end

% LocalWords:  subscripted
