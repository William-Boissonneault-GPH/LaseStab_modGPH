import numpy as np

dimensions = (60, 125)

grosseurElementFinie = (13,23)

arr = np.array(
    [
        [1,2,3],
        [1,2,3],
        [1,2,3],
        [1,2,3],
    ]
)

arr2 = np.array(
    [
        [110,2,3],
        [1,2,3],
        [1,2,3],
        [1,2,3],
    ]
)

y_amount = int(round(dimensions[1]/grosseurElementFinie[1]))
x_amount = int(round(dimensions[0]/grosseurElementFinie[0]))
newGrosseurElementFinie = (dimensions[0]/x_amount, dimensions[1]/y_amount)

matTemperatureInitiale = np.full((y_amount, x_amount), 25)

print(matTemperatureInitiale)
print(newGrosseurElementFinie)




def hi(*matrices):

    print(matrices[0])

hi([arr,arr2])


arr3 = np.array(
    [
        [1,2,3],
        [4,5,6],
        [7,8,9],
    ]
)
print(arr3[1:-1,1:-1])