from cryolo import utils
import numpy as np
from cryoloBM import MySketch,helper_GUI,helper
from typing import Union,List,Dict,Tuple

class picked_filament:
    """
    A picked filament
    In the rectangular visualization we lose the left half of the first square box (the one on the first point of the filament)
    """
    def __init__(self, box_size:int, is_tomo:bool=True, fil_id=None)->None:
        """
        :param box_size:
        :param is_tomo:
        :param fil_id:
        """
        self.id = fil_id

        self.boxsize = box_size
        self.begin_fil = list()        # event position obj ... the first click (got via on_click)
        self.end_fil = list()          # event position obj ... the las click (got via on_release or on_move)

        self.filament=utils.Filament(list())        # crYOLO filament object

        self.is_tomo=is_tomo

        self.angle = None # In rads
        self.offset = None          # offset to center the filament (i.e.: for default we pick via mouse on the left corner but we need to pick on the center of the filament)
        self.rect_vect = None       # versor of the rectangle
        self.orth_vect = None       # versor orthogonal to self.rect_vect

        # distance between the first and last sketch
        self.width = box_size
        self.height = box_size

    def create_from_rect(self,rect:MySketch.MySketch)->None:
        """
        create a picked filament object starting from a MySketche obj
        :param rect: MySketch obj
        """
        rad_angle = np.deg2rad(rect.get_angle())
        x, y = rect.get_xy(circle=False)
        x -= self.boxsize / 2
        y -= self.boxsize / 2
        x_fin = x + rect.get_width()* np.cos(rad_angle)
        y_fin = y + rect.get_width()* np.sin(rad_angle)
        x_in = x + 1 * np.cos(rad_angle)
        y_in = y + 1 * np.sin(rad_angle)
        self.begin_fil=[x_in,y_in]
        self.end_fil = [x_fin, y_fin]
        self.set_line_params()

    def set_first(self,event:helper_GUI.plt_qtbackend)->None:
        """
        It sets the first element
        :param event: click event via 'onclick
        """
        self.begin_fil = [event.xdata,event.ydata]
        self.end_fil =  [event.xdata,event.ydata]

    def append_sketch(self,sketch:MySketch.MySketch)->None:
        """
        Append sketch to le list
        :param sketch: MySketch obj
        """
        self.filament.add_box(sketch)

    def reset_sketches(self)->None:
        self.filament.boxes = list()


    def set_line_params(self)->None:
        """
        Calculate params of the line got from  'begin_fil' and 'end_fil'
        """
        self.rect_vect = np.array(self.end_fil) - np.array(self.begin_fil)
        self.width = np.linalg.norm(self.rect_vect)
        self.angle = np.rad2deg(np.arctan2(self.rect_vect[1], self.rect_vect[0]))

        # calculate offset to filament start. this has the effect that filaments can picked centerd.
        self.orth_vect = np.array(self.rect_vect)/self.width # normalized vector
        help_value = self.orth_vect[0]
        self.orth_vect[0] = self.orth_vect[1]
        self.orth_vect[1] = -1*help_value  #now it orthogonal to rect_vect
        self.offset = self.orth_vect #* self.height/2 # offset for drawing.


    def get_R(self)->np.array:
        """
        Returns the rotation matrix of the rectangle as np array
        """
        theta = -np.radians(self.angle)
        c, s = np.cos(theta), np.sin(theta)
        return np.array(((c, -s), (s, c)))


    def get_coordinate_rect(self)->np.array:
        """
        returns the real coordinate of the rectangles as np array
        -) each row is a point x,y.
        -) first row =bottom left corner
        -) second row = bottom right corner
        -) third row = top left corner
        -) fourth row = top right corner
        """
        norm_v_ort = self.orth_vect/np.linalg.norm(self.orth_vect)
        scale_v_ort = norm_v_ort*self.height

        corner_0 = np.array(self.begin_fil)-np.array(self.offset * self.height/2)
        corner_1 = corner_0 + scale_v_ort
        corner_2 = corner_0 + self.rect_vect
        corner_3 = corner_2 + scale_v_ort
        return np.vstack((corner_0, corner_1, corner_2, corner_3))


    def  get_rotated_coordinate_rect(self)->np.array:
        """
        Returns the coordinate of the rect on the x axis
        """
        return self.get_R()@self.get_coordinate_rect().T

    def fill_and_get_sketches(self, box_distance:int=1, as_bbox:bool=False, z:int=None, color ='r')->Union[List[utils.BoundBox],List[MySketch.MySketch]]:
        """
        It is used for saving data on file
        Create a square box every 'box_distance' point on the central line of the filament
        :param box_distance: sampling step
        :param as_bbox: convert the sketches in cryolo.bbox
        :param z:   in case of filament in a tomo I need to know the slice
        :param color: edgecolor
        """
        self.fill_sketches(box_distance=box_distance,as_bbox=as_bbox, z=z, color=color)
        return self.get_sketches()

    def fill_sketches(self, box_distance:int = 1, as_bbox:bool = False, z:int=None, color ='r')->None:
        """
        It is used for saving data on file or fill the box_dictionary.particle_dictionary dict for speed up the realtime visualization
        Create a square box every 'box_distance' point on the central line of the filament
        :param box_distance: sampling step
        :param as_bbox: convert the sketches in cryolo.bbox
        :param z:   in case of filament in a tomo I need to know the slice
        :param color: edgecolor
        """
        self.set_line_params()
        self.reset_sketches()
        nboxes = int(self.width//box_distance)

        begin_sketch = MySketch.MySketch(xy=(self.begin_fil[0] - self.height / 2 , self.begin_fil[1] - self.height / 2 ), width=self.boxsize, height=self.boxsize,
                                         is_tomo=self.is_tomo, angle=self.angle, est_size=self.boxsize, confidence=1,
                                         only_3D_visualization=False, num_boxes=1, meta=None, z=z,
                                         linewidth=1, edgecolor=color, facecolor="none")
        end_sketch = MySketch.MySketch(xy=(self.end_fil[0] - self.height / 2 , self.end_fil[1] - self.height / 2 ), width=self.boxsize, height=self.boxsize,
                                       is_tomo=self.is_tomo, angle=self.angle, est_size=self.boxsize, confidence=1,
                                       only_3D_visualization=False, num_boxes=1, meta=None, z=z,
                                       linewidth=1, edgecolor=color, facecolor="none")
        self.filament.boxes = utils.getEquidistantBoxes(begin_sketch.get_as_BBox(confidence=1, z=z),end_sketch.get_as_BBox(confidence=1, z=z),nboxes)
        if as_bbox is False:
            self.filament.boxes = helper.convert_list_bbox_to_sketch(self.filament.boxes,out_dict=False, fil_id =self.id,col=color)

    def get_sketches(self,box_distance:int = 1, as_bbox:bool = False, z:int=None)->Union[List[utils.BoundBox],List[MySketch.MySketch]]:
        """
        It is used for saving data on file or fill the box_dictionary.particle_dictionary dict for speed up the realtime visualization
        Create a square box every 'box_distance' point on the central line of the filament
        :param box_distance: sampling step
        :param as_bbox: convert the sketches in cryolo.bbox
        :param z:   in case of filament in a tomo I need to know the slice
        """
        if not self.filament.boxes:
            return self.fill_and_get_sketches(box_distance=box_distance,as_bbox=as_bbox,z=z)
        return self.filament.boxes


    def get_rect_sketch(self,color='r',sketch_id=None)->MySketch.MySketch:
        """
        :param color: edgecolor
        :param sketch_id: id, used only in resize step
        """
        self.set_line_params()

        # for centering on x i have to calculate, geometrically, it. It does not deserve calulate it
        return  MySketch.MySketch(xy=(self.begin_fil[0] + self.offset[0] * self.height/2, self.begin_fil[1] + self.offset[1]* self.height/2), width=self.width, height=self.height,
                                  is_tomo=self.is_tomo, angle=self.angle, est_size=self.boxsize, confidence=1,
                                  only_3D_visualization=False, num_boxes=1, meta=None, z=None,id=sketch_id,
                                  linewidth=1, edgecolor=color, facecolor="none")
