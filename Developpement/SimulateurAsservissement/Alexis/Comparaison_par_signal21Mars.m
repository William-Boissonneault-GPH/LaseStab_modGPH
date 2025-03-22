%% Load CSV Data
T = readtable('ReponseEchelon16mars_vrai.csv');
time_csv     = T.Time;
temp1_csv    = T.Temp1;
temp2_csv    = T.Temp2;
temp3_csv    = T.Temp3;
setpoint_csv = T.Setpoint;

%% Extract Simulation Data from out.simout
% Assumes that out.simout.Data columns are arranged as: [Temp1, Temp2, Temp3, Setpoint]
time_sim   = out.tout;
data_sim   = out.logsout;
temp1_sim  = data_sim(:,1);
temp2_sim  = data_sim(:,2);
temp3_sim  = data_sim(:,3);
% setpoint_sim = data_sim(:,4);  % If you prefer the simulation setpoint, uncomment.

%% Figure for Temp1
figure;
plot(time_csv, temp1_csv, 'b-', 'LineWidth', 1.5); hold on;
plot(time_sim, temp1_sim, 'r--', 'LineWidth', 1.5);
plot(time_csv, setpoint_csv, 'k:', 'LineWidth', 1.5);

% --- Interpolation & Error Computation ---
% Interpolate CSV data onto simulation times
csv_interp_temp1 = interp1(time_csv, temp1_csv, time_sim, 'linear', 'extrap');
% Percent error (using CSV as the reference)
percent_error_temp1 = abs((temp1_sim - csv_interp_temp1) ./ csv_interp_temp1) * 100;

% Mean & Uncertainty (2×std)
mean_err_temp1   = mean(percent_error_temp1);
uncert_err_temp1 = 2*std(percent_error_temp1);

% Round using local helper functions (defined below)
[rounded_mean_t1, rounded_uncert_t1] = round_uncertainty(mean_err_temp1, uncert_err_temp1);

% Add a dummy plot for the legend to display these stats
plot(nan, nan, 'w', 'DisplayName', ...
    sprintf('Accord Temp1: %.2f±%.2f %%', rounded_mean_t1, rounded_uncert_t1));

hold off;
xlabel('Time');
ylabel('Temperature (°C)');
title('Temp1 vs. Time');
legend({'Proto Temp1', 'Sim Temp1', 'Setpoint', ...
    sprintf('Accord Temp1: %.2f±%.2f %%', rounded_mean_t1, rounded_uncert_t1)}, ...
    'Location', 'best');
grid on;

%% Figure for Temp2
figure;
plot(time_csv, temp2_csv, 'b-', 'LineWidth', 1.5); hold on;
plot(time_sim, temp2_sim, 'r--', 'LineWidth', 1.5);
plot(time_csv, setpoint_csv, 'k:', 'LineWidth', 1.5);

% Interpolate & Error
csv_interp_temp2 = interp1(time_csv, temp2_csv, time_sim, 'linear', 'extrap');
percent_error_temp2 = abs((temp2_sim - csv_interp_temp2) ./ csv_interp_temp2) * 100;

mean_err_temp2   = mean(percent_error_temp2);
uncert_err_temp2 = 2*std(percent_error_temp2);
[rounded_mean_t2, rounded_uncert_t2] = round_uncertainty(mean_err_temp2, uncert_err_temp2);

plot(nan, nan, 'w', 'DisplayName', ...
    sprintf('Accord Temp2: %.2f±%.2f %%', rounded_mean_t2, rounded_uncert_t2));

hold off;
xlabel('Time');
ylabel('Temperature (°C)');
title('Temp2 vs. Time');
legend({'Proto Temp2', 'Sim Temp2', 'Setpoint', ...
    sprintf('Accord Temp2: %.2f±%.2f %%', rounded_mean_t2, rounded_uncert_t2)}, ...
    'Location', 'best');
grid on;

%% Figure for Temp3
figure;
plot(time_csv, temp3_csv, 'b-', 'LineWidth', 1.5); hold on;
plot(time_sim, temp3_sim, 'r--', 'LineWidth', 1.5);
plot(time_csv, setpoint_csv, 'k:', 'LineWidth', 1.5);

% Interpolate & Error
csv_interp_temp3 = interp1(time_csv, temp3_csv, time_sim, 'linear', 'extrap');
percent_error_temp3 = abs((temp3_sim - csv_interp_temp3) ./ csv_interp_temp3) * 100;

mean_err_temp3   = mean(percent_error_temp3);
uncert_err_temp3 = 2*std(percent_error_temp3);
[rounded_mean_t3, rounded_uncert_t3] = round_uncertainty(mean_err_temp3, uncert_err_temp3);

plot(nan, nan, 'w', 'DisplayName', ...
    sprintf('Accord Temp3: %.2f±%.2f %%', rounded_mean_t3, rounded_uncert_t3));

hold off;
xlabel('Time');
ylabel('Temperature (°C)');
title('Temp3 vs. Time');
legend({'Proto Temp3', 'Sim Temp3 Estimé', 'Setpoint', ...
    sprintf('Accord Temp3: %.2f±%.2f %%', rounded_mean_t3, rounded_uncert_t3)}, ...
    'Location', 'best');
grid on;

%% Helper Functions
function y = round_to_sigfig(x, sigfigs)
    % Rounds x to the specified number of significant figures.
    if x == 0
        y = 0;
    else
        digits = -floor(log10(abs(x))) + (sigfigs - 1);
        y = round(x, digits);
    end
end

function [rounded_value, rounded_uncertainty] = round_uncertainty(value, uncertainty)
    % Rounds the uncertainty to 1 significant figure, and the value accordingly.
    rounded_uncertainty = round_to_sigfig(uncertainty, 1);
    
    if rounded_uncertainty == 0
        decimal_places = 0;
    else
        decimal_places = -floor(log10(abs(rounded_uncertainty)));
    end
    
    % Round the value to one fewer decimal place than the uncertainty
    rounded_value = round(value, decimal_places - 1);
end
