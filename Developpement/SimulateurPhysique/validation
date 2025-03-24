import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.interpolate import UnivariateSpline
from scipy.stats import linregress
from matplotlib.animation import FuncAnimation

from PlaqueThermique import PlaqueThermique
from ActuateurThermique import ActionneurThermique
from ActuateurThermique import ActionneurThermiqueSIMPLE

from ActuateurThermique import predict_Q
from thermistance import thermo

from scipy.interpolate import interp1d



fichierAComparer = r'C:\Users\willi\OneDrive - Université Laval\Cours\HIV2025\ModelisationGPH\LaseStab_modGPH\Developpement\SimulateurPhysique\comparaisonValidation\donneesProto\mesures_-1_5A.csv'
regimeString="legen"
indiceDeDepartFicher = 11

T_ambiante = 22.5

tempRegime1 = 12- indiceDeDepartFicher
courantRegime1 = -1.5

tempRegime2 = 1
courantRegime2 = 0



###############Modele##########################

position1 = (0.11875 - 0.014, 0.031)  
position2 = (0.11875 - 0.0604, 0.031) 
position3 = (0.11875 - 0.1065, 0.031) 
# Créer des instances de thermoresistance
    
plaque = PlaqueThermique((0.11875,0.062,0.0016), (180, 900, 2700), 14, (0.001,0.001), T_ambiante)
Tec = ActionneurThermiqueSIMPLE((0.096, 0.031), (0.015,0.0156), plaque.matTemperature, plaque.dimensionsElementFinie)

thermo1 = thermo(position=position1, diamètre=0.008, épaisseur=0.001, plaque=plaque)
thermo2 = thermo(position=position2, diamètre=0.008, épaisseur=0.001, plaque=plaque)
thermo3 = thermo(position=position3, diamètre=0.008, épaisseur=0.001, plaque=plaque)

Thermistances=[thermo1, thermo2, thermo3]


###############SIMULATION######################

#Pour actuateur SIMPLE
Tec.updateMatQTECCourrant(courantRegime1)
totalTime = tempRegime1 + tempRegime2
dTime = 1/363

num_frames = int(totalTime * (1/dTime))
animationStep = 1600
plotRes = 10

video = []
temperatures = [[], [], []]
plottingTemp = [[],[],[]]
plottingtemp = []
time = []

# Génération de la matrice de puissance thermique
#mat_perturb = plaque.generer_mat_pertub(sources_chaleur)

echelonCourant = courantRegime1

for i in range(num_frames):

    if i * dTime > tempRegime1:
        #Effectue la fermeture à mi-chemin
        echelonCourant = courantRegime2
    
    if i % (animationStep/plotRes) == 0:
        if i % animationStep == 0:
            print(f"La simulation est rendu à {round((i / num_frames)*100, 2)} %")
            #progressCallback(round((i / num_frames)*100, 2))
            video.append(plaque.propagationDunPasDeTemps(dTime, T_ambiante, [Tec.matQTEC]))
            Tec.updateMatQTECCourrant(echelonCourant)

        for j, thermistance in enumerate(Thermistances):
            plottingTemp[j].append(thermistance.lire_temperature())
        plottingtemp.append(i * dTime)

        #mat_perturb = PlaqueA.generer_mat_pertub(sources_chaleur)
    else:
        plaque.propagationDunPasDeTemps(dTime, T_ambiante, [Tec.matQTEC])
    
    for j, thermistance in enumerate(Thermistances):
        temperatures[j].append(thermistance.lire_temperature())
    time.append(i * dTime)

temperatures = np.array(temperatures)

### Animation
fig, (ax_im, ax_hist) = plt.subplots(2, 1, figsize=(8, 8))
im = ax_im.imshow(video[0], cmap='viridis', interpolation='none')
cbar = plt.colorbar(im, ax=ax_im)
cbar.set_label('Température en C')

max_value = np.max(video)
min_value = np.min(video)
im.set_clim(min_value, max_value)

ax_im.set_title(f"Time = 0 ms")

ax_hist.set_xlim(0, num_frames * dTime)
ax_hist.set_ylim(np.min(temperatures) - 0.1, np.max(temperatures) + 0.1)
ax_hist.set_xlabel("Time (s)")
ax_hist.set_ylabel("Average Temperature (°C)")

line_hist1, = ax_hist.plot([], [], color='red', label="Thermo 1")
line_hist2, = ax_hist.plot([], [], color='blue', label="Thermo 2")
line_hist3, = ax_hist.plot([], [], color='orange', label="Thermo 3")
ax_hist.legend()

