import customtkinter as ctk
from MAIN import lancer_simulation  
from tkinter import messagebox
import threading  

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

class SimulationInterface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulation Thermique")
        self.geometry("600x500")

        # Stocker les variables
        self.variables = {
            "Position_x_thermo1": ctk.StringVar(value="0.10475"),
            "Position_y_thermo1": ctk.StringVar(value="0.031"),
            "Position_x_thermo2": ctk.StringVar(value="0.05835"),
            "Position_y_thermo2": ctk.StringVar(value="0.031"),
            "Position_x_thermo3": ctk.StringVar(value="0.01225"),
            "Position_y_thermo3": ctk.StringVar(value="0.031"),
            "Coéfficient_convection": ctk.StringVar(value="15"),
            "Capacité_thermique": ctk.StringVar(value="900"),
            "Conductivité_thermique": ctk.StringVar(value="237"),
            "Dimension_x_plaque": ctk.StringVar(value="0.11875"),
            "Dimension_y_plaque": ctk.StringVar(value="0.062"),
            "Dimension_z_plaque": ctk.StringVar(value="0.002"),
            "Température_initiale": ctk.StringVar(value="24"),
            "Échelon_courant_(A)": ctk.StringVar(value="-0.7"),
            "Temps_simulation_(s)": ctk.StringVar(value="1600"),
            "Position_x_TEC": ctk.StringVar(value="0.096"),
            "Position_y_TEC": ctk.StringVar(value="0.031"),
            "Dimension_x_TEC": ctk.StringVar(value="0.015"),
            "Dimension_y_TEC": ctk.StringVar(value="0.0156")

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
        """Récupère les paramètres et lance la simulation sur le thread principal."""
        try:
            params = {key: float(var.get()) for key, var in self.variables.items()}
            print("🟢 Paramètres récupérés :", params)  

            # Lancer la simulation sur le thread principal
            self.after(100, lambda: lancer_simulation(params))

            print("🟢 Simulation en cours...")  

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")

if __name__ == "__main__":
    app = SimulationInterface()
    app.mainloop()