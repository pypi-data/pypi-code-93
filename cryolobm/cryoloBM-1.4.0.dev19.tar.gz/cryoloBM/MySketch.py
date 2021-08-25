from matplotlib.patches import  Rectangle,Circle
from matplotlib import colors
from cryolo import utils
import numpy as np
from typing import Union,Tuple,Dict

class MySketch:
    def __init__(self, xy: Union[Tuple[float, float], None] = None, width: Union[int, None] = None,
                 height: Union[int, None] = None, is_tomo: bool = False, angle: float = 0.0,
                 est_size: Union[int, None] = None, confidence: Union[float, None] = None,
                 only_3D_visualization: bool = False, num_boxes: int = 1,
                 meta: Union[Dict[str, Tuple[float, float]], None] = None, z: Union[int, None] = None,
                 id: Union[int, None] = None, **kwargs) -> None:
        """
        :param xy: tuple representing the bottom and left rectangle coordinates. In according with matplotlib.patches.py class Rectangle
        :param width: of the rect
        :param height: of the rect
        :param is_tomo: True if the sketch will belong to a tomography
        :param angle: rotation in degrees anti-clockwise about *xy* (default is 0.0). In according with matplotlib.patches.py class Rectangle
        :param est_size: size estimated by crYOLO ( .cbox cases)
        :param confidence: confidence value estimated by crYOLO
        :param only_3D_visualization: If true this box is not a real box picked or detected by crYOLO but it is created in the 3D visualization feature
        :param num_boxes: number of boxes of the 3D particle (CBOX_3D file). in case of 2D it has value 1
        :param meta: meta data values of a Bbox instance
        :param z: slice in tomography
        :param id: particle id. I set it ONLY when i create the 3D visualization for detecting all the 2D part of the 'id 3D particle

        NB:
        in case of particle a rectangle will be a square --> box_size = height = width (hence radius = width/2)
        In case of filament it will be NOT A SQUARE, we have to decide how manage some stuff BUT the radius = It would be size perpendicular to the filament
        """

        # sketch id. The idea is to use the value for managing the pick and delete options in the 3D visualization
        self.id=id
        self.only_3D_visualization=only_3D_visualization
        self.meta = meta

        #it is the number of boxes of the 3D particle (CBOX_3D file). in case of 2D it has value 1
        # NB:
        #   the 'current_num_boxes_thresh' is set 0 for default, that means that in helper.check_if_should_be_visible
        #   2D particle (hence whose in the untraced_cbox files too) will be always visible when check 'box.num_boxes > num_boxes_thresh'
        self.num_boxes = num_boxes

        """
        Value used , together with meta["_filamentid"]for the filament tracking
        z = index tomo
        """
        self.z = z

        self.sketch_circle = MyCircle(xy=(xy[0]+width/2,xy[1]+width/2), radius=int(width / 2), is_tomo= is_tomo, est_size=est_size, confidence = confidence, **kwargs)
        self.sketch_rect = MyRectangle(xy=xy, width=width, height=height, is_tomo= is_tomo, angle=angle, est_size=est_size, confidence = confidence, **kwargs)

    def get_as_BBox(self, confidence:float = None, z:int = None)->utils.BoundBox:
        """
        convert the sketch in a cryolo Bounding box and return it
        :param confidence: confidence value. 1 if the bbox will pass to cryolo.grouping3d.do_tracing
        :param z: slice of the 3D tomo, None otherwise
        return: a BBox
        """

        """
            NB:
                The x,y of a BBox are the center of the box
                The x,y of a circle_sketch are the center of the circle
                The x,y of a rect_sketch are the bottom and left rectangle coordinates
        """
        w = self.get_width()

        #The bbox are rectangles hence i need the x,y values of the rectangles sketch.
        xy = self.get_xy(circle=False)

        #depth is always 1 even in the tomo because the box are on a slice, hence in 2D hence depth=1
        b= utils.BoundBox(x=xy[0], y=xy[1], w=w, h=w, c=confidence, classes=["particle"], z=z, depth=1)
        meta = (w,w)
        if self.meta is not None and "est_box_size" in self.meta:
            meta = self.meta["est_box_size"]
        b.meta = {"boxsize_estimated": meta}       # i need it in the 'cryolo.grouping3d.convert_traces_to_bounding_boxes'
        return b

    def resize(self, new_size:int)->None:
        confidence = self.get_confidence()
        is_tomo =self.get_is_tomo()
        color = self.getSketch().get_edgecolor()

        """est_size contained the estimated size of cryolo, when loaded from '.cbox' and should be never changed"""
        est_size = self.get_est_size()

        self.remove_instances()

        self.sketch_circle = MyCircle(xy=self.get_xy(circle=True), radius=new_size/2, is_tomo=is_tomo, est_size=est_size,
                                      confidence=confidence, linewidth=1, edgecolor=color, facecolor="none")

        xy = self.get_xy(circle=False)
        x = xy[0] + (self.get_width()-new_size)/2
        y = xy[1] + (self.get_width()-new_size)/2
        self.sketch_rect = MyRectangle(xy=(x,y), width=new_size, height=new_size, is_tomo=is_tomo,
                                       angle=self.get_angle(), est_size=est_size, confidence=confidence,
                                       linewidth=1, edgecolor=color, facecolor="none")
        self.createSketches()  # create the new instances

    def remove_instances(self)->None:
        """
        Remove the instances of the sketches
        """
        self.sketch_circle.remove_istance()
        self.sketch_rect.remove_istance()

    def createSketches(self)->None:
        """
        Create the instances of the sketches
        """
        self.getSketch(circle =True)
        self.getSketch(circle =False)

    def getSketch(self, circle:bool = False)->Union[Rectangle,Circle]:
        """
        Return an matplotlib instance of my sketch
        """
        if circle:
            return self.sketch_circle.getSketch()
        return self.sketch_rect.getSketch()

    def set_Sketches_visible(self, visible:bool =True)->None:
        self.getSketch(circle=True).set_visible(visible)
        self.getSketch(circle=False).set_visible(visible)

    def set_xy(self, xy:Tuple[float,float], circle:bool = False)->None:
        if circle:
            self.sketch_circle.xy = xy
        else:
            self.sketch_rect.xy = xy

    def set_radius(self, radius:int)->None:
        self.sketch_circle.radius = radius

    def set_width(self, width:int)->None:
        self.sketch_rect.width = width

    def set_height(self, height:int)->None:
        self.sketch_rect.set_height(new_height= height)

    def set_is_tomo(self, is_tomo:bool)->None:
        self.sketch_rect.is_tomo = is_tomo
        self.sketch_circle.is_tomo = is_tomo

    def set_angle(self, angle:float)->None:
        self.sketch_rect.angle = angle

    def set_est_size(self, est_size:int)->None:
        self.sketch_rect.est_size = est_size
        self.sketch_circle.est_size = est_size

    def set_confidence(self, confidence:float)->None:
        self.sketch_rect.confidence = confidence
        self.sketch_circle.confidence = confidence

    def set_colour(self, colour:str)->None:
        self.sketch_rect.kwargs["edgecolor"]=colour
        self.sketch_circle.kwargs["edgecolor"] = colour

    def get_xy(self, circle:bool = False)->Tuple[float,float]:
        if circle:
            return self.sketch_circle.xy
        return self.sketch_rect.xy

    def get_radius(self)->float:
        return self.sketch_circle.radius

    def get_width(self)->int:
        return self.sketch_rect.width

    def get_height(self)->int:
        return self.sketch_rect.height

    def get_is_tomo(self)->bool:
        return self.sketch_rect.is_tomo

    def get_angle(self)->float:
        return self.sketch_rect.angle

    def get_est_size(self, circle:bool = False)->int:
        if circle:
            return self.sketch_circle.est_size
        return self.sketch_rect.est_size

    def get_confidence(self)->float:
        return self.sketch_rect.confidence

    def get_color(self)->Tuple[float,float,float,float]:
        return self.getSketch().get_edgecolor()


