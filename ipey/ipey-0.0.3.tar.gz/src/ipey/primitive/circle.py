from ipey.primitive.ellipse import Ellipse

class Circle(Ellipse):

    def __init__(self, p, r, prototype=None):
        super().__init__(p, (r,0), (0,r), prototype=prototype)


    # def draw(self):
    #     elem = ET.Element('path')
    #     self.addProperties(elem)

    #     elem.text = f"{self.r} 0 0 {self.r} {self.p[0]} {self.p[1]} e"

    #     return elem

