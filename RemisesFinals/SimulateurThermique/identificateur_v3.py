import numpy as np
import matplotlib.pyplot as plt
import _tkinter as tkr
import csv
from scipy.interpolate import UnivariateSpline
from scipy.stats import linregress

"""Ce fichier, combiné au code source du simulateur physique, permet l'identification d'un quelqu'onque protoype
Du travai manuel dans le code est necessaire pour activer chaque étape d'identification. Cela dit chaque fonction utilisé
Ce retrouve dans ce fichier.

1. L'indentification du coeficients de convection (h) est déterminé par la dérivée de température T2 T3 à le fermeture du TEC
à plusieurs niveau. Une regression linéaire est utilisé pour obtenir le h final 

2. Le ratio T3-Tamb/T1-Tamb peut être ajusté avec k pour son identification.

3. Finalement, le TEC est lui même identifié en effectuant 7 simulations en simultané pour chaque puissance de TEC récolté. Permettant 
la modélisation du TEC par un polynome de degrée deux"""

from PlaqueThermique import PlaqueThermique
from ActuateurThermique import ActionneurThermique
from ActuateurThermique import ActionneurThermiqueSIMPLE

from ActuateurThermique import predict_Q
from thermistance import thermo

epaisseurPlaque = 1.6 * 10**-3
AireTEC = 0.0156**2
rho = 2700
cp = 900

T_amb = 23
startTime = 29
endTime = 1000
totalTime = 600
courrantDEchelon = -3

indiceFichier = 4

NomDeFichier = ["donnéesProto/mesures_3A.csv",
                "donnéesProto/mesures_2A.csv",
                "donnéesProto/mesures_1_5A.csv",
                "donnéesProto/mesures_-1_5A.csv",
                "donnéesProto/mesures_-3A.csv",
                ]
Amperage = [
            3,
            2,
            1.5,
            -1.5,
            -3
            ]

### Aller chercher les données du prototype
EssaisProto = []
for nom in NomDeFichier:
    time=[]
    T1=[]
    T2=[]
    T3=[]
    with open(nom, mode="r", encoding="ISO-8859-1") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first header row
        next(reader)  # Skip the duplicate header row

        for row in reader:
            time.append(int(row[0]))  # Convert time to integer
            T1.append(float(row[1]))  # Convert temperatures to float
            T2.append(float(row[2]))
            T3.append(float(row[3]))
    T1 = np.array(T1)
    T2 = np.array(T2)
    T3 = np.array(T3)

    EssaisProto.append({
        "time" : time,
        "T1" : T1,
        "T2" : T2,
        "T3" : T3
    })

EssaiPerturb = []
time=[]
T1=[]
T2=[]
T3=[]
nomfichier=r'C:\Users\willi\OneDrive - Université Laval\Cours\HIV2025\ModelisationGPH\LaseStab_modGPH\Developpement\SimulateurPhysique\Perturbation_temp_piece.csv'
with open(nomfichier, mode="r", encoding="ISO-8859-1") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the first header row
    next(reader)  # Skip the duplicate header row

    for row in reader:
        time.append(int(row[0]))  # Convert time to integer
        T1.append(float(row[1]))  # Convert temperatures to float
        T2.append(float(row[2]))
        T3.append(float(row[3]))
T1 = np.array(T1)
T2 = np.array(T2)
T3 = np.array(T3)

EssaiPerturb.append({
    "time" : time,
    "T1" : T1,
    "T2" : T2,
    "T3" : T3
})


dT_dt_fermetureTEC = []
deltaT_conv_fermeture = []
i_fermeture_TEC = []

fig, ax = plt.subplots(2, 1, figsize=(6, 4), sharex=True)

