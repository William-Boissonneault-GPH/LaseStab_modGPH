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
from tkinter import messagebox
import time 

def lancer_simulation(params, progressCallback):
    """Lance la simulation thermique avec les paramètres fournis par l'interface."""
    print("🟡 Début de la simulation...")
    # Récupération des paramètres depuis l'interface
    dim_x = params["Dimension_x_plaque_(m)"]
    dim_y = params["Dimension_y_plaque_(m)"]
    dim_z = params["Dimension_z_plaque_(m)"]

    dim_dx = params['Largeur_élement_fini_dx_(m)']
    dim_dy = params['Largeur_élement_fini_dy_(m)']

    h = params["Coéfficient_convection_(W/m²K)"]
    cp = params["Capacité_thermique_(J/KgK)"]
    k = params["Conductivité_thermique_(W/mK)"]
    rho = params["Densité_(kg/m³)"]
    T_init = params["Température_initiale_(°C)"]
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
    coeff_a= params["Coefficient_couplage_a"]  
    coeff_b= params["Coefficient_couplage_b"]

    # Création de la plaque thermique avec les paramètres de l'interface
    PlaqueA = PlaqueThermique((dim_x, dim_y, dim_z), (k, rho, cp), h, (dim_dx, dim_dy), T_init)
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
    #Choix dT en 2D
    dTime = 0.4 * (rho * cp / k) * ((1/dim_dx)**2+(1/dim_dy)**2)**-1

    num_frames = int(totalTime * (1/dTime))
    ##Animation steps détermine le nombre de frame video
    #PlotRes est la resolution conserve pour graphique et csv
    animationStep = int(num_frames / 200)
    plotRes = max(1, int(num_frames / 30000))

    print(f"Animation step: {animationStep}")
    print(f"Plotting resolution: {plotRes}")    
    print(f"Num frames: {num_frames}")
    print(f"dtime: {dTime}")

    if animationStep == 0:
        animationStep = 1
    if plotRes == 0:
        plotRes = 1

    video = []
    temperatures = [[], [], []]
    plottingTemp = [[],[],[]]
    plottingtemp = []
    time1 = []
    currentCourant = 0
    currentPerturbation = 0
    plottingCourant = []
    plottingPerturbation = []



    temps_attente = params["Temps_avant_d'appliquer_la_perturbation_(s)"]
    perturbation_appliquee = False  # Assure qu'on applique la perturbation une seule fois
    
    mat_perturb = PlaqueA.generer_mat_pertub(sources_chaleur)

    for i in range(num_frames):
        current_time = i * dTime

        # Gestion de l'échelon de courant
        if current_time <= dureeEchelon1:
            TecA.updateMatQTECCourrant(echelonCourant1)
            currentCourant = echelonCourant1
        elif dureeEchelon1 < current_time <= (dureeEchelon1 + dureeEchelon2):
            TecA.updateMatQTECCourrant(echelonCourant2)
            currentCourant = echelonCourant2
        else:
            TecA.updateMatQTECCourrant(0)

        # Appliquer la perturbation seulement après le temps spécifié
        if current_time >= temps_attente and not perturbation_appliquee:
            mat_perturb = PlaqueA.generer_mat_pertub(sources_chaleur)  # Générer la perturbation
            perturbation_appliquee = True  # Empêcher de l'appliquer plusieurs fois
            currentPerturbation = sources_chaleur[0]["puissance"] 

        # Si on est avant le temps d'attente, pas de perturbation appliquée
        if current_time < temps_attente:
            sources_chaleur_actuelles = np.zeros_like(mat_perturb)  # Matrice nulle si la perturbation ne doit pas encore être appliquée
            currentPerturbation = 0

        else:
            sources_chaleur_actuelles = mat_perturb

        if i % animationStep == 0:
            #print(f"La simulation est rendue à {round((i / num_frames) * 100, 2)} %")
            progressCallback(round((i / num_frames) * 100, 2))
            video.append(PlaqueA.propagationDunPasDeTemps(dTime, T_init, [TecA.matQTEC, sources_chaleur_actuelles]))
        else:
            PlaqueA.propagationDunPasDeTemps(dTime, T_init, [TecA.matQTEC, sources_chaleur_actuelles])
        
        if i % plotRes == 0:
            for j, thermistance in enumerate(Thermistances):
                plottingTemp[j].append(thermistance.lire_temperature())
            plottingtemp.append(i * dTime)
            plottingCourant.append(currentCourant)
            plottingPerturbation.append(currentPerturbation)

        for j, thermistance in enumerate(Thermistances):
            temperatures[j].append(thermistance.lire_temperature())
        time1.append(i * dTime)

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



    ###Affichage des bonnes dimensions (en mm) sur le graphique
    height, width = video[0].shape
    x0, x1 = 0, width * PlaqueA.dimensionsElementFinie["dX"] * 1000
    y0, y1 = height * PlaqueA.dimensionsElementFinie["dY"] * 1000, 0

    im = ax_im.imshow(video[0], cmap='viridis', interpolation='none', extent=[x0, x1, y0, y1])
    cbar = plt.colorbar(im, ax=ax_im)
    cbar.set_label('Température en °C')
    ax_im.set_xlabel('Position en X (mm)') 
    ax_im.set_ylabel('Position en Y (mm)') 

    max_value = np.max(video)
    min_value = np.min(video)
    im.set_clim(min_value, max_value)

    ax_im.set_title(f"Temps = 0 ms")
    

    ax_hist.set_xlim(0, num_frames * dTime)
    ax_hist.set_ylim(np.min(temperatures) - 0.1, np.max(temperatures) + 0.1)
    ax_hist.set_xlabel("Temps (s)")
    ax_hist.set_ylabel("Température moyenne (°C)")

    line_hist1, = ax_hist.plot([], [], color='red', label="T1")
    line_hist2, = ax_hist.plot([], [], color='blue', label="T2")
    line_hist3, = ax_hist.plot([], [], color='orange', label="T3")
    ax_hist.legend()

    def update(frame):
        im.set_array(video[frame])
        ax_im.set_title(f"Temps = {int(frame * animationStep * dTime)} (s)")

        dataPerFrame = int(animationStep / plotRes)
        line_hist1.set_data(plottingtemp[:frame * dataPerFrame + 1], plottingTemp[0][:frame * dataPerFrame + 1])
        line_hist2.set_data(plottingtemp[:frame * dataPerFrame + 1], plottingTemp[1][:frame * dataPerFrame + 1])
        line_hist3.set_data(plottingtemp[:frame * dataPerFrame + 1], plottingTemp[2][:frame * dataPerFrame + 1])

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
                writer.writerow(["temps(s)", "T1", "T2", "T3", "Courant (A)", "Perturbation (W thermique)"])
                writer.writerows(zip(plottingtemp, plottingTemp[0], plottingTemp[1], plottingTemp[2], plottingCourant, plottingPerturbation))
            messagebox.showinfo(f"Fichier CSV enregistré avec succès : {file_path}!")

    savebutton.on_clicked(save_data)


    plt.tight_layout()
    plt.show(block=True)

