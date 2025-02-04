import numpy as np
from PlaqueThermique import PlaqueThermique
#class thermo:
   # def __init__(self, position, diamètre, épaisseur, plaque):
     #   self.position = position
     #   self.diamètre = diamètre
     #   self.épaisseur = épaisseur
      #  self.plaque = plaque

  #  def lire_temperature(self):

       # dx, dy = self.plaque.grosseurElement[:2]

        # Convertir la position en indices de la matrice
       # x_index = int(self.position[0] / dx)
       # y_index = int(self.position[1] / dy)

        #Prendre en compte la grosseur de la thermores
        #rayon_px = int((self.diamètre / 2) / dx)
        #indices_x = slice(max(0, x_index - rayon_px), min(self.plaque.matTemperature.shape[1], x_index + rayon_px + 1))
        #indices_y = slice(max(0, y_index - rayon_px), min(self.plaque.matTemperature.shape[0], y_index + rayon_px + 1))

        #Prendre la temp moy de cette zone
        #return np.mean(self.plaque.matTemperature[indices_y, indices_x])
    
    #import numpy as np

class thermo:
    def __init__(self, position, diamètre, épaisseur, plaque):
        self.position = position  # (x, y) en mètres
        self.diamètre = diamètre
        self.épaisseur = épaisseur
        self.plaque = plaque
        
        # Conversion de la position en indices de la matrice (en prenant en compte les tailles des éléments)
        self.x_index = round(self.position[0] / plaque.grosseurElement[0])
        self.y_index = round(self.position[1] / plaque.grosseurElement[1])
        
        # Affichage des indices pour débogage
        print(f"Indices calculés pour la thermorésistance : x_index = {self.x_index}, y_index = {self.y_index}")

    def lire_temperature(self):
        # indices valides?
        if (0 <= self.x_index < self.plaque.matTemperature.shape[1] and
            0 <= self.y_index < self.plaque.matTemperature.shape[0]):
            return self.plaque.matTemperature[self.y_index, self.x_index]
        else:
            print("Indices hors des limites de la matrice.")
            return np.nan  # Retourne NaN si les indices sont hors limites
