from collections import namedtuple


class Frame_Object():

    def __init__(self, object_record):
        self.record = dict(object_record)
        self.Rectangle_Tuple = namedtuple('Rectangle', 'xmin ymin xmax ymax')
        self.Rectangle = self.rectangle_from_record(object_record)
    
    def rectangle_from_record(self, object_record):
        return self.Rectangle_Tuple(
            object_record["object_x"],
            object_record["object_y"],
            object_record["object_x"] + object_record["object_w"],
            object_record["object_y"] + object_record["object_h"]
        )
    
    # Methods related only to this object
    
    def area(self):
        """Calculate the area of the object in pixels"""
        a = self.Rectangle
        dx = a.xmax - a.xmin
        dy = a.ymax - a.ymin
        return dx*dy
    
    # Methods for comparing this object to others
    
    def contains(self, frame_object_b):
        """Check whether this object encompasses another object"""
        r1 = self.Rectangle
        r2 = frame_object_b.Rectangle
        return r1.xmin < r2.xmin < r2.xmax < r1.xmax and r1.ymin < r2.ymin < r2.ymax < r1.ymax
    
    def area_intersection(self, frame_object_b):
        a = self.Rectangle
        b = frame_object_b.Rectangle
        """Calculates area (in pixels) of intersection of two objects"""
        dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
        dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
        if (dx>=0) and (dy>=0):
            return dx*dy
        else:
            return 0
    
    def intersection_percentage(self, frame_object_b):
        a = self.Rectangle
        b = frame_object_b.Rectangle
        area_a = self.area()
        overlap = self.area_intersection(frame_object_b)
        return overlap / area_a
