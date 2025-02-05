import numpy as np
import matplotlib.pyplot as plt
import _tkinter as tkr
import csv

from PlaqueThermique import PlaqueThermique
from ActuateurThermique import ActionneurThermique
from thermistance import thermo

T_amb = 24.3

PlaqueA = PlaqueThermique((0.11875,0.062,0.002), "Ajustement", 14.5, (0.001,0.001), T_amb)
TecA = ActionneurThermique((0.096, 0.031), (0.015,0.0156), PlaqueA.matTemperature, PlaqueA.dimensionsElementFinie)

# Définir les positions en mètres
position1 = (0.11875 - 0.014, 0.031)  # 14 mm et 26.5 mm
position2 = (0.11875 - 0.0604, 0.031)  # 60.4 mm et 26.5 mm
position3 = (0.11875 - 0.1065, 0.031)  # 106.5 mm et 26.5 mm

# Créer des instances de thermoresistance
thermo1 = thermo(position=position1, diamètre=0.008, épaisseur=0.001, plaque=PlaqueA)
thermo2 = thermo(position=position2, diamètre=0.008, épaisseur=0.001, plaque=PlaqueA)
thermo3 = thermo(position=position3, diamètre=0.008, épaisseur=0.001, plaque=PlaqueA)

# Ajouter à la liste des thermoresistances
Thermistances = [thermo1, thermo2, thermo3]


from matplotlib.animation import FuncAnimation
plt.ion()

###Echelon de 6A
echelonCourant = 0
TecA.updateMatPerturbation(echelonCourant,PlaqueA.matTemperature,24)
#garder le même ratio
totalTime = 800
num_frames = int(290000 / 1)
dTime = totalTime/num_frames
###Nombre de frame skippé dans l'animation
animationStep = 1600

video = []
temperatures = [[],[],[]]
time = []

for i in range(num_frames):
    ###Effectue un échelon d'opération à mi chemin
    if i * dTime >= 40:
        echelonCourant = 1

    if i % animationStep == 0:
        video.append(PlaqueA.propagationDunPasDeTemps(dTime, T_amb, [TecA.matPerturbation]))
        TecA.updateMatPerturbation(echelonCourant, PlaqueA.matTemperature, T_amb)
    else:
        PlaqueA.propagationDunPasDeTemps(dTime, T_amb, [TecA.matPerturbation])
    
    for j, thermistance in enumerate(Thermistances):
        temperatures[j].append(thermistance.lire_temperature())
    time.append(i*dTime)

temperatures = np.array(temperatures)

fig, (ax_im, ax_hist) = plt.subplots(2, 1, figsize=(8, 8))
im = ax_im.imshow(video[0], cmap='viridis', interpolation='none')

cbar = plt.colorbar(im, ax=ax_im)
cbar.set_label('Température en C')  # Label for the colorbar

max_value = np.max(video)
min_value = np.min(video)
im.set_clim(min_value, max_value)

ax_im.set_title(f"Time = 0 ms")



# Setup for the history plot
ax_hist.set_xlim(0, num_frames * dTime)  # X-axis for time
ax_hist.set_ylim(np.min(temperatures)-0.1, np.max(temperatures)+0.1)  # Y-axis for temperature
ax_hist.set_xlabel("Time (s)")
ax_hist.set_ylabel("Average Temperature (°C)")

# Define three separate line objects for the history plot
line_hist1, = ax_hist.plot([], [], color='red', label="Thermo 1")
line_hist2, = ax_hist.plot([], [], color='blue', label="Thermo 2")
line_hist3, = ax_hist.plot([], [], color='orange', label="Thermo 3")


# Initialize lists
time = []
T1 = []
T2 = []
T3 = []
T4 = []

# Read CSV file
with open("donnéesProto/data_thermistances-1A.csv", mode="r", encoding="ISO-8859-1") as file:
    reader = csv.reader(file)
    next(reader)  # Skip the first header row
    next(reader)  # Skip the duplicate header row

    for row in reader:
        time.append(int(row[0]))  # Convert time to integer
        T1.append(float(row[1]))  # Convert temperatures to float
        T2.append(float(row[2]))
        T3.append(float(row[3]))
        T4.append(float(row[4]))

line_hist4, = ax_hist.plot(time, T1, color='red', label="Thermo 1")
line_hist5, = ax_hist.plot(time, T2, color='blue', label="Thermo 2")
line_hist6, = ax_hist.plot(time, T3, color='orange', label="Thermo 3")

print(T3)


ax_hist.legend()




def update(frame):
    im.set_array(video[frame])
    ax_im.set_title(f"Time = {round(frame * animationStep * dTime, 2)} s")

    # Update the history plots for all three lines
    #time_values = np.arange(frame * animationStep + 1) * dTime
    
    line_hist1.set_data(np.arange(frame * animationStep + 1) * dTime, temperatures[0][:frame *animationStep + 1])
    line_hist2.set_data(np.arange(frame * animationStep + 1) * dTime, temperatures[1][:frame *animationStep + 1])
    line_hist3.set_data(np.arange(frame * animationStep + 1) * dTime, temperatures[2][:frame *animationStep + 1])

    
    return [im, line_hist1, line_hist2, line_hist3, line_hist4, line_hist5, line_hist6]

# Create the animation
ani = FuncAnimation(fig, update, frames=range(0, int(num_frames/animationStep)), interval=1, blit=False)

plt.show(block=True)