for i, essai in enumerate(EssaisProto):
        # Fit a smoothing spline
    x = essai["time"]
    y = essai["T3"]
    spline = UnivariateSpline(x, y, s=3)  # s controls the smoothness
    y_smooth = spline(x)

    # Compute the first derivative
    dy_dx = spline.derivative()(x)
    # Plot results

    ax[0].plot(x, y, 'o', markersize=3, alpha=0.5, label="Noisy Data")
    ax[0].plot(x, y_smooth, linewidth=2, label="Smoothed Curve")
    ax[0].set_ylabel("Temperature [C]")
    #ax[0].legend()

    ax[1].plot(x, dy_dx, 'r', linewidth=2, label="Derivative")
    ax[1].set_xlabel("temps [sec]")
    ax[1].set_ylabel("dT/dt [K/sec]")
    #ax[1].legend()

    i_fermeture = 0
    if Amperage[i] > 0:
        dT_dt_fermetureTEC.append(np.min(dy_dx[100:]))
        i_fermeture = np.argmin(dy_dx[100:])+100

    else:
        dT_dt_fermetureTEC.append(np.max(dy_dx[100:]))
        i_fermeture = np.argmax(dy_dx[100:])+100

    deltaT_conv_fermeture.append(T_amb-y_smooth[i_fermeture])

    i_fermeture_TEC.append(i_fermeture)

    plt.scatter(i_fermeture+1, dT_dt_fermetureTEC[-1])

    #plt.show()
for i, essai in enumerate(EssaisProto):
        # Fit a smoothing spline
    x = essai["time"]
    y = essai["T1"]
    spline = UnivariateSpline(x, y, s=3)  # s controls the smoothness
    y_smooth = spline(x)

    # Compute the first derivative
    dy_dx = spline.derivative()(x)

    ax[0].plot(x, y, 'o', markersize=3, alpha=0.5, label="Noisy Data")
    ax[0].plot(x, y_smooth, linewidth=2, label="Smoothed Curve")
    ax[0].set_ylabel("Température [C]")
    #ax[0].legend()

    ax[1].plot(x, dy_dx, 'r', linewidth=2, label="Derivative")
    ax[1].set_xlabel("temps [sec]")
    ax[1].set_ylabel("dT/dt [K/sec]")
    #ax[1].legend()

    i_fermeture = 0
    if Amperage[i] > 0:
        dT_dt_fermetureTEC.append(np.min(dy_dx[100:]))
        i_fermeture = np.argmin(dy_dx[100:])+100

    else:
        dT_dt_fermetureTEC.append(np.max(dy_dx[100:]))
        i_fermeture = np.argmax(dy_dx[100:])+100

    deltaT_conv_fermeture.append(T_amb-y_smooth[i_fermeture])

    i_fermeture_TEC.append(i_fermeture)

    plt.scatter(i_fermeture+1, dT_dt_fermetureTEC[-1])

    #plt.show()
plt.show()

plt.figure(figsize=(6, 3))
plt.scatter(deltaT_conv_fermeture, dT_dt_fermetureTEC, label="Données", color='green')

slope, intercept, _, _, std_err_slope = linregress(deltaT_conv_fermeture, dT_dt_fermetureTEC)
incert_slope = std_err_slope *2
x_vals = np.linspace(min(deltaT_conv_fermeture), max(deltaT_conv_fermeture), 100)
y_vals = slope * x_vals + intercept
plt.plot(x_vals, y_vals, color='red', label=f"Régression: y = ({slope:.4f}+-{incert_slope:.4f})x + {intercept:.4f}")

plt.xlabel("(Tamb - T) [C]")
plt.ylabel("dT/dt à la fermeture [K/sec]")
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.show()

h_rhocp_experimental = (slope * epaisseurPlaque) / 2
h = h_rhocp_experimental * rho * cp

print(f'experimental h: {h}, valeur reference : {15/(900*2700)}')


