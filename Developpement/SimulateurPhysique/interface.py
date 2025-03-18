import os
import json
import customtkinter as ctk
from MAIN import lancer_simulation  
from tkinter import messagebox
from PIL import Image  
from threading import Thread
from tkinter import filedialog


ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

class SimulationInterface(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulation Thermique")
        self.geometry("1100x600")

        # Définition des paramètres par section
        self.thermistances = {
            "Position_x_thermo1": "0.10475", "Position_y_thermo1": "0.031",
            "Position_x_thermo2": "0.05835", "Position_y_thermo2": "0.031",
            "Position_x_thermo3": "0.01225", "Position_y_thermo3": "0.031"
        }

        self.tec = {
            "Position_x_TEC": "0.096", "Position_y_TEC": "0.031",
            "Dimension_x_TEC": "0.015", "Dimension_y_TEC": "0.0156",
            "Coefficient_couplage_a": "0.1493",  
            "Coefficient_couplage_b": "1.3291"
        }

        self.plaque = {
            "Dimension_x_plaque": "0.11875", "Dimension_y_plaque": "0.062",
            "Dimension_z_plaque": "0.0016", "Coéfficient_convection": "14",
            "Température_initiale": "24"
        }

        self.proprietes_materiau = {
            "Conductivité_thermique": "180", "Densité": "2700",
            "Capacité_thermique": "900"
        }

        self.details_simulation = {
            "Échelon_courant_(A)": "-0.7",
            "Temps_simulation_(s)": "1600",
            "Position_x_perturbation": ctk.StringVar(value="0.05"),  # Nouveau champ pour la position X
            "Position_y_perturbation": ctk.StringVar(value="0.03"),  # Nouveau champ pour la position Y
            "Puissance_perturbation_(W)": ctk.StringVar(value="0.3")   # Nouveau champ pour la puissance thermique
            
        }

        # Créer les widgets
        self.create_widgets()

        ###Loading bar
        # Create a label
        self.label = ctk.CTkLabel(self, text="En attente de simulation", font=("Arial", 14))
        self.label.grid(row=1, column=4, pady=5, padx=20, sticky="ew")

        # Create the progress bar
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal")
        self.progress_bar.grid(row=2, column=4, pady=5, padx=20, sticky="ew")
        self.progress_bar.set(0)  # Initialize at 0%

    def ajouter_image(self):
        """Ajoute une image explicative sous les paramètres avec un titre"""
        try:
            # Chemin vers l'image
            chemin_image = os.path.join(os.path.dirname(__file__), "schémadimensions.png")

            # Créer un cadre pour l'image et le titre
            frame_image = ctk.CTkFrame(self)
            frame_image.grid(row=21, column=0, columnspan=5, pady=20, padx=10, sticky="nsew")

            # Ajouter un titre au-dessus de l’image
            titre = ctk.CTkLabel(frame_image, text="Schéma des dimensions demandées", font=("Arial", 14, "bold"))
            titre.pack(pady=(10, 5))

            # Charger et afficher l’image
            image = ctk.CTkImage(light_image=Image.open(chemin_image), size=(670, 380))  # Augmente la taille
            label_image = ctk.CTkLabel(frame_image, image=image, text="")
            label_image.pack(pady=5)

        except Exception as e:
            print(f"Erreur lors du chargement de l'image : {e}")

    def create_widgets(self):
        """Crée et place les widgets dans l'interface en sections"""
        self.create_section("Thermistances", self.thermistances, 0)
        self.create_section("TEC", self.tec, 1)
        self.create_section("Plaque", self.plaque, 2)
        self.create_section("Propriétés du matériau", self.proprietes_materiau, 3)
        self.create_section("Détails de la simulation", self.details_simulation, 4, add_button=True)
        self.ajouter_image()


    def create_section(self, title, parameters, col, add_button=False):
        """Crée une section avec un titre et des entrées pour les paramètres."""
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=col, padx=10, pady=10, sticky="n")

        ctk.CTkLabel(frame, text=title, font=("Arial", 14, "bold")).pack(pady=5)
        
        for key, default_value in parameters.items():
            var = ctk.StringVar(value=default_value)
            parameters[key] = var  # Stocker la variable pour la récupérer plus tard
            ctk.CTkLabel(frame, text=key.replace("_", " ")).pack(anchor="w")
            ctk.CTkEntry(frame, textvariable=var).pack(pady=2)

        # Ajouter un bouton pour lancer la simulation uniquement dans la dernière section
        if add_button:
            ctk.CTkButton(frame, text="Charger Paramètres", command=self.charger_parametres).pack(pady=5)
            ctk.CTkButton(frame, text="Lancer Simulation", command=self.lancer_simulation_interface).pack(pady=10)

    def update_progress(self, progress):
        """ Update the progress bar """
        self.progress_bar.set(progress/100)
        self.label.configure(text="Temps restant : [Estime par derivé]")

    def lancer_simulation_interface(self):
        """Récupère les paramètres et lance la simulation."""
        try:
            params = {**self.get_values(self.thermistances),
                    **self.get_values(self.tec),
                    **self.get_values(self.plaque),
                    **self.get_values(self.proprietes_materiau),
                    **self.get_values(self.details_simulation)}
            
            self.sauvegarder_parametres()

            # Transformation des valeurs de perturbation en une liste de sources
            params["Sources_chaleur"] = [{
                "x": params.pop("Position_x_perturbation"),
                "y": params.pop("Position_y_perturbation"),
                "puissance": params.pop("Puissance_perturbation_(W)")
            }]
            
            print("Paramètres récupérés :", params)
            
            self.label.configure(text="Simulation en cours...")
            thread = Thread(target=lancer_simulation, args=(params, self.update_progress), daemon=True)
            thread.start()

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")

    def get_values(self, param_dict):
        """Convertit les valeurs des dictionnaires en float."""
        return {key: float(var.get()) for key, var in param_dict.items()}

    def sauvegarder_parametres(self):
        """Sauvegarde les paramètres actuels dans un fichier JSON."""
        params = {**self.get_values(self.thermistances),
                **self.get_values(self.tec),
                **self.get_values(self.plaque),
                **self.get_values(self.proprietes_materiau),
                **self.get_values(self.details_simulation)}

        params["Sources_chaleur"] = [{
            "x": params.pop("Position_x_perturbation"),
            "y": params.pop("Position_y_perturbation"),
            "puissance": params.pop("Puissance_perturbation_(W)")
        }]

        with open("derniere_simulation.json", "w") as f:
            json.dump(params, f, indent=4)
        
        print("Paramètres sauvegardés dans 'derniere_simulation.json'")


    def charger_parametres(self):
        """Charge un fichier JSON et remplit les entrées de l'interface avec ces valeurs."""
        fichier = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")])
        if not fichier:
            return  

        try:
            with open(fichier, "r") as f:
                params = json.load(f)

            # Répartir les valeurs dans les dictionnaires de l'interface
            for key, var in {**self.thermistances, **self.tec, **self.plaque, **self.proprietes_materiau, **self.details_simulation}.items():
                if key in params:
                    var.set(str(params[key]))  # Remettre sous forme de string pour les champs d'entrée

            # Remettre les valeurs des perturbations
            if "Sources_chaleur" in params and len(params["Sources_chaleur"]) > 0:
                source = params["Sources_chaleur"][0]
                self.details_simulation["Position_x_perturbation"].set(str(source["x"]))
                self.details_simulation["Position_y_perturbation"].set(str(source["y"]))
                self.details_simulation["Puissance_perturbation_(W)"].set(str(source["puissance"]))


            print("Paramètres chargés avec succès depuis", fichier)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier JSON.\n{e}")


if __name__ == "__main__":
    app = SimulationInterface()
    app.mainloop()
