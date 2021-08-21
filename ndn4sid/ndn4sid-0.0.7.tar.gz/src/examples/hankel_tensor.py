import numpy as np
from ndn4sid import linearalgebra
from ndn4sid import systems


# Define an example system
A = np.diag([1,2,3,4])
B = np.diag([5,6,7,8])
x0 = np.array([1,1,1,1])
C = np.array([1,1,1,1])

my_system = systems.SS([A,B],C,x0,suppress_warnings=True)

# Define the size of the simulated data and the order of the hankelization.
data_size = [10,8]
hankel_order = [5,4]

# Simulate the system.
y = systems.simulate_SS(my_system,data_size)

# Calculate the Hankel tensor.
H = systems.get_hankel_tensor(y,hankel_order)