def simulationMultiplesPuissanceTEC(courrantIndice, fileName, currentsPassed):

    TunningRange = 1 #Watts
    Q_predicted = predict_Q(0, Amperage[courrantIndice], T_amb) * 0.6
    #Pour plusieurs simulation
    PuissanceATester = np.linspace(Q_predicted - TunningRange, Q_predicted + TunningRange,7)

    PuissanceATester = [1]


    color = ['red','black','orange','blue','green','gray','purple']

    Plaques = []
    thermos = []
    Tecs = []

    position1 = (0.11875 - 0.014, 0.031)  
    position2 = (0.11875 - 0.0604, 0.031) 
    position3 = (0.11875 - 0.1065, 0.031) 
        # Créer des instances de thermoresistance
        
    for PuissanceTec in PuissanceATester:
        #plaque = PlaqueThermique((0.11875,0.062,0.002), (k_rhocp * (1/(cTec_rhocp / cTec)), 1, 1/(cTec_rhocp / cTec)), h_rhocp * (1/(cTec_rhocp / cTec)), (0.001,0.001), T_amb)
        plaque = PlaqueThermique((0.11875,0.062,0.0016), (180, 900, 2700), 14, (0.001,0.001), T_amb)
        Tec = ActionneurThermiqueSIMPLE((0.096, 0.031), (0.015,0.0156), plaque.matTemperature, plaque.dimensionsElementFinie)

        thermo1 = thermo(position=position1, diamètre=0.008, épaisseur=0.001, plaque=plaque)
        thermo2 = thermo(position=position2, diamètre=0.008, épaisseur=0.001, plaque=plaque)
        thermo3 = thermo(position=position3, diamètre=0.008, épaisseur=0.001, plaque=plaque)

        Plaques.append(plaque)
        thermos.append([thermo1, thermo2, thermo3])
        Tecs.append(Tec)

    #garder le même ratio
    #= 800
    num_frames = int(1.5 * totalTime * 1000)
    dTime = totalTime/num_frames
    ##Nombre de frame skippé dans l'animation
    animationStep = 1600

    echelonCourant = 0

    temperatures = [[]]
    time = []
    
    for i in range(num_frames):
            ###Effectue un échelon d'opération à mi chemin
            if i*dTime >= startTime:
                echelonCourant = currentsPassed[0]
            if i*dTime >= endTime:
                echelonCourant = currentsPassed[1]
    
            if i % animationStep == 0:
                print(i)
                for j, tec in enumerate(Tecs):
                    #tec.updateMatPerturbation(echelonCourant * PuissanceATester[j])
                    tec.updateMatQTECCourrant(echelonCourant * PuissanceATester[j])

                for j, thermistances in enumerate(thermos):
                    temperatures[j].append([thermistances[0].lire_temperature(), thermistances[1].lire_temperature(), thermistances[2].lire_temperature()])
                time.append(i*dTime)
            else:
                for j, plaque in enumerate(Plaques):
                    plaque.propagationDunPasDeTemps(dTime, T_amb, [Tecs[j].matQTEC])
            

    plt.plot(EssaisProto[courrantIndice]["time"][0:], EssaisProto[courrantIndice]["T3"][0:])
    plt.plot(EssaisProto[courrantIndice]["time"][0:], EssaisProto[courrantIndice]["T2"][0:])
    plt.plot(EssaisProto[courrantIndice]["time"][0:], EssaisProto[courrantIndice]["T1"][0:])



    #tempAAfficher = []

    for i, temps in enumerate(temperatures):
        temp1AAfficher = []
        temp2AAfficher = []
        temp3AAfficher = []
        for temp in temps:
            temp1AAfficher.append(temp[0])
            temp2AAfficher.append(temp[1])
            temp3AAfficher.append(temp[2])
        plt.plot(time, temp1AAfficher, label=f'{PuissanceATester[i]}', color=color[i])
        plt.plot(time, temp2AAfficher, color=color[i])
        plt.plot(time, temp3AAfficher, color=color[i])

    rows = zip(time, temp1AAfficher, temp2AAfficher, temp3AAfficher)

    # Write to CSV
    with open(fileName, "w", newline="") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["time(s)", "tempTec", "tempMilieu", "tempLaser"])
        # Write data
        writer.writerows(rows)

    print("CSV file saved successfully!")



    #plt.legend()
    #plt.show()

