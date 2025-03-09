%------------------------------------------------------------
% Example: Multiply Two TFs and Print Polynomials,
%          Then Form the Closed Loop (with unity feedback)
%------------------------------------------------------------

% 1) Define the two transfer functions G1(s) and G2(s)
%    using numerator & denominator polynomials.

numG1 = [1 5];        % e.g. s + 5
denG1 = [1 6 5];      % e.g. s^2 + 6s + 5

numG2 = [1 2];        % e.g. s + 2
denG2 = [1 10];       % e.g. s + 10

% Build them as tf (transfer function) objects:
G1 = tf(numG1, denG1);
G2 = tf(numG2, denG2);

fprintf('G1(s) = \n');
G1  % prints in the Command Window

fprintf('G2(s) = \n');
G2

% 2) Multiply the two transfer functions (i.e. cascade connection)
G = G1 * G2;  % or use series(G1, G2)

fprintf('\n----------------------------------------\n');
fprintf('Multiplication result G(s) = G1(s)*G2(s):\n');
G

% 3) Print out the multiplied transfer function in polynomial form
[Gnum, Gden] = tfdata(G, 'v');  % 'v' returns row vectors
fprintf('Polynomial form of G(s):\n');
fprintf('  Numerator = ');
disp(Gnum);
fprintf('  Denominator = ');
disp(Gden);

% 4) Form the closed-loop transfer function with unity feedback
%    i.e., T(s) = G(s) / (1 + G(s)) by default in feedback(G,1).
CL = feedback(G, 1);

fprintf('\n----------------------------------------\n');
fprintf('Closed-Loop T(s) = G(s) / (1 + G(s)):\n');
CL

% 5) Print out polynomials for the closed-loop TF
[CLnum, CLden] = tfdata(CL, 'v');
fprintf('Polynomial form of T(s):\n');
fprintf('  Numerator = ');
disp(CLnum);
fprintf('  Denominator = ');
disp(CLden);
%------------------------------------------------------------
