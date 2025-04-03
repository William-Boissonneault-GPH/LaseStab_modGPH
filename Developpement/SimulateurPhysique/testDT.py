rho = 900
cp = 2700
dx = 0.001
dy = 0.001
k = 180
dt = 1/363


constante = (k * dt) / (rho * cp * dx * dy)

dt_0_25 = (rho * cp * dx * dy) * 0.25 / k

print(constante)
print(dt_0_25)