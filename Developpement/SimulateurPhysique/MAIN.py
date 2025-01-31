import numpy as np
import matplotlib.pyplot as plt
import _tkinter as tkr

from PlaqueThermique import PlaqueThermique
from ActuateurThermique import ActionneurThermique
from thermistance import thermo

PlaqueA = PlaqueThermique((0.11875,0.062,0.002), "Aluminium", 60, (0.001,0.001), 25)
TecA = ActionneurThermique((0.096, 0.031), (0.015,0.0156), PlaqueA.matTemperature, PlaqueA.dimensionsElementFinie)

thermo1 = thermo(position=(0.03, 0.02), diamètre=0.005, épaisseur=0.001, plaque=PlaqueA)
thermo2 = thermo(position=(0.07, 0.04), diamètre=0.005, épaisseur=0.001, plaque=PlaqueA)
thermo3 = thermo(position=(0.10, 0.06), diamètre=0.005, épaisseur=0.001, plaque=PlaqueA)
Thermistances = [thermo1,thermo2,thermo3]


from matplotlib.animation import FuncAnimation
plt.ion()

###Echelon de 6A
echelonCourant = 3
TecA.updateMatPerturbation(echelonCourant,PlaqueA.matTemperature,25)

T_amb = 25

#garder le même ratio
totalTime = 600
num_frames = 240000
dTime = totalTime/num_frames
###Nombre de frame skippé dans l'animation
animationStep = 400

video = []
temperatures = [[],[],[]]

for i in range(num_frames):

    ###Effectue un échelon d'opération à mi chemin
    if i == num_frames/2:
        echelonCourant = 6

    if i % animationStep == 0:
        video.append(PlaqueA.propagationDunPasDeTemps(dTime, T_amb, [TecA.matPerturbation]))
        TecA.updateMatPerturbation(echelonCourant, PlaqueA.matTemperature, T_amb)
    else:
        PlaqueA.propagationDunPasDeTemps(dTime, T_amb, [TecA.matPerturbation])
    
    for j, thermistance in enumerate(Thermistances):
        temperatures[j].append(thermistance.lire_temperature())

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
ax_hist.legend()

def update(frame):
    im.set_array(video[frame])
    ax_im.set_title(f"Time = {round(frame * animationStep * dTime, 2)} s")

    # Update the history plots for all three lines
    #time_values = np.arange(frame * animationStep + 1) * dTime
    
    line_hist1.set_data(np.arange(frame * animationStep + 1) * dTime, temperatures[0][:frame *animationStep + 1])
    line_hist2.set_data(np.arange(frame * animationStep + 1) * dTime, temperatures[1][:frame *animationStep + 1])
    line_hist3.set_data(np.arange(frame * animationStep + 1) * dTime, temperatures[2][:frame *animationStep + 1])
    
    # Adjust x-axis limits dynamically
    #ax_hist.set_xlim(0, max((frame + 1) * dTime, num_frames * dTime))
    
    # Optionally adjust y-axis limits dynamically
    #ax_hist.set_ylim(min(min(thermo1_temps), min(thermo2_temps), min(thermo3_temps)),
    #                 max(max(thermo1_temps), max(thermo2_temps), max(thermo3_temps)))
    
    return [im, line_hist1, line_hist2, line_hist3]

# Create the animation
ani = FuncAnimation(fig, update, frames=range(0, int(num_frames/animationStep)), interval=1, blit=False)

plt.show(block=True)
