function tv2slsv_Out = tv2slsv(~, tv2slsv_Inp)
%TV2SLSV Convert tunable variables struct array to an array of
%Simulink.Simulation.Variable objects.
%   Return an array of Simulink.Simulation.Variable objects corresponding
%   to the specified tunable variable struct array with QualifiedName and
%   Value as the fields of the struct.

%   Copyright 2021 The MathWorks, Inc.
    
    if isempty(tv2slsv_Inp)
        tv2slsv_Out = [];
        return;
    end

    if isa(tv2slsv_Inp, 'Simulink.Simulation.Variable')
        tv2slsv_Out = tv2slsv_Inp;
        return;
    end

    %%% DO NOT ADD ANY CODE IN THIS SECTION %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    for tv2slsv_Idx = 1:numel(tv2slsv_Inp)
        eval(tv2slsv_Inp(tv2slsv_Idx).QualifiedName ...
            + "= tv2slsv_Inp(tv2slsv_Idx).Value;");
    end
    tv2slsv_VarNames = setdiff(string(who), ["tv2slsv_Inp", "tv2slsv_Idx"]);
    %%% DO NOT ADD ANY CODE IN THIS SECTION %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    for tv2slsv_Idx = 1:numel(tv2slsv_VarNames)
        eval("tv2slsv_VarValue = " + tv2slsv_VarNames(tv2slsv_Idx) + ";");
        % TODO: Workspace is not currently part of tv
        tv2slsv_Out(tv2slsv_Idx) = ...
            Simulink.Simulation.Variable(...
            tv2slsv_VarNames(tv2slsv_Idx), ...
            tv2slsv_VarValue, ...
            'Workspace', tv2slsv_Inp(tv2slsv_Idx).Workspace);  %#ok<AGROW>
    end
end
