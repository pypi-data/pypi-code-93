VectorError = RuntimeError
class LinearTransformations2D(object):
    def __init__(self,ix,iy,jx,jy):
        self.ix,self.jx,self.iy,self.jy = ix,jx,iy,jy
class Vector2D(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __mul__(self, other, mul_type="Dot"):
        if isinstance(other,LinearTransformations2D):
            return

    def __repr__(self):
        return f"┌{self.x}┐\n│{' '*(len(str(max(self.x, self.y))))}│\n└{self.y}┘"

    def __add__(self, other):
        if isinstance(other,Vector2D):
            return Vector2D(self.x + other.x,self.y + other.y)
        else:
            raise VectorError

print(Vector2D(1,2)+Vector2D(3,4))