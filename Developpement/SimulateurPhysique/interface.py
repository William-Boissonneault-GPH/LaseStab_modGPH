import customtkinter as ctk

# Seulement un essai, les paramètres ont pas rapport et ce n'est pas encore lié avec la simul
ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème bleu

class SimulationUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Paramètres de Simulation")
        self.geometry("400x350")

        # Température initiale
        self.create_slider("Température initiale (°C):", 0, 100, 25, "temp_var")

        # Conductivité thermique
        self.create_slider("Conductivité thermique (W/mK):", 50, 400, 200, "cond_var")

        # Épaisseur de la plaque
        self.create_slider("Épaisseur de la plaque (mm):", 1, 10, 5, "epaisseur_var")

        # Bouton de lancement
        self.start_button = ctk.CTkButton(self, text="Lancer la simulation", command=self.lancer_simulation)
        self.start_button.pack(pady=20)

    def create_slider(self, label_text, min_val, max_val, default_val, var_name):
        """Crée un slider avec un champ d'entrée pour voir et ajuster précisément la valeur"""
        frame = ctk.CTkFrame(self)
        frame.pack(pady=5, fill="x", padx=10)

        label = ctk.CTkLabel(frame, text=label_text)
        label.pack(side="left", padx=10)

        var = ctk.DoubleVar(value=default_val)
        setattr(self, var_name, var)  # Stocke la variable dans l'objet

        entry = ctk.CTkEntry(frame, textvariable=var, width=50)
        entry.pack(side="right", padx=10)

        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, variable=var, command=lambda v: var.set(round(float(v), 2)))
        slider.pack(side="right", expand=True, fill="x", padx=10)

    def lancer_simulation(self):
        """Récupère les valeurs et affiche la configuration choisie"""
        temp = self.temp_var.get()
        conductivite = self.cond_var.get()
        epaisseur = self.epaisseur_var.get()
        print(f"Simulation lancée avec Temp={temp}°C, Conductivité={conductivite} W/mK, Épaisseur={epaisseur} mm")

# Lancer l'interface
if __name__ == "__main__":
    app = SimulationUI()
    app.mainloop()