def update(frame):
    im.set_array(video[frame])
    ax_im.set_title(f"Time = {round(frame * animationStep * dTime, 2)} s")

    line_hist1.set_data(plottingtemp[:frame * plotRes + 1], plottingTemp[0][:frame * plotRes + 1])
    line_hist2.set_data(plottingtemp[:frame * plotRes + 1], plottingTemp[1][:frame * plotRes + 1])
    line_hist3.set_data(plottingtemp[:frame * plotRes + 1], plottingTemp[2][:frame * plotRes + 1])

    return [im, line_hist1, line_hist2, line_hist3]

ani = FuncAnimation(fig, update, frames=range(0, int(num_frames / animationStep)), interval=1, blit=False)

plt.show(block=True)





###############COMPARAISON####################

proto_time=[]
T1=[]
T2=[]
T3=[]
with open(fichierAComparer, mode="r", encoding="ISO-8859-1") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the first header row
    next(reader)  # Skip the duplicate header row
    
    for row in reader:
        proto_time.append(int(row[0]))  # Convert time to integer
        T1.append(float(row[1]))  # Convert temperatures to float
        T2.append(float(row[2]))
        T3.append(float(row[3]))
proto_time = np.array(proto_time)
proto_time = proto_time - proto_time[indiceDeDepartFicher]

T1 = np.array(T1)
T2 = np.array(T2)
T3 = np.array(T3)
EssaisProto = {
    "time" : proto_time,
    "T1" : T1,
    "T2" : T2,
    "T3" : T3
}

plt.figure(figsize=(5,3))

colors = ['#DC143C', '#B22222', '#FF6347']
line_styles = ['-', '--', ':']

plt.plot(EssaisProto["time"][0::10], EssaisProto["T3"][0::10], color=colors[2], linestyle=line_styles[2], label='T3 mesurée')
plt.plot(EssaisProto["time"][0::10], EssaisProto["T2"][0::10], color=colors[1], linestyle=line_styles[1], label='T2 mesurée')
plt.plot(EssaisProto["time"][0::10], EssaisProto["T1"][0::10], color=colors[0], linestyle=line_styles[0], label='T1 mesurée')

plt.plot(time, temperatures[0], color='k', alpha=0.5, label='T simulée')
plt.plot(time, temperatures[1], color='k', alpha=0.5)
plt.plot(time, temperatures[2], color='k', alpha=0.5)

plt.xlabel("temps [s]")
plt.ylabel("Température [C]")

################CALCULS ACCORD######################
def round_to_sigfig(x, sigfigs=1):
    if x == 0:
        return 0
    return round(x, -int(np.floor(np.log10(abs(x)))) + (sigfigs - 1))

def round_uncertainty(value, uncertainty):
    # Round value to 1 significant figure
    rounded_uncertainty = round_to_sigfig(uncertainty, 1)
    
    # Find the decimal place based on the rounded value
    decimal_places = -int(np.floor(np.log10(abs(rounded_uncertainty)))) + (len(str(rounded_uncertainty).split('.')[1]) if '.' in str(rounded_uncertainty) else 0)
    
    # Round uncertainty to the same decimal places
    rounded_value = round(value, decimal_places - 1)
    
    return rounded_value, rounded_uncertainty


for i in range(3):
    interp_func = interp1d(proto_time, EssaisProto[f"T{i+1}"][0:], kind='linear', fill_value='extrapolate')
    values2_interp = interp_func(time) 

    percent_error = np.abs((temperatures[i]- values2_interp) / values2_interp) * 100

    accord, incert = round_uncertainty(np.mean(percent_error), 2*np.std(percent_error))
    print(f"TermoRes {int(i+1)} : {accord} pm {incert}")
    print(f"TermoRes {int(i+1)} : {np.mean(percent_error)} pm {2*np.std(percent_error)}")

    plt.plot([],[],' ',label=f"Accord T{i+1}: {accord}±{incert} %")

plt.legend()
plt.xlim((0,tempRegime1+tempRegime2))
plt.ylim((10,25))
plt.tight_layout()
plt.savefig(f'Developpement/SimulateurPhysique/comparaisonValidation/{regimeString}.pdf')
plt.show()




### Sauvegarde des données en CSV
rows = zip(time, temperatures[0], temperatures[1], temperatures[2])
with open("output.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["time(s)", "tempTec", "tempMilieu", "tempLaser"])
    writer.writerows(rows)

print("CSV file saved successfully!")