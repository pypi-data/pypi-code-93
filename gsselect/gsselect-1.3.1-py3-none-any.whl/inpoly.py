def inpoly(xv, yv, xt, yt):
    """
    Originally in C by Bob Stein and Craig Yap
    http://www.visibone.com/inpoly/
    Converted to python by Bryan Miller
    2013.04.18
    Inputs:
      xv - x vertices of polygon (does not have to be 'closed', ie. last = first)
      yv - y vertices of polygon
      xt - x of test point(s)
      yt - y of test point(s)

    # 2016.06.25 - generalize to handle input arrays
    """

    nvert = len(xv)
    if nvert != len(yv) or nvert < 3:
        return -1

    l_xt = xt
    l_yt = yt

    try:
        npoints = len(l_xt)
    except Exception:
        l_xt = [l_xt]
        npoints = len(l_xt)
    try:
        npointsy = len(l_yt)
    except Exception:
        l_yt = [l_yt]
        npointsy = len(l_yt)

    if npoints != npointsy:
        return -1

    inside = [False for ii in range(npoints)]

    for jj in range(npoints):
        xold = xv[nvert-1]
        yold = yv[nvert-1]
        for i in range(nvert):
            xnew = xv[i]
            ynew = yv[i]
            if xnew > xold:
                x1 = xold
                x2 = xnew
                y1 = yold
                y2 = ynew
            else:
                x1 = xnew
                x2 = xold
                y1 = ynew
                y2 = yold
    #        /* edge "open" at one end */
            if (xnew < l_xt[jj]) == (l_xt[jj] <= xold) and (l_yt[jj]-y1)*(x2-x1) < ((y2-y1)*(l_xt[jj]-x1)):
                inside[jj] = not inside[jj]
            xold = xnew
            yold = ynew

    if npoints == 1:
        inside = inside[0]

    return inside
