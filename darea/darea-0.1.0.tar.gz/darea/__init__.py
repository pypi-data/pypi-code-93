# made by atul
# made to find are of 2d and 3d shapes
# area circle

def circle(radius):
    return 22/7*(radius**2)

# area of triangle

def triangle(base,height):
    return 1/2*(base*height)

# area of square

def square(side):
    return side**2

# area of rectangle

def rectangle(length,width):
    return length*width

# area of parallelogram

def parallelogram(base,height):
    return base*height

# area of trapezium

''' a and b are the length of parallel sides '''
def trapezium(a,b,height):
    return 1/2*(a+b)*height

# area of ellipse

def ellipse(minoraxis,majoraxis):
    a=1/2*minoraxis
    b=1/2*majoraxis
    return 22/7*a*b
# area of rhombus
'''length of diagonal A,length of diagonal B'''

def rhombus(diagonalA,diagonalB):
    return 1/2*(diagonalA*diagonalB)


# area of 3d objects

'''area of cube'''
def cube(edge):
    return 6*(edge**2)

'''area of rectangularprism'''

def rectangularprism(length,width,height):
    return 2*(width*length+height*length+height*width)

'''area of cylinder'''
'''radius of circular base'''
def cylinder(radius,height):
    return 2*22/7*radius*(radius+height)

'''area of cone'''

'''radius of circular base'''
'''height is slant height'''

def cone(radius,S_height):
    return 22/7*radius*(radius+S_height)


'''area of sphare'''
'''radius is radius of sphere'''

def sphere(radius):
    return 4*22/7*(radius**2)


'''area of hemisphere '''

def hemisphere(radius):
    return 3*22/7*(radius**2)



'''perimeter of 2d objects'''

'''perimeter of parallelogram'''
'''base of parallelogram'''
'''height of parallelogram'''

def pariparllelogram(base,height):
    return 2*(base+height)

'''perimeter of triangle'''
'''a is side a'''
'''b is side b'''
'''c is side c'''

def peritriangle(a,b,c):
    return (a+b+c)

'''perimeter of rectangle'''

def perirectangle(length,width):
    return 2*(length+width)


'''perimeter of square'''

'''side is length of side'''
def perisquare(side):
    return 4*side

'''perimeter of trapezoid'''

'''a,b,c,d being sides of the trapezoid'''
def peritrapeziod(a,b,c,d):
    return a+b+c+d

'''perimeter of kite'''

'''a=length of the first pair'''
'''b=length of second pair'''
def perikite(a,b):
    return 2*a+2*b

'''perimeter of rhombus'''

def perirhombus(side):
    return 4*side

'''perimeter of hexagon'''

def perihexagon(side):
    return 6*side

'''perimeter of circle'''

def pericircle(radius):
    return 2*22/7*radius