class MyCircle:
    def __init__(self, xy: Union[Tuple[float, float], None], radius:float, is_tomo:bool = False, est_size:Union[int, None]=None, confidence:Union[float, None] = None, **kwargs)->None:
        self.confidence = confidence
        self.est_size = est_size
        self.is_tomo = is_tomo
        self.xy = xy
        self.radius = radius
        self.circleInstance = None
        self.kwargs = kwargs

    def getSketch(self)->Circle:
        if self.circleInstance is None:
            self.circleInstance = Circle(xy=self.xy, radius=self.radius, **self.kwargs)
        return self.circleInstance

    def remove_istance(self)->None:
        self.circleInstance = None


class MyRectangle:
    def __init__(self, xy: Union[Tuple[float, float], None], width:int, height:int, is_tomo:bool = False, angle:float=0.0, est_size:Union[int, None]=None, confidence:Union[float, None] = None, **kwargs)->None:
        self.confidence = confidence
        self.est_size = est_size
        self.is_tomo = is_tomo
        self.xy = xy
        self.width = width
        self.height = height
        self.angle = angle # degree
        self.rectInstance = None
        self.kwargs = kwargs

    def getSketch(self)->Rectangle:
        if self.rectInstance is None:
            self.rectInstance = Rectangle(self.xy, self.width, self.height, self.angle, **self.kwargs)
        return self.rectInstance

    def set_height(self, new_height):
        """Set the height. This method should update also xy when the height is changed"""
        angle = self.angle%180
        sign = 1
        if angle >= 90:
            sign = -1
        rad_angle = np.deg2rad(angle)

        x_fin = np.cos(rad_angle)
        y_fin = np.sin(rad_angle)
        help = x_fin
        x_fin = y_fin
        y_fin = -1*help
        orth_vect = np.array([x_fin,y_fin])

        old_xy = np.array(self.xy)

        new_xy = old_xy + sign*orth_vect*(new_height-self.height)/2

        self.xy = (new_xy[0],new_xy[1])
        self.height = new_height


    def remove_istance(self)->None:
        self.rectInstance = None