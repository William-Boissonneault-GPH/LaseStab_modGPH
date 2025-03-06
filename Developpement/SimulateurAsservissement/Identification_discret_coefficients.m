num = [1 5];      % s + 5
den = [1 6 5];    % s^2 + 6s + 5

Ts1 = 0.011;        % sample time = 10 ms (100 Hz)
Ts2 = 0.005;
method = 'zoh';   % zero-order hold discretization

[b, a] = continuousToDiscreteCoeffs(num, den, Ts1, method);
[b, a] = continuousToDiscreteCoeffs(num, den, Ts2, method);

function [bCoeffs, aCoeffs] = continuousToDiscreteCoeffs(num, den, Ts, method)
% continuousToDiscreteCoeffs
%   Converts a continuous-time transfer function G(s) = num(s)/den(s)
%   to a discrete-time transfer function G(z) using the specified
%   sample time Ts and method (e.g. 'zoh', 'tustin', etc.).
%   Returns the discrete numerator bCoeffs and denominator aCoeffs
%   so that H(z) = (b0 + b1 z^-1 + ... + bM z^-M) / (1 + a1 z^-1 + ... + aN z^-N).
%
%   Example usage:
%      num = [1 5];          % s^1 + 5
%      den = [1 6 5];        % s^2 + 6s + 5
%      Ts  = 0.01;           % 100 Hz sample
%      method = 'zoh';       % Zero-Order Hold discretization
%      [b, a] = continuousToDiscreteCoeffs(num, den, Ts, method);
%      % b, a are the polynomials in z^-1

    % 1) Create continuous-time TF object
    sysC = tf(num, den);

    % 2) Discretize
    sysD = c2d(sysC, Ts, method);

    % 3) Extract discrete-time numerator & denominator vectors
    %    tfdata(...) returns cell arrays by default; the 'v' option
    %    gives numeric row vectors for b, a in descending powers of z^-1.
    [b, a] = tfdata(sysD, 'v');

    % b and a are typically of the form:
    %   H(z) = (b(1) + b(2) z^-1 + ... ) / (a(1) + a(2) z^-1 + ...)
    %
    % Normally a(1) = 1 if the system is properly normalized.

    % 4) Output them
    bCoeffs = b;
    aCoeffs = a;

    % 5) (Optional) Print them in a friendly format for Arduino difference eq:
    fprintf('Discretized transfer function (method=%s, Ts=%g):\n', method, Ts);
    fprintf('Numerator b = [');
    fprintf('%.6g ', b);
    fprintf(']\nDenominator a = [');
    fprintf('%.6g ', a);
    fprintf(']\n\n');
    
    % Quick help for difference equation:
    %  H(z) = B(z^-1) / A(z^-1) = (b0 + b1 z^-1 + ... + bM z^-M) / (1 + a1 z^-1 + ... + aN z^-N).
    % The corresponding time-domain recursion is:
    %  y[n] = b0*x[n] + b1*x[n-1] + ... + bM*x[n-M]
    %         - a1*y[n-1] - ... - aN*y[n-N].
end