def simulationMultiplesPuissancePerturbateur():
    
    ## P = VI = V**2 / R = 5v**2 /25 = 1W
    #Pour plusieurs simulation
    PuissanceATester = np.linspace(0,1,7)

    color = ['red','black','orange','blue','green','gray','purple']

    Plaques = []
    thermos = []
    Tecs = []

    position1 = (0.11875 - 0.014, 0.031)  
    position2 = (0.11875 - 0.0604, 0.031) 
    position3 = (0.11875 - 0.1065, 0.031) 
        # Créer des instances de thermoresistance
        
    for PuissanceTec in PuissanceATester:
        #plaque = PlaqueThermique((0.11875,0.062,0.002), (k_rhocp * (1/(cTec_rhocp / cTec)), 1, 1/(cTec_rhocp / cTec)), h_rhocp * (1/(cTec_rhocp / cTec)), (0.001,0.001), T_amb)
        plaque = PlaqueThermique((0.11875,0.062,0.0016), (180, 900, 2700), 14, (0.001,0.001), T_amb)
        Tec = ActionneurThermiqueSIMPLE((0.096, 0.031), (0.015,0.0156), plaque.matTemperature, plaque.dimensionsElementFinie)

        thermo1 = thermo(position=position1, diamètre=0.008, épaisseur=0.001, plaque=plaque)
        thermo2 = thermo(position=position2, diamètre=0.008, épaisseur=0.001, plaque=plaque)
        thermo3 = thermo(position=position3, diamètre=0.008, épaisseur=0.001, plaque=plaque)

        Plaques.append(plaque)
        thermos.append([thermo1, thermo2, thermo3])
        Tecs.append(Tec)

    #garder le même ratio
    #= 800
    num_frames = int(1.5 * totalTime * 1000)
    dTime = totalTime/num_frames
    ##Nombre de frame skippé dans l'animation
    animationStep = 1600

    echelonCourant = 0

    temperatures = [[],[],[],[],[],[],[]]
    time = []

    mat_perturbs = []

    ###Genere perturbations
    for j, plaque in enumerate(Plaques):
        sourceChaleur = [{
                "x": 0.08155,
                "y": 0.031,
                "puissance": PuissanceATester[j]
            }]
        mat_perturb = plaque.generer_mat_pertub(sourceChaleur)
        mat_perturbs.append(mat_perturb)
    
    for j, tec in enumerate(Tecs):
                    #tec.updateMatPerturbation(echelonCourant * PuissanceATester[j])
                    tec.updateMatQTECCourrant(0)
    
    for i in range(num_frames):
            ###Effectue un échelon d'opération à mi chemin
            if i*dTime >= startTime:
                for j, plaque in enumerate(Plaques):
                    plaque.propagationDunPasDeTemps(dTime, T_amb, [Tecs[j].matQTEC, mat_perturbs[j]])
            else:
                for j, plaque in enumerate(Plaques):
                    plaque.propagationDunPasDeTemps(dTime, T_amb, [Tecs[j].matQTEC])
    
            if i % animationStep == 0:
                print(i)
                for j, tec in enumerate(Tecs):
                    #tec.updateMatPerturbation(echelonCourant * PuissanceATester[j])
                    tec.updateMatQTECCourrant(0)

                for j, thermistances in enumerate(thermos):
                    temperatures[j].append([thermistances[0].lire_temperature(), thermistances[1].lire_temperature(), thermistances[2].lire_temperature()])
                time.append(i*dTime)            

    plt.plot(EssaiPerturb[0]["time"][0:], EssaiPerturb[0]["T3"][0:])
    plt.plot(EssaiPerturb[0]["time"][0:], EssaiPerturb[0]["T2"][0:])
    plt.plot(EssaiPerturb[0]["time"][0:], EssaiPerturb[0]["T1"][0:])
    #tempAAfficher = []

    for i, temps in enumerate(temperatures):
        temp1AAfficher = []
        temp2AAfficher = []
        temp3AAfficher = []
        for temp in temps:
            temp1AAfficher.append(temp[0])
            temp2AAfficher.append(temp[1])
            temp3AAfficher.append(temp[2])
        plt.plot(time, temp1AAfficher, label=f'{PuissanceATester[i]}', color=color[i])
        plt.plot(time, temp2AAfficher, color=color[i])
        plt.plot(time, temp3AAfficher, color=color[i])

        

    rows = zip(time, temp1AAfficher, temp2AAfficher, temp3AAfficher)

    plt.show()

    # Write to CSV
    with open('test.csv', "w", newline="") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["time(s)", "tempTec", "tempMilieu", "tempLaser"])
        # Write data
        writer.writerows(rows)

    print("CSV file saved successfully!")



simulationMultiplesPuissancePerturbateur()

#Currents = [
#    [0.6, 0.8],
#    [0.6, 0.4],
#    [0.9,1.2],
#    [0.9,0.6],
#    [-0.6, -0.8],
#    [-0.6, -0.4],
#    [-0.9,-1.2],
#    [-0.9,-0.6]
#]

#for cur in Currents:
#    filename = f"model_14fev_{str(cur[0]*1000)}_{str(cur[1]*1000)}.csv"
#    simulationMultiplesPuissanceTEC(indiceFichier, filename, cur)
