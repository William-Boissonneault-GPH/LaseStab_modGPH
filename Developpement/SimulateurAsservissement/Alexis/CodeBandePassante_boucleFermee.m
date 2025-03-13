% ----------------------------------------------------------
% Détermination de la bande passante d'une boucle fermée
% ----------------------------------------------------------

% 1) Définir la variable de Laplace
s = tf('s');

% 2) Définir une fonction de transfert en boucle ouverte, G(s).
%    Par exemple : G(s) = 10 / (1 + 0.1s).
G = 6/(1 + 131*s+3403*s^2);

% 3) Construire la fonction de transfert en boucle fermée
%    T_BF(s) = G(s) / [1 + G(s)].
T_BF = feedback(G, 1);  % feedback( G, 1 ) revient à G/(1+G)

% 4) Tracer le Bode de la boucle fermée
figure; 
bode(T_BF), grid on;
title('Bode - Fonction de transfert en boucle fermée');

% 5) Bande passante automatique via la fonction "bandwidth()"
bp = bandwidth(T_BF);

% 6) Affichage du résultat
%    Attention : bandwidth() renvoie la pulsation (rad/s), pas la fréquence en Hz.
%    Pour obtenir la fréquence en Hz, on divise par 2*pi.
disp('=== Résultats : ===');
fprintf('Bande passante (en rad/s) = %.3f rad/s\n', bp);
fprintf('Bande passante (en Hz)    = %.3f Hz\n', bp/(2*pi));
