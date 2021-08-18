def ori_to_resliced(v):
    # rx = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
    ry = [[0, 0, 1], [0, 1, 0], [-1, 0, 0]]
    rz = [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
    # 1º rotation around y
    newV1 = np.matmul(ry, v)
    # 2º rotation around z
    newV2 = np.matmul(rz, newV1)

    print(v, "--->", newV1, "--->", newV2)
    return newV2

def resliced_to_polar(v, center):
    # transform origin
    newV = np.array(v) - np.array(center)

    rho = np.sqrt(newV[0]**2 + newV[1]**2)
    theta = np.arctan(newV[1]/newV[0])
    return rho, theta, newv[2]
