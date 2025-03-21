%% Load CSV Data
T = readtable('ReponseEchelon16mars_vrai.csv');

% Extract CSV columns
time_csv     = T.Time;
temp1_csv    = T.Temp1;
temp2_csv    = T.Temp2;
temp3_csv    = T.Temp3;
setpoint_csv = T.Setpoint;

%% Extract Simulation Data from out.simout
% Assumes that out.simout.Data columns are arranged as: [Temp1, Temp2, Temp3, Setpoint]
time_sim   = out.simout.Time;
data_sim   = out.simout.Data;
temp1_sim  = data_sim(:,1);
temp2_sim  = data_sim(:,2);
temp3_sim  = data_sim(:,3);
setpoint_sim = data_sim(:,4);  % If needed; here we'll use the CSV setpoint

%% Figure for Temp1
figure;
plot(time_csv, temp1_csv, 'b-', 'LineWidth', 1.5); hold on;
plot(time_sim, temp1_sim, 'r--', 'LineWidth', 1.5);
plot(time_csv, setpoint_csv, 'k:', 'LineWidth', 1.5);
hold off;
xlabel('Time');
ylabel('Temperature (°C)');
title('Temp1 vs. Time');
legend({'Proto Temp1', 'Sim Temp1', 'Setpoint'}, 'Location', 'best');
grid on;

%% Figure for Temp2
figure;
plot(time_csv, temp2_csv, 'b-', 'LineWidth', 1.5); hold on;
plot(time_sim, temp2_sim, 'r--', 'LineWidth', 1.5);
plot(time_csv, setpoint_csv, 'k:', 'LineWidth', 1.5);
hold off;
xlabel('Time');
ylabel('Temperature (°C)');
title('Temp2 vs. Time');
legend({'Proto Temp2', 'Sim Temp2', 'Setpoint'}, 'Location', 'best');
grid on;

%% Figure for Temp3
figure;
plot(time_csv, temp3_csv, 'b-', 'LineWidth', 1.5); hold on;
plot(time_sim, temp3_sim, 'r--', 'LineWidth', 1.5);
plot(time_csv, setpoint_csv, 'k:', 'LineWidth', 1.5);
hold off;
xlabel('Time');
ylabel('Temperature (°C)');
title('Temp3 vs. Time');
legend({'Proto Temp3', 'Sim Temp3 Estimé', 'Setpoint'}, 'Location', 'best');
grid on;
