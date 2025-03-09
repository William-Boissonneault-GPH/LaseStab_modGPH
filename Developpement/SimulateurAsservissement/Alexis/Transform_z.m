% ================================
% Discretizing a 2nd-order system
% with a sampling time of 2 s
% ================================

% 1) Define the Laplace variable
s = tf('s');

% 2) Define the continuous-time 2nd-order transfer function
G_s = (1 + 157*s + 3403*s^2) / (131*s + 3403*s^2);

% 3) Choose a sampling time (T = 2 s)
T = 2.0;  

% 4) Discretize the system using 'c2d'
%    We'll use Zero-Order Hold (ZOH) as an example
G_z_zoh = c2d(G_s, T, 'zoh');

% 5) Compare with another discretization method, e.g. Tustin (bilinear)
G_z_tustin = c2d(G_s, T, 'tustin');

% 6) Display the results
disp('--- Continuous-time G(s) ---');
G_s

disp('--- Discrete-time G(z) [ZOH] ---');
G_z_zoh

disp('--- Discrete-time G(z) [Tustin] ---');
G_z_tustin

% 7) (Optional) Compare Bode and Step responses
figure;
subplot(2,1,1)
bode(G_s, 'b', G_z_zoh, 'r--', G_z_tustin, 'g-.');
grid on;
title('Bode Comparison (Continuous vs. Discrete)');
legend('G(s)', 'G(z) ZOH', 'G(z) Tustin');

subplot(2,1,2)
step(G_s, 'b', G_z_zoh, 'r--', G_z_tustin, 'g-.');
grid on;
title('Step Response Comparison');
legend('G(s)', 'G(z) ZOH', 'G(z) Tustin');
