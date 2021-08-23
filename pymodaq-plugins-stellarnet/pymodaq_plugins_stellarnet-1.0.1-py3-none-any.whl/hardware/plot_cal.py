import numpy as np
import pathlib
import matplotlib.pyplot as plt
# print(pathlib.Path().absolute())

import glob

path = glob.glob('../../hardware/*.CAL')

calibration = []
with open(path[0], 'r') as input:
    for line in input:
        if line[0].isdigit():
            calibration.append(np.fromstring(line, sep=' '))
calibration = np.asarray(calibration)
#
# line1 = 31
# f = np.loadtxt('MyCaL-C20111832-VIS-IC2.CAL', skiprows=line1, max_rows=2082-line1)
# plt.figure()
# plt.plot(f[:,0], f[:,1])
# plt.show()
#
