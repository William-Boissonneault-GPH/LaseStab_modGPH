import customtkinter as ctk
from MAIN import lancer_simulation  
import customtkinter as ctk
from tkinter import messagebox
import threading  # Pour lancer la simulation sans bloquer l'interface

ctk.set_appearance_mode("dark")  # Mode sombre
ctk.set_default_color_theme("blue")  # Thème bleu

class SimulationInterface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulation Thermique")
        self.geometry("600x500")

        ctk.set_appearance_mode("dark")  
        ctk.set_default_color_theme("blue")

        # Stocker les variables
        self.variables = {
            "pos_x_thermo1": ctk.StringVar(value="0.10475"),
            "pos_y_thermo1": ctk.StringVar(value="0.031"),
            "pos_x_thermo2": ctk.StringVar(value="0.05835"),
            "pos_y_thermo2": ctk.StringVar(value="0.031"),
            "pos_x_thermo3": ctk.StringVar(value="0.01225"),
            "pos_y_thermo3": ctk.StringVar(value="0.031"),
            "coefficient_convection": ctk.StringVar(value="15"),
            "capacite_thermique": ctk.StringVar(value="900"),
            "conductivite_thermique": ctk.StringVar(value="237"),
            "dim_x_plaque": ctk.StringVar(value="0.11875"),
            "dim_y_plaque": ctk.StringVar(value="0.062"),
            "dim_z_plaque": ctk.StringVar(value="0.002"),
            "temperature_initiale": ctk.StringVar(value="24")
        }

        self.create_widgets()

    def create_widgets(self):
        """Crée et place les widgets dans l'interface"""
        row = 0
        ctk.CTkLabel(self, text="Paramètres de la Simulation", font=("Arial", 16, "bold")).grid(row=row, column=0, columnspan=2, pady=10)

        # Création des entrées pour chaque paramètre
        for key, var in self.variables.items():
            row += 1
            label = key.replace("_", " ").capitalize()
            ctk.CTkLabel(self, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkEntry(self, textvariable=var).grid(row=row, column=1, padx=10, pady=5)

        # Bouton pour lancer la simulation
        row += 1
        self.btn_lancer = ctk.CTkButton(self, text="Lancer Simulation", command=self.lancer_simulation_interface)
        self.btn_lancer.grid(row=row, column=0, columnspan=2, pady=20)

    def lancer_simulation_interface(self):
        """Récupère les paramètres et lance la simulation dans un thread séparé"""
        try:
            # Convertir les entrées en float
            params = {key: float(var.get()) for key, var in self.variables.items()}

            # Affichage des paramètres récupérés 
            print("Paramètres de simulation récupérés :", params)

            # Lancer la simulation dans un thread pour pas bloquer l'interface
            threading.Thread(target=lancer_simulation, daemon=True).start()

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")

if __name__ == "__main__":
    app = SimulationInterface()
    app.mainloop()

