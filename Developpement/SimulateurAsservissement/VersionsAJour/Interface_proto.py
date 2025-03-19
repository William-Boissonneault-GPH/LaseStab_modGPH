import serial
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import time
import numpy as np

csv_writer = None
csv_file = None

# Define serial port and parameters
SERIAL_PORT = 'COM3'  # Update this with your Arduino's serial port
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

notebook.add(page_principale, text="Enregistrer")
notebook.add(page_temperature, text="Température")
notebook.add(page_regulateur, text="Régulateur")


# Create variables to hold the data
time_data, temp1_data, temp2_data, temp3_data, temp4_data, setpoint_data= [], [], [], [], [], []

# Noms des valeurs REG et leurs indices
reg_labels = [
    "Coefficient P", "Coefficient I", "Coefficient D", 
    "Facteur de Normalisation", "Dérivée 1", "Dérivée 2"
]

# Valeurs par défaut de REG (initialisées avec les valeurs Arduino)
default_REG_values = [1.0, -1.8995, 0.901, 1.0, -1.913, 0.913]
entries = {}

lastError = 999
lastCommand = 999
lastSetpoint = 999

# Create a plot for real-time data
plt.rcParams["legend.fontsize"] = 12 # Forcer la taille de la légende globalement
fig, ax = plt.subplots(figsize=(15,10), dpi=100)
scatter_temp1 = ax.scatter([], [], label='Temperature Thermistance 1', s=20)
scatter_temp2 = ax.scatter([], [], label='Temperature Thermistance 2', s=20)
scatter_temp3 = ax.scatter([], [], label='Temperature estimée Thermistance 3', s=20)
scatter_temp4 = ax.scatter([], [], label='Temperature mesurée Thermistance 3', s=20)
scatter_setpoint = ax.scatter([], [], label='Consigne Température', s=10, color='black')


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
        if data:
            try:
                time_str, temp1, temp2, temp3, temp4, lastError, lastCommand, lastSetpoint = data.split(',')
                current_time = time.time() - start_time  # Calculate elapsed time
                time_data.append(current_time)
                temp1_data.append(float(temp1))
                temp2_data.append(float(temp2))
                temp3_data.append(float(temp3))
                temp4_data.append(float(temp4))

                setpoint_data.append(setpoint_float if setpoint_float is not None else 0)
                # Log data to CSV
                if csv_writer:
                    csv_writer.writerow([current_time, temp1, temp2, temp3, temp4, lastError, lastCommand, lastSetpoint, last_point])
                
                # Keep data within the plot window limit
                if len(time_data) > 100:
                    time_data = time_data[1:]
                    temp1_data = temp1_data[1:]
                    temp2_data = temp2_data[1:]
                    temp3_data = temp3_data[1:]
                    temp4_data = temp4_data[1:]
                    setpoint_data = setpoint_data[1:]

            except ValueError:
                raise  # Ignore invalid data

    # Ensure that offsets is a 2D array: we create a list of (time, temp) pairs
    scatter_temp1.set_offsets(np.column_stack((time_data, temp1_data)))
    scatter_temp2.set_offsets(np.column_stack((time_data, temp2_data)))
    scatter_temp3.set_offsets(np.column_stack((time_data, temp3_data)))
    scatter_temp4.set_offsets(np.column_stack((time_data, temp4_data)))
    scatter_setpoint.set_offsets(np.column_stack((time_data, setpoint_data)))  # Ajout de la consigne utilisateur

    if frame%10 == 0 and len(time_data) > 0:
        ax.set_xlim(max(time_data)-90, max(time_data)+10)  # Time axis dynamically adjusts
        #ax.set_ylim(min(min(temp1_data), min(temp2_data), min(temp3_data), min(temp4_data)),
        #        max(max(temp1_data), max(temp2_data), max(temp3_data), max(temp4_data)))
    
    return scatter_temp1, scatter_temp2, scatter_temp3, scatter_temp4, scatter_setpoint



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
        arduino.write(f"GAINREG:{Gainreg_float}\n".encode())  # Envoyer la valeur en Serial
        messagebox.showinfo("Succès", f"Gain régulateur envoyé : {Gainreg_float}")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique valide.")
   

