import serial
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import time
import numpy as np
import json
import os

csv_writer = None
csv_file = None
SAVE_FILE = "config_sauvegarde.json"

# Define serial port and parameters
SERIAL_PORT = 'COM13'  # Update this with your Arduino's serial port
BAUD_RATE = 9600
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Create a Tkinter window
root = tk.Tk()
root.title("Arduino Data Logger")
root.geometry("1300x1600+10+10") #positionne Thinker en haut a gauche


# Création du Notebook pour les pages
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)


# Modifier le style des onglets
style = ttk.Style()
style.theme_use("clam")  # Thème compatible avec la personnalisation des couleurs
style.theme_use("clam")  # Appliquer un thème compatible

# Changer la couleur de fond de la barre d'onglets
style.configure("TNotebook", background="#D3D3D3")  # Gris clair

# Changer la couleur des onglets (non sélectionnés)
style.configure("TNotebook.Tab",
                background="#393E46",   # Couleur de fond des onglets
                foreground="white",      # Texte en blanc
                font=("Times New Roman", 22, "bold"),  # Augmenter la taille du texte
                padding=[20, 10])

# Modifier la couleur de l’onglet sélectionné
style.map("TNotebook.Tab",
          background=[("selected", "#007BFF")],  # Bleu clair pour l'onglet actif
          foreground=[("selected", "white")])   # Texte en blanc quand sélectionné
# Création des deux pages
page_temperature = tk.Frame(notebook)
page_regulateur = tk.Frame(notebook)
page_principale = tk.Frame(notebook)
page_aide = tk.Frame(notebook)

notebook.add(page_principale, text="Enregistrer")
notebook.add(page_temperature, text="Température")
notebook.add(page_regulateur, text="Régulateur")
notebook.add(page_aide, text="Aide")

# 📌 Création du cadre pour la LED de stabilité sur la barre d'onglets
stability_frame = tk.Frame(notebook, bg="#393E46", padx=10, pady=2)  # Fond gris foncé pour s'aligner
stability_frame.place(relx=1.0, rely=0, anchor="ne")  # Position fixe à droite

# 📌 Label de texte "Stabilité atteinte"
stability_label = tk.Label(stability_frame, text="Stabilité atteinte ", font=("Times New Roman", 22, "bold"), fg="white",bg="#393E46")
stability_label.pack(side="left", padx=5)

# Création d'un "cercle LED" avec Canvas
led_canvas = tk.Canvas(stability_frame, width=30, height=30, highlightthickness=0, bg="#393E46")
led_canvas.pack(side="right")

# Cercle LED rouge par défaut
led_indicator = led_canvas.create_oval(5, 5, 25, 25, fill="red", outline="")

# Create variables to hold the data
time_data, temp1_data, temp2_data, temp3_data, temp4_data, setpoint_data= [], [], [], [], [], []

# Noms des valeurs REG et leurs indices
reg_labels = [
    "Coéfficient numérateur dégré 2", "Coéfficient numérateur dégré 1", "Coéfficient numérateur dégré 0", 
    "Coéfficient dénominateur dégré 2", "Coéfficient dénominateur dégré 1", "Coéfficient dénominateur dégré 0"
]

# Valeurs par défaut de REG (initialisées avec les valeurs Arduino)
default_REG_values = [1.0, -1.8995, 0.901, 1.0, -1.913, 0.913]
entries = {}

#enregistrer le temps de première stabilité
stability_reached_time = None
stability_candidate_time = None  # Moment où la stabilité a été détectée
stability_logged = False

lastError = 999
lastCommand = 999
lastSetpoint = 999

# Create a plot for real-time data
plt.rcParams["legend.fontsize"] = 12 # Forcer la taille de la légende globalement
fig, ax = plt.subplots(figsize=(15,10), dpi=100)
line_temp1, = ax.plot([], [], label='Température Thermistance 1', marker='o', linestyle='-', markersize=6)
line_temp2, = ax.plot([], [], label='Température Thermistance 2', marker='s', linestyle='-', markersize=6)
line_temp3, = ax.plot([], [], label='Température estimée T3', marker='^', linestyle='-', markersize=6)
line_temp4, = ax.plot([], [], label='Température mesurée T3', marker='D', linestyle='-', markersize=6)
line_setpoint, = ax.plot([], [], label='Consigne', marker='x', linestyle='--', color='black')



