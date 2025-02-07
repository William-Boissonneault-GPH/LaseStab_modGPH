###Data points from spec sheet
import numpy as np
from scipy.interpolate import interp1d


data_27 = np.array([
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

DeltaT_27 = data_27[:, 0]
Current_27 = data_27[:, 1]
Q_27 = data_27[:, 2]

unique_currents_27 = np.unique(Current_27)

fits_27 = {}
for current in unique_currents_27:
    mask = Current_27 == current
    DeltaT_subset = DeltaT_27[mask]
    Q_subset_27 = Q_27[mask]
    # Linear fit (slope and intercept)
    coefficients = np.polyfit(DeltaT_subset, Q_subset_27, 1)
    fits_27[current] = coefficients

def predict_Q_27(deltaT, current):
    # Interpolate between currents
    currents = np.array(list(fits_27.keys()))
    slopes = np.array([fits_27[c][0] for c in currents])
    intercepts = np.array([fits_27[c][1] for c in currents])

    slope_interp = interp1d(currents, slopes, kind='linear', fill_value='extrapolate')
    intercept_interp = interp1d(currents, intercepts, kind='linear', fill_value='extrapolate')

    slope = slope_interp(current)
    intercept = intercept_interp(current)

    return slope * deltaT + intercept



data_50 = np.array([
    [0, 6, 8.0],
    [50, 6, 2.7],
    [0, 4.8, 7.4],
    [50, 4.8, 2.5],
    [0, 3.6, 6.4],
    [50, 3.6, 1.5],
    [0, 2.4, 4.8],
    [50, 2.4, 0.5],
    [0, 1.2, 2.8],
    [30, 1.2, 0.5]
])

DeltaT_50 = data_50[:, 0]
Current_50 = data_50[:, 1]
Q_50 = data_50[:, 2]

unique_currents_50 = np.unique(Current_50)

fits_50 = {}
for current in unique_currents_50:
    mask = Current_50 == current
    DeltaT_subset = DeltaT_50[mask]
    Q_subset_50 = Q_50[mask]
    # Linear fit (slope and intercept)
    coefficients = np.polyfit(DeltaT_subset, Q_subset_50, 1)
    fits_50[current] = coefficients

def predict_Q_50(deltaT, current):
    # Interpolate between currents
    currents = np.array(list(fits_50.keys()))
    slopes = np.array([fits_50[c][0] for c in currents])
    intercepts = np.array([fits_50[c][1] for c in currents])

    slope_interp = interp1d(currents, slopes, kind='linear', fill_value='extrapolate')
    intercept_interp = interp1d(currents, intercepts, kind='linear', fill_value='extrapolate')

    slope = slope_interp(current)
    intercept = intercept_interp(current)

    return slope * deltaT + intercept

def predict_Q(deltaT, current, Th):
    Q_27 = predict_Q_27(deltaT, current)
    Q_50 = predict_Q_50(deltaT, current)

    Q_fin = Q_27 + (Th-27)/(50-27) * (Q_50 - Q_27)
    #print(f' Q_27:{Q_27}, Q_50:{Q_50}, Q_fin: {Q_fin}')
    return Q_fin


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
        self.couplage = 1
        pass

    def updateMatPerturbation(self, courant, matTemperature, T_ambiant):
        ###Trouver température côté chaud TEC
        T_h = np.sum(matTemperature * self.matElementBinaire)/self.nombreElement
        deltaT = T_h - T_ambiant

        if courant < 0:
            Q_tot = -1 * predict_Q(abs(deltaT), abs(courant), T_ambiant + abs(deltaT))
        else:
            Q_tot = predict_Q(abs(deltaT), courant, T_ambiant + abs(deltaT))
        
        if courant == 0:
            Q_tot = 0
#print(f"Q du Tec {Q_tot}, T_h {T_h}")
        self.matPerturbation = self.couplage* self.matElementBinaire * Q_tot / self.nombreElement
        
