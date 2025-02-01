import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 📌 Configuration du port série
PORT = "COM3"  # ⚠️ Remplacez par le port correct ("COMX" sous Windows, "/dev/ttyUSB0" sous Linux/Mac)
BAUDRATE = 9600
TIMEOUT = 1

# 🔄 Connexion au port série
try:
    arduino = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
    print(f"✅ Connexion au port {PORT} réussie.")
except Exception as e:
    print(f"❌ Erreur : Impossible d'ouvrir le port série {PORT}.")
    print(e)
    exit()

# 📊 Initialisation des listes de données
temps = []
t1_data = []
t2_data = []
t3_data = []

# 📌 Fonction de mise à jour du graphique
def update(frame):
    global temps, t1_data, t2_data, t3_data

    try:
        # 📡 Lire une ligne envoyée par l'Arduino
        line = arduino.readline().decode("utf-8").strip()
        
        if line:
            print(line)  # Afficher les données dans le terminal
            valeurs = line.split(",")  # Séparer les valeurs CSV

            if len(valeurs) == 4:  # Vérifier qu'il y a 4 valeurs (Temps, T1, T2, T3)
                t, t1, t2, t3 = map(float, valeurs)  # Convertir en nombres
                
                # 📊 Ajouter les nouvelles valeurs aux listes
                temps.append(t)
                t1_data.append(t1)
                t2_data.append(t2)
                t3_data.append(t3)

                # 🎨 Mise à jour du graphique
                ax1.clear()
                ax1.plot(temps, t1_data, label="T1 (°C)", color="red")
                ax1.plot(temps, t2_data, label="T2 (°C)", color="blue")
                ax1.plot(temps, t3_data, label="T3 (°C)", color="green")

                ax1.set_title("Températures en Temps Réel")
                ax1.set_xlabel("Temps (s)")
                ax1.set_ylabel("Température (°C)")
                ax1.legend()
                ax1.grid()

    except Exception as e:
        print(f"⚠️ Erreur de lecture : {e}")

# 🔄 Configuration de l'animation pour mise à jour toutes les 1 seconde
fig, ax1 = plt.subplots()
ani = animation.FuncAnimation(fig, update, interval=1000)  

print("📡 Lecture et affichage en temps réel... (Appuyez sur Ctrl+C pour arrêter)")
plt.show()

# 🛑 Fermeture du port série après fermeture du graphique
arduino.close()
print("🔌 Connexion série fermée.")
