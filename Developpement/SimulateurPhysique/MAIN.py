import numpy as np
import matplotlib.pyplot as plt
import csv
from PlaqueThermique import PlaqueThermique
from ActuateurThermique import ActionneurThermique
from thermistance import thermo
from matplotlib.animation import FuncAnimation

def lancer_simulation(params):
    """Lance la simulation thermique avec les paramètres fournis par l'interface."""
    
    # Récupération des paramètres depuis l'interface
    dim_x = params["dim_x_plaque"]
    dim_y = params["dim_y_plaque"]
    dim_z = params["dim_z_plaque"]
    h = params["coefficient_convection"]
    cp = params["capacite_thermique"]
    k = params["conductivite_thermique"]
    T_init = params["temperature_initiale"]

    pos_x_thermo1 = params["pos_x_thermo1"]
    pos_y_thermo1 = params["pos_y_thermo1"]
    pos_x_thermo2 = params["pos_x_thermo2"]
    pos_y_thermo2 = params["pos_y_thermo2"]
    pos_x_thermo3 = params["pos_x_thermo3"]
    pos_y_thermo3 = params["pos_y_thermo3"]

    # Création de la plaque thermique avec les paramètres de l'interface
    PlaqueA = PlaqueThermique((dim_x, dim_y, dim_z), "Aluminium", h, (0.001, 0.001), T_init)
    TecA = ActionneurThermique((0.096, 0.031), (0.015, 0.0156), PlaqueA.matTemperature, PlaqueA.dimensionsElementFinie)

    # Création des thermorésistances avec les positions spécifiées par l'utilisateur
    thermo1 = thermo(position=(pos_x_thermo1, pos_y_thermo1), diamètre=0.008, épaisseur=0.001, plaque=PlaqueA)
    thermo2 = thermo(position=(pos_x_thermo2, pos_y_thermo2), diamètre=0.008, épaisseur=0.001, plaque=PlaqueA)
    thermo3 = thermo(position=(pos_x_thermo3, pos_y_thermo3), diamètre=0.008, épaisseur=0.001, plaque=PlaqueA)

    Thermistances = [thermo1, thermo2, thermo3]

    ### Simulation
    echelonCourant = -0.7
    TecA.updateMatPerturbation(echelonCourant, PlaqueA.matTemperature, T_init)

    totalTime = 1600
    num_frames = 580000
    dTime = totalTime / num_frames
    animationStep = 1600

    video = []
    temperatures = [[], [], []]
    time = []

    for i in range(num_frames):
        if i == num_frames / 2:
            echelonCourant = -0.7

        if i % animationStep == 0:
            video.append(PlaqueA.propagationDunPasDeTemps(dTime, T_init, [TecA.matPerturbation]))
            TecA.updateMatPerturbation(echelonCourant, PlaqueA.matTemperature, T_init)
        else:
            PlaqueA.propagationDunPasDeTemps(dTime, T_init, [TecA.matPerturbation])
        
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

        line_hist1.set_data(np.arange(frame * animationStep + 1) * dTime, temperatures[0][:frame * animationStep + 1])
        line_hist2.set_data(np.arange(frame * animationStep + 1) * dTime, temperatures[1][:frame * animationStep + 1])
        line_hist3.set_data(np.arange(frame * animationStep + 1) * dTime, temperatures[2][:frame * animationStep + 1])

        return [im, line_hist1, line_hist2, line_hist3]

    ani = FuncAnimation(fig, update, frames=range(0, int(num_frames / animationStep)), interval=1, blit=False)

    plt.show()

    ### Sauvegarde des données en CSV
    rows = zip(time, temperatures[0], temperatures[1], temperatures[2])
    with open("output.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["time(s)", "tempTec", "tempMilieu", "tempLaser"])
        writer.writerows(rows)

    print("CSV file saved successfully!")
