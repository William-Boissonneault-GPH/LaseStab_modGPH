import numpy as np
import matplotlib.pyplot as plt
import csv
from PlaqueThermique import PlaqueThermique
from ActuateurThermique import ActionneurThermiqueSIMPLE
from thermistance import thermo
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename
import matplotlib.gridspec as gridspec  # NEW: Import gridspec

def lancer_simulation(params, progressCallback):
    """Lance la simulation thermique avec les paramètres fournis par l'interface."""
    print("🟡 Début de la simulation...")
    # Récupération des paramètres depuis l'interface
    dim_x = params["Dimension_x_plaque_(m)"]
    dim_y = params["Dimension_y_plaque_(m)"]
    dim_z = params["Dimension_z_plaque_(m)"]
    h = params["Coéfficient_convection_(W/m²K)"]
    cp = params["Capacité_thermique_(J/KgK)"]
    k = params["Conductivité_thermique_(W/mK)"]
    rho = params["Densité_(kg/m³)"]
    T_init = params["Température_initiale_(°C)"]
    #echelonCourant = params["Échelon_courant_(A)"]
    totalTime= params["Temps_simulation_(s)"]
    sources_chaleur = params["Sources_chaleur"]

    echelonCourant1 = params["Échelon_courant_1_(A)"]
    dureeEchelon1 = params["Durée_échelon_1_(s)"]
    echelonCourant2 = params["Échelon_courant_2_(A)"]
    dureeEchelon2 = params["Durée_échelon_2_(s)"]


    pos_x_thermo1 = params["Position_x_T1_(m)"]
    pos_y_thermo1 = params["Position_y_T1_(m)"]
    pos_x_thermo2 = params["Position_x_T2_(m)"]
    pos_y_thermo2 = params["Position_y_T2_(m)"]
    pos_x_thermo3 = params["Position_x_T3_(m)"]
    pos_y_thermo3 = params["Position_y_T3_(m)"]

    pos_x_TEC = params["Position_x_TEC_(m)"]
    pos_y_TEC = params["Position_y_TEC_(m)"]
    dim_x_TEC = params["Dimension_x_TEC_(m)"]
    dim_y_TEC = params["Dimension_y_TEC_(m)"]
    coeff_a= params["Coefficient_couplage_a"]  # Ajout des coefficients
    coeff_b= params["Coefficient_couplage_b"]

    # Création de la plaque thermique avec les paramètres de l'interface
    PlaqueA = PlaqueThermique((dim_x, dim_y, dim_z), (k, rho, cp), h, (0.001, 0.001), T_init)
    TecA = ActionneurThermiqueSIMPLE((pos_x_TEC, pos_y_TEC), (dim_x_TEC, dim_y_TEC), PlaqueA.matTemperature, PlaqueA.dimensionsElementFinie, coeff_a, coeff_b)

    # Création des thermorésistances avec les positions spécifiées par l'utilisateur
    thermo1 = thermo(position=(pos_x_thermo1, pos_y_thermo1), diamètre=0.008, épaisseur=0.001, plaque=PlaqueA)
    thermo2 = thermo(position=(pos_x_thermo2, pos_y_thermo2), diamètre=0.008, épaisseur=0.001, plaque=PlaqueA)
    thermo3 = thermo(position=(pos_x_thermo3, pos_y_thermo3), diamètre=0.008, épaisseur=0.001, plaque=PlaqueA)

    Thermistances = [thermo1, thermo2, thermo3]

    ### Simulation

    #Pour actuateur complexe
    #TecA.updateMatQTEC(echelonCourant, PlaqueA.matTemperature, T_init)

    #Pour actuateur SIMPLE
    TecA.updateMatQTECCourrant(echelonCourant1)

    totalTime = totalTime
    dTime = 1/363

    num_frames = int(totalTime * (1/dTime))
    ##Animation steps détermine la mémoire utilisé dans l'ordi!
    #animationStep = 1600
    animationStep = 1600
    plotRes = 10
    
    video = []
    temperatures = [[], [], []]
    plottingTemp = [[],[],[]]
    plottingtemp = []
    time = []

    # Génération de la matrice de puissance thermique
    mat_perturb = PlaqueA.generer_mat_pertub(sources_chaleur)

    for i in range(num_frames):
        # if i == num_frames / 2:
        #     #Effectue la fermeture à mi-chemin
        #     echelonCourant = 0

        current_time = i * dTime

        # Gestion de l'échelon de courant
        if current_time <= dureeEchelon1:
            TecA.updateMatQTECCourrant(echelonCourant1)

        elif dureeEchelon1 < current_time <= (dureeEchelon1 + dureeEchelon2):
            TecA.updateMatQTECCourrant(echelonCourant2)

        else:
            TecA.updateMatQTECCourrant(0)
        
        if i % (animationStep/plotRes) == 0:
            if i % animationStep == 0:
                print(f"La simulation est rendu à {round((i / num_frames)*100, 2)} %")
                progressCallback(round((i / num_frames)*100, 2))
                video.append(PlaqueA.propagationDunPasDeTemps(dTime, T_init, [TecA.matQTEC, mat_perturb]))

                #Pour actuateur complex
                #TecA.updateMatQTEC(echelonCourant, PlaqueA.matTemperature, T_init)

                #Pour actuateur SIMPLE
                TecA.updateMatQTECCourrant(echelonCourant1)

                #mat_perturb = PlaqueA.generer_mat_pertub(sources_chaleur)
            
            for j, thermistance in enumerate(Thermistances):
                plottingTemp[j].append(thermistance.lire_temperature())
            plottingtemp.append(i * dTime)
        else:
            PlaqueA.propagationDunPasDeTemps(dTime, T_init, [TecA.matQTEC, mat_perturb])
        #if i % animationStep == 0:
            #video.append(PlaqueA.propagationDunPasDeTemps(dTime, T_init, [TecA.matPerturbation]))
            #TecA.updateMatPerturbation(echelonCourant, PlaqueA.matTemperature, T_init)
        #else:
            #PlaqueA.propagationDunPasDeTemps(dTime, T_init, [TecA.matPerturbation])
        
        for j, thermistance in enumerate(Thermistances):
            temperatures[j].append(thermistance.lire_temperature())
        time.append(i * dTime)

    temperatures = np.array(temperatures)

    ### Animation
    gs = gridspec.GridSpec(3, 1, height_ratios=[4, 4, 1])
    plt.style.use("dark_background")

    plt.rcParams.update({
        "figure.facecolor": "#333333",
        "axes.facecolor": "#333333",
    })


    fig = plt.figure(figsize=(8, 8))
    ax_im = fig.add_subplot(gs[0])
    ax_hist = fig.add_subplot(gs[1])
    ax_savebutton = fig.add_subplot(gs[2])
    ax_savebutton.axis("off")

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

    ax_savebutton = plt.axes([0.4, 0.05, 0.3, 0.05])  # [x, y, width, height]
    savebutton = Button(ax_savebutton, 'Enregistrer les résultats', color='dodgerblue', hovercolor='0.5')

    def save_data(event):
        root = Tk()
        root.withdraw()
        
        file_path = asksaveasfilename(defaultextension=".csv", 
                                    filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")],
                                    title="Save as")
        
        if file_path:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["time(s)", "tempTec", "tempMilieu", "tempLaser"])
                writer.writerows(zip(time, temperatures[0], temperatures[1], temperatures[2]))
            print(f"CSV file saved successfully at {file_path}!")

    savebutton.on_clicked(save_data)


    plt.tight_layout()
    plt.show(block=True)

    ### Sauvegarde des données en CSV
    #rows = zip(time, temperatures[0], temperatures[1], temperatures[2])
    #with open("output.csv", "w", newline="") as file:
    #    writer = csv.writer(file)
    #    writer.writerow(["time(s)", "tempTec", "tempMilieu", "tempLaser"])
    #    writer.writerows(rows)

    #print("CSV file saved successfully!")

