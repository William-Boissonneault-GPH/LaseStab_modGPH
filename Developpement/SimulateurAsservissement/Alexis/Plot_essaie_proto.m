% Read the CSV file into a table (replace 'data.csv' with your actual file)
T = readtable('ReponseEchelon16mars_vrai.csv');

% Create a new figure
figure;

% Plot Temp1, Temp2, and Temp3 vs. Time on the same axes
plot(T.Time, T.Temp1, 'LineWidth', 1.5);
hold on;
plot(T.Time, T.Temp2, 'LineWidth', 1.5);
plot(T.Time, T.Temp3, 'LineWidth', 1.5);
plot(T.Time, T.Setpoint, 'LineWidth', 1.5);

hold off;

% Label the axes and add a title
xlabel('Time');
ylabel('Temperature (°C)');
title('Temperature vs. Time');

% Add a legend
legend({'Temp1', 'Temp2', 'Temp3','Setpoint'}, 'Location', 'best');

% Display a grid
grid on;