ax.set_xlim(0, 100)  # Time window for the plot (can be adjusted)
ax.set_ylim(12,38)  # Data range from analogRead() (0 to 1023 for most Arduino boards)
ax.set_xlabel("Temps (s)", fontsize=16, fontweight='bold')  # Titre de l'axe X
ax.set_ylabel("Température (°C)", fontsize=16, fontweight='bold')  # Titre de l'axe Y
ax.tick_params(axis='both', labelsize=14)  # Change la taille des étiquettes des axes
ax.legend()
ax.set_title("Évolution de la Température des Thermistances", fontsize=18, fontweight='bold')
plt.get_current_fig_manager().window.geometry("+1350+10")

# Function to update the plot and log data
def update_data(frame):
    global time_data, temp1_data, temp2_data, temp3_data, temp4_data, setpoint_data
    global lastError, lastCommand, lastSetpoint, setpoint_float
    # Read data from Arduino
    
    if arduino.in_waiting > 0:
        data = arduino.readline().decode('utf-8').strip()
        #if not "," in data:  # Filtre les lignes non numériques (comme les confirmations)
            #print(f"📩 Message Arduino : {data}")


        if data.count(',') == 7:
            try:
                time_str, temp1, temp2, temp3, temp4, lastError, lastCommand, lastSetpoint = data.split(',')
                current_time = time.time() - start_time  # Calculate elapsed time
                time_data.append(current_time)
                temp1_data.append(float(temp1))
                temp2_data.append(float(temp2))
                temp3_data.append(float(temp3))
                temp4_data.append(float(temp4))
                setpoint_data.append(float(lastSetpoint))
                # Log data to CSV
                if csv_writer:
                    csv_writer.writerow([current_time, temp1, temp2, temp3, temp4, lastError, lastCommand, lastSetpoint,
                                          stability_reached_time if stability_logged else ""])
                
                # Keep data within the plot window limit
                if len(time_data) > 400:
                    time_data = time_data[1:]
                    temp1_data = temp1_data[1:]
                    temp2_data = temp2_data[1:]
                    temp3_data = temp3_data[1:]
                    temp4_data = temp4_data[1:]
                    setpoint_data = setpoint_data[1:]

                

            except ValueError:
                raise  # Ignore invalid data
        else:
            return
        
    # Ensure that offsets is a 2D array: we create a list of (time, temp) pairs
    line_temp1.set_data(time_data, temp1_data)
    line_temp2.set_data(time_data, temp2_data)
    line_temp3.set_data(time_data, temp3_data)
    line_temp4.set_data(time_data, temp4_data)
    line_setpoint.set_data(time_data, setpoint_data)

    if frame%10 == 0 and len(time_data) > 0:
        ax.set_xlim(max(time_data)-90, max(time_data)+10)  # Time axis dynamically adjusts
        #ax.set_ylim(min(min(temp1_data), min(temp2_data), min(temp3_data), min(temp4_data)),
        #        max(max(temp1_data), max(temp2_data), max(temp3_data), max(temp4_data)))
    
     # Vérifier la stabilité à chaque mise à jour des données
    check_stability()
    return line_temp1, line_temp2, line_temp3, line_temp4, line_setpoint

is_stable = False  # Indicateur de stabilité (False au départ)

def check_stability():
    global is_stable  # Permet d'accéder à la variable globale

    """Vérifie si la température Temp3 est stable sur les 20 dernières secondes."""
    if len(time_data) < 20:
        return  # Pas assez de données pour évaluer la stabilité

    # Prendre les 20 dernières secondes de Temp3
    recent_times = np.array(time_data[-20:])
    recent_temps = np.array(temp3_data[-20:])

    # Calcul de la standard deviation (écart-type)
    std_dev = np.std(recent_temps)

    # Ajustement linéaire (pente de la régression linéaire)
    if len(recent_times) > 1:
        slope, _ = np.polyfit(recent_times, recent_temps, 1)  # Ajustement linéaire
    else:
        slope = float("inf")  # Évite la division par zéro

    #print(f"Écart-type: {std_dev:.4f}, Pente: {slope:.4f}")  # 🔍 Debugging console

    # Condition de stabilité : faible variation et faible pente
    is_stable = std_dev < 0.1 and (abs(slope) < 0.005 and abs(slope) > -0.002) and abs(float(np.average(recent_temps)) - float(lastSetpoint)) < 0.4

    # Mise à jour de la LED
    update_stability_led(is_stable)


# Fonction pour mettre à jour la LED en fonction de la stabilité
def update_stability_led(is_stable):
    global stability_candidate_time, stability_reached_time, stability_logged

    color = "green" if is_stable else "red"
    led_canvas.itemconfig(led_indicator, fill=color)

    current_time = time_data[-1] if time_data else 0

    if is_stable:
        if stability_candidate_time is None:
            stability_candidate_time = current_time  # Début de stabilité
        elif (current_time - stability_candidate_time) >= 5 and not stability_logged:
            stability_reached_time = current_time
            stability_logged = True
            print(f"✅ Stabilité confirmée à {stability_reached_time:.2f} secondes")
    else:
        stability_candidate_time = None
        stability_logged = False  # Réinitialiser si instable à nouveau

