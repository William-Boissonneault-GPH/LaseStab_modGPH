import numpy as np
class thermo:
    def __init__(self, position, diamètre, épaisseur, plaque):
        self.position = position
        self.diamètre = diamètre
        self.épaisseur = épaisseur
        self.plaque = plaque

    def lire_temperature(self):

        dx, dy = self.plaque.grosseurElement[:2]

        # Convertir la position en indices de la matrice
        x_index = int(self.position[0] / dx)
        y_index = int(self.position[1] / dy)

        #Prendre en compte la grosseur de la thermores
        rayon_px = int((self.diamètre / 2) / dx)
        indices_x = slice(max(0, x_index - rayon_px), min(self.plaque.matTemperature.shape[1], x_index + rayon_px + 1))
        indices_y = slice(max(0, y_index - rayon_px), min(self.plaque.matTemperature.shape[0], y_index + rayon_px + 1))

        #Prendre la temp moy de cette zone
        return np.mean(self.plaque.matTemperature[indices_y, indices_x])