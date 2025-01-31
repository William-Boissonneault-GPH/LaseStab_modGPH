import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

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

# Separate columns
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

print(predict_Q(12, 2.7))