setpoint_float = None
# Function to send a setpoint to Arduino
def send_setpoint():
    global setpoint_float
    setpoint = setpoint_entry.get().strip()
    try:
        setpoint_float= float(setpoint)
        arduino.write(f"SETPOINT:{setpoint_float}\n".encode())  # Send command to Arduino
        messagebox.showinfo("Succès", f"Température envoyé : {setpoint_float}")
    except ValueError :
        messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique valide.")

# Function to send a regulator gain to Arduino
def send_Gainreg():
    Gainreg = Gainreg_entry.get().strip()  # Récupérer la valeur entrée et supprimer les espaces inutiles
    try:
        Gainreg_float = float(Gainreg)  # Convertir en float
        #print(Gainreg_float)
        arduino.write(f"GAINREG:{Gainreg_float}\n".encode())  # Envoyer la valeur en Serial
        messagebox.showinfo("Succès", f"Gain régulateur envoyé : {Gainreg_float}")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique valide.")

 #reset le gain du regulateur  
def reset_Gainreg():
    """Réinitialise le GainREG à sa valeur par défaut (0.4) et l'envoie à l'Arduino"""
    default_gain = float (0.4) # Valeur par défaut
    Gainreg_entry.delete(0, tk.END)  # Efface l'entrée actuelle
    Gainreg_entry.insert(0, str(default_gain))  # Insère la valeur par défaut
    
    #print("reset_Gainreg() a été appelé")  # 🔍 Vérification
    #print(f"Valeur réinitialisée : {default_gain}")  # 🔍 Vérification
    # Envoyer la valeur par défaut à l'Arduino
    arduino.write(f"GAINREG:{default_gain}\n".encode())
    
    messagebox.showinfo("Info", "Le Gain du regulateur  a été réinitialisé à sa valeur par défaut (0.4).")




# Variable pour suivre l'état du régulateur
is_regulation_on = False  # Le régulateur commence éteint (OFF)

def toggle_regulator():
    global is_regulation_on
    is_regulation_on = not is_regulation_on  # Change l'état ON/OFF
    print(f"🟢 État du régulateur modifié : {is_regulation_on}")

    if is_regulation_on:
        regulator_button.config(text="❌ Désactiver Régulateur", bg="red")
        arduino.write(b"REGON\n")
    else:
        regulator_button.config(text="✅ Activer Régulateur", bg="green")
        arduino.write(b"REGOFF\n")

# Fonction pour envoyer les valeurs REG modifiées à l'Arduino
def send_REG_values():
    reg_values = []

    # Récupérer et vérifier chaque champ
    for i in range(6):
        value = entries[f"reg_{i}"].get().strip()  # Récupérer la valeur entrée
        if value == "":  # Si le champ est vide, garder la valeur par défaut
            reg_values.append(default_REG_values[i])
        else:
            try:
                reg_values.append(float(value))  # Convertir en float
            except ValueError:
                messagebox.showerror("Erreur", f"REG[{i}] ({reg_labels[i]}) contient une valeur invalide.")
                return  # Arrêter l'envoi si une valeur est invalide

    # Construire la commande pour Arduino
    reg_command = f"REGVALUES:{','.join(map(str, reg_values))}\n"
    
    # Envoyer au port série
    arduino.write(reg_command.encode())
    messagebox.showinfo("Succès", "Les nouvelles valeurs de REG ont été envoyées.")

# Reset les valeurs du regulateurs a celles par defaut
def reset_REG_values():
    """Réinitialise les coefficients du régulateur aux valeurs par défaut"""
    print("reset_REG_values() a été appelé")  # 🔍 Vérification
    for i in range(6):
        entries[f"reg_{i}"].delete(0, tk.END)  # Efface la valeur actuelle
        entries[f"reg_{i}"].insert(0, str(default_REG_values[i]))  # Insère la valeur par défaut
    
    # Envoyer les valeurs par défaut à l'Arduino
    reg_command = f"REGVALUES:{','.join(map(str, default_REG_values))}\n"
    print(reg_command)
    arduino.write(reg_command.encode())
    
    messagebox.showinfo("Info", "Les valeurs du régulateur ont été réinitialisées aux valeurs par défaut.")



