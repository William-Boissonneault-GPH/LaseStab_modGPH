function showPanels(obj, panelsToShow)

    arguments
        obj
        panelsToShow (1,:) string = ["model", "params", "signals", "plots"]
    end

    app = obj.App;

    %   Copyright 2021 The MathWorks, Inc.

    if any(panelsToShow == "model") || any(panelsToShow == "params")
        if ~app.ScrollUpUIC.Enable
            app.Helper.scroll(app.ScrollDownUIC);
        end
        if ~app.ScrollTopLeftUIC.Enable && any(panelsToShow == "model")
            app.Helper.scroll(app.ScrollTopRightUIC);
        end
        if ~app.ScrollTopRightUIC.Enable && any(panelsToShow == "params")
            app.Helper.scroll(app.ScrollTopLeftUIC);
        end
    end

    if any(panelsToShow == "signals") || any(panelsToShow == "plots")
        if ~app.ScrollDownUIC.Enable
            app.Helper.scroll(app.ScrollUpUIC);
        end
        if ~app.ScrollBottomLeftUIC.Enable && any(panelsToShow == "signals")
            app.Helper.scroll(app.ScrollBottomRightUIC);
        end
        if ~app.ScrollBottomRightUIC.Enable && any(panelsToShow == "plots")
            app.Helper.scroll(app.ScrollBottomLeftUIC);
        end
    end
    
end % showPlanels
