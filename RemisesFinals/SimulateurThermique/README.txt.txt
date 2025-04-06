

balbslbasl


NOM et NI 


Inclus dans ce fichier: 

-Simulateur physique:
	Fonctionnement: 
	1. Ouvrir l'executable
	2. Simluer!

-Manuel d'instructions

-Code source

-Identificateur: 
	Ce fichier, combiné au code source du simulateur physique, permet l'identification d'un quelqu'onque protoype
	Du travai manuel dans le code est necessaire pour activer chaque étape d'identification. Cela dit chaque fonction utilisé
	Ce retrouve dans ce fichier.

	1. L'indentification du coeficients de convection (h) est déterminé par la dérivée de température T2 T3 à le fermeture du TEC
	à plusieurs niveau. Une regression linéaire est utilisé pour obtenir le h final 

	2. Le ratio T3-Tamb/T1-Tamb peut être ajusté avec k pour son identification.

	3. Finalement, le TEC est lui même identifié en effectuant 7 simulations en simultané pour chaque puissance de TEC récolté. Permettant 
	la modélisation du TEC par un polynome de degrée deux