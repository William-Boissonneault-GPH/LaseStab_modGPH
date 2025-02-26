import numpy as np
import scipy.signal as signal
import scipy.optimize as opt

import matplotlib.pyplot as plt
import csv


# Define Transfer Function
num_U1 = np.array([8.93])
den_U1 = np.array([102.5 , 1])
GU1 = signal.TransferFunction(num_U1 , den_U1)
print ('T1(s) =', GU1)
# Step Response
t, y1 = signal.step(GU1)
y1 *= 0.2

num_13 = np.array([0.6587])
den_13 = np.array([394.68, 48, 1])
G13 = signal.TransferFunction(num_13 , den_13)

###T3 basé sur T1
num_combined = np.polymul(num_U1, num_13)
den_combined = np.polymul(den_U1, den_13)
GU_13 = signal.TransferFunction(num_combined, den_combined)




num_U2 = np.array([6.97])
den_U2 = np.array([536.94, 137.91, 1])

GU2 = signal.TransferFunction(num_U2 , den_U2)
print ('T2(s) =', GU2)
# Step Response
t, y2 = signal.step(GU2)
y2 *= 0.2

num_23 = np.array([0.8532])
den_23 = np.array([19.469, 1])
G23 = signal.TransferFunction(num_23 , den_23)

###T3 basé sur T1
num_combined = np.polymul(num_U2, num_23)
den_combined = np.polymul(den_U2, den_23)
GU_23 = signal.TransferFunction(num_combined, den_combined)






t, y31 = signal.step(GU_13)
y31 *= 0.2
t, y32 = signal.step(GU_23)
y32 *= 0.2




# Load Experimental Data from CSV
csv_filename = "model_14fev_600.0_800.0.csv"  # Change this to your actual CSV filename
t_csv = []
y1_csv = []
y2_csv = []
y3_csv = []

with open(csv_filename, newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header if there is one
    for row in reader:
        t_csv.append(float(row[0]))  # First column: time
        y1_csv.append(float(row[1]))  # Second column: response
        y2_csv.append(float(row[2]))  # Second column: response
        y3_csv.append(float(row[3]))  # Second column: response

half_index = len(t_csv) // 2
t_csv = np.array(t_csv[half_index:]) - 1000
y1_csv = np.array(y1_csv[half_index:]) - 28.99
y2_csv = np.array(y2_csv[half_index:]) - 27.86
y3_csv = np.array(y3_csv[half_index:]) - 27.29




def error_function(a):
    b = 1 - a
    y_est = a * y31 + b * y32  # Compute estimated response
    y_sim_interpolated = np.interp(t_csv, t, y_est)  # Interpolate at actual time points
    squared_errors = (y3_csv - y_sim_interpolated) ** 2  # Compute squared errors
    return np.sum(squared_errors)  # Return the sum of squared errors


result = opt.minimize(error_function, x0=0.5, bounds=[(0, 1)])

optimal_a = result.x[0]
optimal_b = 1 - optimal_a

print(optimal_a, optimal_b)

# Estimate uncertainty using the inverse Hessian
if "hess_inv" in result:
    hessian_inv = result.hess_inv.todense() if hasattr(result.hess_inv, "todense") else result.hess_inv
    std_a = np.sqrt(hessian_inv[0, 0])  # Standard deviation of 'a'
else:
    std_a = np.nan  # If Hessian is not available

y_est = optimal_a * y31 + optimal_b * y32  # Compute estimated response

y_sim_interpolated = np.interp(t_csv, t, y_est)
mse = np.mean((y_sim_interpolated - y3_csv)**2)
rmse = np.sqrt(mse)
print(f"rmse : {rmse}")


plt.figure(figsize=(7,4))
plt.rcParams.update({"font.size": 8})

# Plotting
plt.scatter(t, y1, label="T1 fonction transfert", s=2)
plt.scatter(t, y2, label="T2 fonction transfert", s=2)
plt.scatter(t, y31, label="T3 basé sur T1", s=2)
plt.scatter(t, y32, label="T3 basé sur T2", s=2)

plt.plot(t_csv, y1_csv, label="Données simulées T1")
plt.plot(t_csv, y2_csv, label="Données simulées T2")
plt.plot(t_csv, y3_csv, label="Données simulées T3")

plt.scatter(t, y_est, label="T3 estimé \n α : 0.098 \n β : 0.902",  marker='^', s=8)

plt.xlabel("temps [sec]")
plt.ylabel("ΔT [°C]")
plt.grid()
plt.legend()

plt.savefig("estimateurDeTemperature.pdf")
plt.show()