# Function to open file dialog and select where to save the CSV file
def save_csv():
    global csv_writer, csv_file
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        # Open the file in write mode
        csv_file = open(file_path, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Time', 'Temp1', 'Temp2', 'Temp3', 'Temp4', 'Erreur', 'Commande PWM', 'Setpoint', 'Stabilité atteinte (s)'])
        messagebox.showinfo("Info", f"CSV file will be saved to: {file_path}")

# Enregistrer les dernieres valeurs entrees par l'utilisateur
def save_user_config():
    config = {
        "setpoint": setpoint_entry.get(),
        "gainreg": Gainreg_entry.get(),
        "reg_values": [entries[f"reg_{i}"].get() for i in range(6)]
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(config, f)
    print("📁 Configuration sauvegardée.")


# 🛠️ Création du cadre principal avec une grille
page_principale.columnconfigure(0, weight=1)  # Centre les éléments horizontalement

# 📌 Cadre supérieur pour "Enregistrer CSV"
top_frame = tk.Frame(page_principale)
top_frame.grid(row=0, column=0, pady=20)  # Ajoute un espacement en haut

save_button = tk.Button(top_frame, text="📁 Enregistrer les mesures", font=("Times New Roman", 20, "bold"), 
                        command=save_csv, bg="green", fg="white", width=30)
save_button.pack(pady=20)

# 📌 Cadre central (peut contenir d'autres éléments)
center_frame = tk.Frame(page_principale)
center_frame.grid(row=1, column=0, pady=100)  # Ajoute de l'espace pour équilibrer



# Create input field and button to send setpoint to Arduino
setpoint_label = tk.Label(page_temperature, text="Entrer la température désirée (°C):", font=("Times New Roman", 20, "bold"))
setpoint_label.pack(padx=20, pady=20)
setpoint_entry = tk.Entry(page_temperature, font=("Times New Roman", 20), width=50)
setpoint_entry.pack(padx=20, pady=10, ipady=10)
setpoint_button = tk.Button(page_temperature, text="Valider", font=("Times New Roman", 18, "bold"), command=send_setpoint, bg="blue", fg="white", width=15)
setpoint_button.pack(padx=10, pady=10)

# 🛠️ Création du cadre principal pour organiser les éléments page regulateur
frame_reg = tk.Frame(page_regulateur)
frame_reg.pack(pady=30)

# 🎯 Saisie du Gain du régulateur (entrée + bouton dans une ligne)
Gain_frame = tk.Frame(frame_reg)
Gain_frame.pack(pady=20)

Gainreg_label = tk.Label(Gain_frame, text="Gain du régulateur :", font=("Times New Roman", 20, "bold"))
Gainreg_label.grid(row=0, column=0, padx=20, pady=10, sticky="e")  # Aligné à droite

Gainreg_entry = tk.Entry(Gain_frame, font=("Times New Roman", 20), width=15, justify="center")
Gainreg_entry.grid(row=0, column=1, padx=20, pady=10, ipady=5)  # Aligné à gauche

Gainreg_button = tk.Button(Gain_frame, text="Valider", font=("Times New Roman", 20, "bold"), 
                           command=send_Gainreg, bg="blue", fg="white", width=20)
Gainreg_button.grid(row=0, column=2, padx=20, pady=10)

# 🔄 Bouton pour réinitialiser le GainREG (en dessous du bouton Valider)
reset_gain_button = tk.Button(Gain_frame, text="Réinitialiser", font=("Times New Roman", 18, "bold"),
                              command=reset_Gainreg, bg="gray", fg="white", width=20)
reset_gain_button.grid(row=1, column=2, padx=20, pady=10)  # On met row=1 pour qu'il soit en dessous

# 🛠️ Cadre pour stocker les coefficients du régulateur
coeff_frame = tk.Frame(frame_reg)
coeff_frame.pack(pady=15)


for i, label_text in enumerate(reg_labels):
    row_frame = tk.Frame(coeff_frame)
    row_frame.pack(pady=15)

    label = tk.Label(row_frame, text=label_text + " :", font=("Times New Roman", 20, "bold"))
    label.pack(side="left", padx=20, pady=10)

    entry = tk.Entry(row_frame, font=("Times New Roman", 20), width=20, justify="center")
    entry.pack(side="left", padx=20, pady=10, ipady=5)

    entries[f"reg_{i}"] = entry  # Stocker les entrées pour récupération ultérieure

# 🟢 Bouton pour envoyer les nouvelles valeurs du régulateur
send_button = tk.Button(frame_reg, text="Appliquer les réglages", font=("Times New Roman", 20, "bold"), command=send_REG_values, width=20, bg="blue", fg="white")
send_button.pack(pady=30)

# 🔄 Bouton pour réinitialiser les valeurs du régulateur
reset_button = tk.Button(frame_reg, text="Réinitialiser les réglages", font=("Times New Roman", 20, "bold"), 
                         command=reset_REG_values, width=20, bg="gray", fg="white")
reset_button.pack(pady=20)

# 📌 Bouton d’activation du régulateur en bas, bien centré
bottom_frame = tk.Frame(page_regulateur)
bottom_frame.pack(side="bottom", pady=30)  # positionnement en bas de la page

# 🔹 Configuration du bouton au démarrage
regulator_button = tk.Button(bottom_frame, text="✅ Activer Régulateur", font=("Times New Roman", 22, "bold"), command=toggle_regulator, 
    bg="green", fg="white", width=40, height=2
)
regulator_button.pack()

# Charger les valeurs a l'ouverture
def load_user_config():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            config = json.load(f)
        # Remplir les champs
        setpoint_entry.delete(0, tk.END)
        setpoint_entry.insert(0, config.get("setpoint", ""))

        Gainreg_entry.delete(0, tk.END)
        Gainreg_entry.insert(0, config.get("gainreg", ""))

        reg_vals = config.get("reg_values", [])
        for i in range(min(len(reg_vals), 6)):
            entries[f"reg_{i}"].delete(0, tk.END)
            entries[f"reg_{i}"].insert(0, reg_vals[i])

        print("🔁 Configuration rechargée.")


# Contenu de la page "Aide"
aide_frame = tk.Frame(page_aide, bg="#F0F0F0")
aide_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Titre
titre_label = tk.Label(aide_frame, text="🧭 Guide d'utilisation", font=("Times New Roman", 30, "bold"), bg="#F0F0F0")
titre_label.pack(pady=(0, 20))

# Texte explicatif
texte = (
    "Bienvenue dans l'interface de régulation thermique.\n\n"
    "🔹 Onglet 'Enregistrer' : permet d'enregistrer les données dans un fichier CSV.\n"
    "🔹 Onglet 'Température' : entrez une température cible et validez pour envoyer la consigne.\n"
    "🔹 Onglet 'Régulateur' : ajustez les coefficients du régulateur et activez/désactivez l'asservissement.\n"
    "🔹 LED de stabilité (coin supérieur droit) :"
)
texte_label = tk.Label(aide_frame, text=texte, font=("Times New Roman", 22), justify="left", bg="#F0F0F0")
texte_label.pack(anchor="w")

# LED verte - Température stable
led_row1 = tk.Frame(aide_frame, bg="#F0F0F0")
led_row1.pack(anchor="w", pady=5)
led_canvas1 = tk.Canvas(led_row1, width=20, height=20, bg="#F0F0F0", highlightthickness=0)
led_canvas1.create_oval(2, 2, 18, 18, fill="green")
led_canvas1.pack(side="left", padx=(40,10))
tk.Label(led_row1, text="Température stable", font=("Times New Roman", 22), bg="#F0F0F0").pack(side="left")

# LED rouge - Température instable
led_row2 = tk.Frame(aide_frame, bg="#F0F0F0")
led_row2.pack(anchor="w", pady=5)
led_canvas2 = tk.Canvas(led_row2, width=20, height=20, bg="#F0F0F0", highlightthickness=0)
led_canvas2.create_oval(2, 2, 18, 18, fill="red")
led_canvas2.pack(side="left", padx=(40,10))
tk.Label(led_row2, text="Température instable", font=("Times New Roman", 22), bg="#F0F0F0").pack(side="left")

# Conseils supplémentaires
conseils = (
    "\n🔐 Assurez-vous que l'Arduino est connecté sur le bon port COM.\n"
    "⚠️ Ne quittez pas brutalement l'interface pour éviter la perte de données."
)
conseils_label = tk.Label(aide_frame, text=conseils, font=("Times New Roman", 22), justify="left", bg="#F0F0F0")
conseils_label.pack(anchor="w", pady=(10, 0))




#Start real-time plot updating
start_time = time.time()  # Start time for plotting
ani = FuncAnimation(fig, update_data, interval=100, cache_frame_data=False)


load_user_config()  # 🔁 Charger les anciennes valeurs sauvegardées
# Start the Tkinter GUI
tkinter_plot = plt.gcf().canvas.get_tk_widget()
tkinter_plot.pack(fill=tk.BOTH, expand=1)
plt.show()


def on_close():
    save_user_config()
    if csv_file:
        csv_file.close()
    arduino.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()

# Cleanup and close the CSV file when the program exits
if csv_file:
    csv_file.close()
arduino.close()