def send_command():
    command = command_entry.get()
    if command:
        arduino.write(f"ASSERVT3:{command}\n".encode())  # Send custom command to Arduino
    else:
        messagebox.showerror("Error", "Please enter a command.")
"""

"""



# Variable pour suivre l'état du régulateur
is_regulation_on = False  # Le régulateur commence éteint (OFF)

def toggle_regulator():
    global is_regulation_on
    is_regulation_on = not is_regulation_on  # Change l'état ON/OFF
    print(f"🟢 État du régulateur modifié : {is_regulation_on}")

    if is_regulation_on:
        regulator_button.config(text="❌ Désactiver Régulateur", bg="red")
        arduino.write(f"REGSET:{is_regulation_on}\n".encode())
    else:
        regulator_button.config(text="✅ Activer Régulateur", bg="green")
        arduino.write(f"REGSET:{is_regulation_on}\n".encode())

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

def reset_REG_values():
    """Réinitialise les coefficients du régulateur aux valeurs par défaut"""
    for i in range(6):
        entries[f"reg_{i}"].delete(0, tk.END)  # Efface la valeur actuelle
        entries[f"reg_{i}"].insert(0, str(default_REG_values[i]))  # Insère la valeur par défaut
    
    # Envoyer les valeurs par défaut à l'Arduino
    reg_command = f"REGVALUES:{','.join(map(str, default_REG_values))}\n"
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
        csv_writer.writerow(['Time', 'Temp1', 'Temp2', 'Temp3', 'Temp4', 'Erreur', 'Commande PWM', 'Setpoint'])
        messagebox.showinfo("Info", f"CSV file will be saved to: {file_path}")

# 🛠️ Création du cadre principal avec une grille
page_principale.columnconfigure(0, weight=1)  # Centre les éléments horizontalement

# 📌 Cadre supérieur pour "Enregistrer CSV"
top_frame = tk.Frame(page_principale)
top_frame.grid(row=0, column=0, pady=20)  # Ajoute un espacement en haut

save_button = tk.Button(top_frame, text="📁 Charger CSV", font=("Times New Roman", 20, "bold"), 
                        command=save_csv, bg="green", fg="white", width=30)
save_button.pack(pady=20)

# 📌 Cadre central (peut contenir d'autres éléments)
center_frame = tk.Frame(page_principale)
center_frame.grid(row=1, column=0, pady=100)  # Ajoute de l'espace pour équilibrer



# Create input field and button to send setpoint to Arduino
setpoint_label = tk.Label(page_temperature, text="Entrer la température désirée (°C):", font=("Times New Roman", 20, "bold"))
setpoint_label.pack(padx=20, pady=20)
setpoint_entry = tk.Entry(page_temperature, font=("Times New Roman", 16), width=50)
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

Gainreg_button = tk.Button(Gain_frame, text="Valider", font=("Times New Roman", 20, "bold"), command=send_Gainreg, bg="blue", fg="white", width=20)
Gainreg_button.grid(row=0, column=2, padx=20, pady=10)

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


"""
# Create input field and button to send custom command to Arduino
command_label = tk.Label(root, text="0 pour asservir T3_estimé, 1 pour T3:", font=("Times New Roman", 14, "bold"))
command_label.pack(padx=10, pady=10)
command_entry = tk.Entry(root, font=("Times New Roman", 14))
command_entry.pack(padx=10, pady=10)
command_button = tk.Button(root, text="Choisir Asserv", font=("Times New Roman", 14, "bold"), command=send_command)
command_button.pack(padx=10, pady=10)
"""




#Start real-time plot updating
start_time = time.time()  # Start time for plotting
ani = FuncAnimation(fig, update_data, interval=100, cache_frame_data=False)


# Start the Tkinter GUI
tkinter_plot = plt.gcf().canvas.get_tk_widget()
tkinter_plot.pack(fill=tk.BOTH, expand=1)
plt.show()

root.mainloop()

# Cleanup and close the CSV file when the program exits
if csv_file:
    csv_file.close()
arduino.close()
