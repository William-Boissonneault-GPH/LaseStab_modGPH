###Data points from spec sheet
import numpy as np
from scipy.interpolate import interp1d


data = np.array([
    [0, 6, 7.0],
    [50, 6, 1.8],
    [0, 4.8, 6.5],
    [50, 4.8, 1.5],
    [0, 3.6, 5.4],
    [50, 3.6, 0.7],
    [0, 2.4, 4.2],
    [40, 2.4, 0.7],
    [0, 1.2, 2.15],
    [30, 1.2, 0.3]
])

DeltaT = data[:, 0]
Current = data[:, 1]
Q = data[:, 2]

unique_currents = np.unique(Current)

fits = {}
for current in unique_currents:
    mask = Current == current
    DeltaT_subset = DeltaT[mask]
    Q_subset = Q[mask]
    # Linear fit (slope and intercept)
    coefficients = np.polyfit(DeltaT_subset, Q_subset, 1)
    fits[current] = coefficients

def predict_Q(deltaT, current):
    # Interpolate between currents
    currents = np.array(list(fits.keys()))
    slopes = np.array([fits[c][0] for c in currents])
    intercepts = np.array([fits[c][1] for c in currents])

    slope_interp = interp1d(currents, slopes, kind='linear', fill_value='extrapolate')
    intercept_interp = interp1d(currents, intercepts, kind='linear', fill_value='extrapolate')

    slope = slope_interp(current)
    intercept = intercept_interp(current)

    return slope * deltaT + intercept

class ActionneurThermique:
    
    def __init__(self, position, dimensions, matPlaque, dimensionElementFiniePlaque):
        self.matElementBinaire = np.zeros_like(matPlaque)
        self.matPerturbation = np.zeros_like(matPlaque)

        ###(en x, en y) [m]
        self.dimensions = dimensions
        self.aireEnM2 = dimensions[0] * dimensions[1]

        ###(x,y) [m]
        self.postionCentre = position

        self.dimensionElementFiniePlaque = dimensionElementFiniePlaque

        ### Trouve les indices de matrice
        indiceCentre = (round(self.postionCentre[0] / self.dimensionElementFiniePlaque["dX"]), round(self.postionCentre[1] / self.dimensionElementFiniePlaque["dY"]))
        largeurIndice = (round(dimensions[0] / self.dimensionElementFiniePlaque["dX"]), round(dimensions[1] / self.dimensionElementFiniePlaque["dY"]))
        Indices = np.array((int(indiceCentre[1] - largeurIndice[1]/2), int(indiceCentre[1] + largeurIndice[1]/2), int(indiceCentre[0] - largeurIndice[0]/2), int(indiceCentre[0] + largeurIndice[0]/2)))

        if np.min(Indices) < 0:
            raise ValueError("L'actionneur dépasse de la plaque")
        
        self.nombreElement = (Indices[1] - Indices[0]) * (Indices[3] - Indices[2])
        self.aireEnM2_element = self.aireEnM2 / self.nombreElement

        self.matElementBinaire[Indices[0]:Indices[1], Indices[2]:Indices[3]] = 1

        ###le Tec n'est pas parfaitement couplé
        self.couplage = 0.9
        pass

    def updateMatPerturbation(self, courant, matTemperature, T_ambiant):
        ###Trouver température côté chaud TEC
        T_h = np.sum(matTemperature * self.matElementBinaire)/self.nombreElement
        deltaT = T_h - T_ambiant

        if courant < 0:
            Q_tot = -1 * predict_Q(abs(deltaT), abs(courant))
        else:
            Q_tot = predict_Q(abs(deltaT), courant)
        
        if courant == 0:
            Q_tot = 0
        
        print(f"Q du Tec {Q_tot}, T_h {T_h}")
        self.matPerturbation = self.couplage* self.matElementBinaire * Q_tot / self.nombreElement
        
