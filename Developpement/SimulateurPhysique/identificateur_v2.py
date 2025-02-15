import numpy as np
import matplotlib.pyplot as plt
import _tkinter as tkr
import csv
from scipy.interpolate import UnivariateSpline
from scipy.stats import linregress

from PlaqueThermique import PlaqueThermique
from ActuateurThermique import ActionneurThermique
from ActuateurThermique import predict_Q
from thermistance import thermo

epaisseurPlaque = 1.6 * 10**-3
AireTEC = 0.0156**2

T_amb = 22.6

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


### Aller chercher les dérivés et retard du prototype
dT_dt_allumageTEC = []
Q_Tec_allumage = []
i_allumage_TEC = []


for i, essai in enumerate(EssaisProto):
        # Fit a smoothing spline
    x = essai["time"]
    y = essai["T1"]
    spline = UnivariateSpline(x, y, s=3)  # s controls the smoothness
    y_smooth = spline(x)

    # Compute the first derivative
    dy_dx = spline.derivative()(x)

    # Plot results
    fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

    ax[0].plot(x, y, 'o', markersize=3, alpha=0.5, label="Noisy Data")
    ax[0].plot(x, y_smooth, linewidth=2, label="Smoothed Curve")
    ax[0].set_ylabel("y")
    ax[0].legend()

    ax[1].plot(x, dy_dx, 'r', linewidth=2, label="Derivative")
    ax[1].set_xlabel("x")
    ax[1].set_ylabel("dy/dx")
    ax[1].legend()

    i_allumage = 0
    if Amperage[i] > 0:
        dT_dt_allumageTEC.append(np.max(dy_dx[2:]))
        i_allumage = np.argmax(dy_dx[2:])

    else:
        dT_dt_allumageTEC.append(np.min(dy_dx[2:]))
        i_allumage = np.argmin(dy_dx[2:])

    if Amperage[i] < 0 :
        Q_Tec_allumage.append(-1*predict_Q(0, abs(Amperage[i]), T_amb))
        print(-1*predict_Q(0, abs(Amperage[i]), T_amb))
    else:
        Q_Tec_allumage.append(predict_Q(0, Amperage[i], T_amb))
        print(predict_Q(0, Amperage[i], T_amb))

    i_allumage_TEC.append(i_allumage)

    plt.scatter(i_allumage+1, dT_dt_allumageTEC[-1])

    plt.show()

plt.scatter(Q_Tec_allumage, dT_dt_allumageTEC)
plt.xlabel("Q prédit du TEC")
plt.ylabel("dT/dt à l'allumage")

slope, intercept, _, _, _ = linregress(Q_Tec_allumage, dT_dt_allumageTEC)
x_vals = np.linspace(min(Q_Tec_allumage), max(Q_Tec_allumage), 100)
y_vals = slope * x_vals + intercept
plt.plot(x_vals, y_vals, color='red', label=f"Fit: y = {slope:.3f}x + {intercept:.3f}")

plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.show()

cTEC_rhocp_experimental = slope * epaisseurPlaque * AireTEC

print(f'experimental : {cTEC_rhocp_experimental}, valeur reference : {1/(900*2700)}')



dT_dt_fermetureTEC = []
deltaT_conv_fermeture = []
i_fermeture_TEC = []


