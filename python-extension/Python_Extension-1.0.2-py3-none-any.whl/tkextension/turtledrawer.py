from turtle import *

class Draw():
    def __init__(self, pen_attribute):
        self.pen = pen_attribute
    def create_triangle(self, distance, angle=90, fill=None):
        self.pen.setheading(angle)
        # Angle
        if fill != None:
            self.pen.fillcolor(fill)
            self.pen.begin_fill()
        self.pen.left(30)
        for x in range(0, 3):
            self.pen.right(120)
            self.pen.forward(distance)
        self.pen.left(30)
        if fill != None:
            self.pen.end_fill()
        # Draw
    def create_rectangle(self, distance_x, distance_y, angle=90, fill=None):
        self.pen.setheading(angle)
        # Angle
        if fill != None:
            self.pen.fillcolor(fill)
            self.pen.begin_fill()
        for x in range(0, 2):
            self.pen.forward(distance_x)
            self.pen.right(90)
            self.pen.forward(distance_y)
            self.pen.right(90)
        if fill != None:
            self.pen.end_fill()
        # Draw
    def create_pentagon(self, distance, angle=90, fill=None):
        self.pen.setheading(angle)
        # Angle
        if fill != None:
            self.pen.fillcolor(fill)
            self.pen.begin_fill()
        for x in range(0, 5):
            self.pen.forward(distance)
            self.pen.right(72)
        if fill != None:
            self.pen.end_fill()
        # Draw
    def create_polygon(self, side, distance, angle=90, fill=None):
        internal_angle_sum = (side - 2) * 180
        # Value
        self.pen.setheading(angle)
        # Angle
        if fill != None:
            self.pen.fillcolor(fill)
            self.pen.begin_fill()
        for x in range(0, side):
            self.pen.forward(distance)
            self.pen.right(180 - internal_angle_sum / side)
        if fill != None:
            self.pen.end_fill()
        # Draw
