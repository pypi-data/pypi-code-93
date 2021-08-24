def bisection(f, x0, x1, error=1e-15):
    if f(x0) * f(x1) > 0:
        print("No root found.")
    else:
        while True:
            mid = 0.5 * (x0 + x1)
            if abs(f(mid)) < error:
                return mid
            elif f(x0) * f(mid) > 0:
                x0 = mid
            else:
                x1 = mid


def secant(f, x0, x1, error=1e-15):
    fx0 = f(x0)
    fx1 = f(x1)
    while abs(fx1) > error:
        x2 = (x0 * fx1 - x1 * fx0) / (fx1 - fx0)
        x0, x1 = x1, x2
        fx0, fx1 = fx1, f(x2)
    return x1


def newton_raphson(f, df_dx, x0, error=1e-15):
    while abs(f(x0)) > error:
        x0 -= f(x0) / df_dx(x0)
    return x0


def newton_raphson_2x2(f, g, fx, fy, gx, gy, x0, y0, error=1e-15):

    while abs(f(x0, y0)) > error or abs(g(x0, y0)) > error:
        jacobian = fx(x0, y0) * gy(x0, y0) - gx(x0, y0) * fy(x0, y0)
        x0 = x0 + (g(x0, y0) * fy(x0, y0) - f(x0, y0) * gy(x0, y0)) / jacobian
        y0 = y0 + (f(x0, y0) * gx(x0, y0) - g(x0, y0) * fx(x0, y0)) / jacobian

    return x0, y0


def newton_raphson_multiple_roots(f, df_dx, n, x0=2., error=1e-15):

    roots = []

    for i in range(n):
        xi = x0
        while abs(f(xi)) > error:
            xi -= f(xi) / (df_dx(xi) - f(xi) * sum([1 / (xi - root) for root in roots]))
        roots.append(xi)

    return sorted(roots)
