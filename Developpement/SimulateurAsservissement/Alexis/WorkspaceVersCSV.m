% 1. Extract time and data
time = out.simout.Time;  % Time vector
data = out.simout.Data;  % Matrix of signal values (columns)

% 2. Plot all signals
figure;
plot(time, data, 'LineWidth', 1.5);
xlabel('Time (s)');
ylabel('Signal Value');
title('Simulation Results');
grid on;

% Define custom labels for the signals:
% Adjust the order if your columns are arranged differently.
legendEntries = {'Temp1', 'Temp2', 'Temp3', 'Setpoint'};
legend(legendEntries, 'Location', 'best');

% 3. Write the data to a CSV file
% Combine time (first column) and data (subsequent columns)
outputMatrix = [time, data];

% Option A: Write CSV without headers (MATLAB R2019a or later)
writematrix(outputMatrix, 'simOutput.csv');

% Option B: Write CSV with headers using a table (uncomment if needed)
% varNames = [{'Time'}, legendEntries];
% T = array2table(outputMatrix, 'VariableNames', varNames);
% writetable(T, 'simOutput_withHeaders.csv');