for i, essai in enumerate(EssaisProto):
        # Fit a smoothing spline
    x = essai["time"]
    y = essai["T3"]
    spline = UnivariateSpline(x, y, s=3)  # s controls the smoothness
    y_smooth = spline(x)

    # Compute the first derivative
    dy_dx = spline.derivative()(x)


    ax[0].plot(x, y, 'o', markersize=3, alpha=0.5, label="Noisy Data")
    ax[0].plot(x, y_smooth, linewidth=2, label="Smoothed Curve")
    ax[0].set_ylabel("y")
    ax[0].legend()

    ax[1].plot(x, dy_dx, 'r', linewidth=2, label="Derivative")
    ax[1].set_xlabel("x")
    ax[1].set_ylabel("dy/dx")
    ax[1].legend()

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
    y = essai["T2"]
    spline = UnivariateSpline(x, y, s=3)  # s controls the smoothness
    y_smooth = spline(x)

    # Compute the first derivative
    dy_dx = spline.derivative()(x)

    ax[0].plot(x, y, 'o', markersize=3, alpha=0.5, label="Noisy Data")
    ax[0].plot(x, y_smooth, linewidth=2, label="Smoothed Curve")
    ax[0].set_ylabel("y")
    ax[0].legend()

    ax[1].plot(x, dy_dx, 'r', linewidth=2, label="Derivative")
    ax[1].set_xlabel("x")
    ax[1].set_ylabel("dy/dx")
    ax[1].legend()

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

plt.scatter(deltaT_conv_fermeture, dT_dt_fermetureTEC, label="Data", color='green')

slope, intercept, _, _, _ = linregress(deltaT_conv_fermeture, dT_dt_fermetureTEC)
x_vals = np.linspace(min(deltaT_conv_fermeture), max(deltaT_conv_fermeture), 100)
y_vals = slope * x_vals + intercept
plt.plot(x_vals, y_vals, color='red', label=f"Fit: y = {slope:.3f}x + {intercept:.3f}")

plt.xlabel("Différence T fermeture - T amb")
plt.ylabel("dT/dt à la fermeture")
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.show()

h_rhocp_experimental = (slope * epaisseurPlaque) / 2

print(f'experimental : {h_rhocp_experimental}, valeur reference : {15/(900*2700)}')

k_rhocp_experimental = 120/(900*2700)

###Tunning alpha

#k_atester = [80,100,120,140,160,180,200,220,240,260,280,300]
#Plaques = []
#thermos = []
#Tecs = []

#position1 = (0.11875 - 0.014, 0.031)  
#position2 = (0.11875 - 0.0604, 0.031) 
#position3 = (0.11875 - 0.1065, 0.031) 
    # Créer des instances de thermoresistance
    
#for k in k_atester:
#    plaque = PlaqueThermique((0.11875,0.062,0.002), (k, 2700, 900), 15, (0.001,0.001), T_amb)
#    Tec = ActionneurThermique((0.096, 0.031), (0.015,0.0156), plaque.matTemperature, plaque.dimensionsElementFinie)

#    thermo1 = thermo(position=position1, diamètre=0.008, épaisseur=0.001, plaque=plaque)
#    thermo2 = thermo(position=position2, diamètre=0.008, épaisseur=0.001, plaque=plaque)
#    thermo3 = thermo(position=position3, diamètre=0.008, épaisseur=0.001, plaque=plaque)

#    Plaques.append(plaque)
#    thermos.append([thermo1, thermo2, thermo3])
#    Tecs.append(Tec)

#garder le même ratio
#totalTime = 50
#num_frames = int(580000 / 10)
#dTime = totalTime/num_frames
###Nombre de frame skippé dans l'animation
#animationStep = 1600

#echelonCourant = 0

#temperatures = [[],[],[],[],[],[],[],[],[],[],[],[]]
#time = []
#
#for i in range(num_frames):
#        ###Effectue un échelon d'opération à mi chemin
#        if i*dTime >= 5:
#            echelonCourant = 3
#
#        if i % animationStep == 0:
#            print(i)
#            for j, tec in enumerate(Tecs):
#                tec.updateMatPerturbation(echelonCourant, Plaques[j].matTemperature, T_amb)
#        else:
#            for j, plaque in enumerate(Plaques):
#                plaque.propagationDunPasDeTemps(dTime, T_amb, [Tecs[j].matPerturbation])
        
#        for j, thermistances in enumerate(thermos):
#            temperatures[j].append([thermistances[0].lire_temperature(), thermistances[1].lire_temperature(), thermistances[2].lire_temperature()])
#        time.append(i*dTime)

