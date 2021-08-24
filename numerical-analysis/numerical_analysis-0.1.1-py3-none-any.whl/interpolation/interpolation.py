def linear_interpolation(p0, p1, x):
    a = (p1[1] - p0[1]) / (p1[0] - p0[0])
    b = p0[1] - a * p0[0]
    return a * x + b
