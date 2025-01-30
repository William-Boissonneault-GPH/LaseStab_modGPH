###Data points from spec sheet

import numpy as np

# Sample data (replace with your actual data)
# Columns: DeltaT, Current, Q
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

# Extracting DeltaT, Current, and Q
DeltaT = data[:, 0]
Current = data[:, 1]
Q = data[:, 2]

# Combine DeltaT and Current into a feature matrix with an intercept term
X = np.column_stack((np.ones(len(DeltaT)), DeltaT, Current))

# Solve for coefficients using the normal equation: theta = (X^T X)^(-1) X^T y
theta = np.linalg.inv(X.T @ X) @ X.T @ Q

# Coefficients
intercept = theta[0]
coef_DeltaT = theta[1]
coef_Current = theta[2]

print("Model Intercept:", intercept)
print("Coefficient for DeltaT:", coef_DeltaT)
print("Coefficient for Current:", coef_Current)

# Predict Q for new data
new_data = np.array([[0, 6], [28, 4.5]])  # New DeltaT and Current values
new_X = np.column_stack((np.ones(len(new_data)), new_data[:, 0], new_data[:, 1]))
predicted_Q = new_X @ theta

print("Predicted Q values:", predicted_Q)