#plt.plot(EssaisProto[0]["time"][0:50], EssaisProto[0]["T3"][0:50])

#tempAAfficher = []


#tempAAfficher = []
#for i, temps in enumerate(temperatures):
#    tempAAfficher=[]
#    for temp in temps:
#        tempAAfficher.append(temp[2])
#    plt.plot(time, tempAAfficher, label=f'{i}')

#plt.legend()
#plt.show()


def simulationMultiples(cTec_rhocp, h_rhocp, k_rhocp, echelonsComparer):
    
    cTec_atester = [1]
    Plaques = []
    thermos = []
    Tecs = []

    position1 = (0.11875 - 0.014, 0.031)  
    position2 = (0.11875 - 0.0604, 0.031) 
    position3 = (0.11875 - 0.1065, 0.031) 
        # Créer des instances de thermoresistance
        
    for cTec in cTec_atester:
        #plaque = PlaqueThermique((0.11875,0.062,0.002), (k_rhocp * (1/(cTec_rhocp / cTec)), 1, 1/(cTec_rhocp / cTec)), h_rhocp * (1/(cTec_rhocp / cTec)), (0.001,0.001), T_amb)
        plaque = PlaqueThermique((0.11875,0.062,0.0016), (210, 900, 2700), 14.4, (0.001,0.001), T_amb)
        Tec = ActionneurThermique((0.096, 0.031), (0.015,0.0156), plaque.matTemperature, plaque.dimensionsElementFinie)

        thermo1 = thermo(position=position1, diamètre=0.008, épaisseur=0.001, plaque=plaque)
        thermo2 = thermo(position=position2, diamètre=0.008, épaisseur=0.001, plaque=plaque)
        thermo3 = thermo(position=position3, diamètre=0.008, épaisseur=0.001, plaque=plaque)

        Plaques.append(plaque)
        thermos.append([thermo1, thermo2, thermo3])
        Tecs.append(Tec)

    #garder le même ratio
    totalTime = 200
    num_frames = 290000
    dTime = totalTime/num_frames
    ##Nombre de frame skippé dans l'animation
    animationStep = 1600

    echelonCourant = 0

    temperatures = [[]]
    time = []
    
    for i in range(num_frames):
            ###Effectue un échelon d'opération à mi chemin
            if i*dTime >= 8:
                echelonCourant = 1.5
    
            if i % animationStep == 0:
                print(i)
                for j, tec in enumerate(Tecs):
                    tec.updateMatPerturbation(echelonCourant, Plaques[j].matTemperature, T_amb)
            else:
                for j, plaque in enumerate(Plaques):
                    plaque.propagationDunPasDeTemps(dTime, T_amb, [Tecs[j].matPerturbation])
            
            for j, thermistances in enumerate(thermos):
                temperatures[j].append([thermistances[0].lire_temperature(), thermistances[1].lire_temperature(), thermistances[2].lire_temperature()])
            time.append(i*dTime)

    plt.plot(EssaisProto[0]["time"][0:400], EssaisProto[2]["T3"][0:400])
    plt.plot(EssaisProto[0]["time"][0:400], EssaisProto[2]["T2"][0:400])
    plt.plot(EssaisProto[0]["time"][0:400], EssaisProto[2]["T1"][0:400])



    #tempAAfficher = []

    for i, temps in enumerate(temperatures):
        temp1AAfficher = []
        temp2AAfficher = []
        temp3AAfficher = []
        for temp in temps:
            temp1AAfficher.append(temp[0])
            temp2AAfficher.append(temp[1])
            temp3AAfficher.append(temp[2])
        plt.plot(time, temp1AAfficher, label=f'{i}')
        plt.plot(time, temp2AAfficher, label=f'{i}')
        plt.plot(time, temp3AAfficher, label=f'{i}')


    plt.legend()
    plt.show()

simulationMultiples(cTEC_rhocp_experimental*15, h_rhocp_experimental, k_rhocp_experimental, "hi")

