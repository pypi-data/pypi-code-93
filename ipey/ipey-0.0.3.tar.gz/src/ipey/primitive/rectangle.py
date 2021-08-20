from ipey.primitive.polygon import Polygon


class Rectangle(Polygon):

    def __init__(self, p, w, h, prototype = None):
        
        points = []
        pp = (p[0], p[1] - h)
        ppp = (pp[0] + w, pp[1])
        pppp = (ppp[0], p[1])

        points.append(p)
        points.append(pp)
        points.append(ppp)
        points.append(pppp)

        super().__init__(points, prototype=prototype)
        
        

        



