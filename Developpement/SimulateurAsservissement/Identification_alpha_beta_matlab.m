% =========================================================================
% 1) Lecture du fichier CSV
% =========================================================================

% Supposons que votre fichier s'appelle "donnees_temperature.csv"
% et qu'il contient un en-tête (première ligne) avec les noms des colonnes.
% Dans ce cas, on peut utiliser readtable ou readmatrix.

% Méthode 1 : readtable (recommandée si la première ligne contient l’en-tête)
dataTable = readtable('N900_N600.csv');

% Supposez que les noms de colonnes sont : "time", "T1", "T2", "T3".
% Vous pouvez alors extraire vos variables ainsi :
time = dataTable.time;
T1   = dataTable.tempTec;
T2   = dataTable.tempMilieu;
T3   = dataTable.tempLaser;

% Méthode 2 : readmatrix (si pas d’en-tête)
% data = readmatrix('donnees_temperature.csv');
% time = data(:,1);
% T1   = data(:,2);
% T2   = data(:,3);
% T3   = data(:,4);

% =========================================================================
% 2) Identification de alpha et beta par régression linéaire
% =========================================================================

% On veut résoudre T3 = alpha*T1 + beta*T2
% Au sens des moindres carrés, on forme la matrice A et le vecteur b :
A = [T1, T2];  % Matrice N x 2
b = T3;        % Vecteur N x 1

% Résolution du problème A*x = b au sens des moindres carrés
x = A \ b;

% Récupération des coefficients alpha et beta
alpha = x(1);
beta  = x(2);

% =========================================================================
% 3) Calcul de T3 estimé et visualisation (optionnel)
% =========================================================================

T3_estime = alpha * T1 + beta * T2;

% Affichage des valeurs trouvées
fprintf('Valeur estimée de alpha : %.4f\n', alpha);
fprintf('Valeur estimée de beta  : %.4f\n',  beta);

% Comparaison graphique entre T3 mesurée et T3 estimée
figure;
plot(time, T3, 'b-', 'LineWidth', 1.5); hold on;
plot(time, T3_estime, 'r--', 'LineWidth', 1.5);
legend('T3 mesurée', 'T3 estimée');
xlabel('Temps');
ylabel('Température');
title('Comparaison entre T3 mesurée et T3 estimée');
grid on;
