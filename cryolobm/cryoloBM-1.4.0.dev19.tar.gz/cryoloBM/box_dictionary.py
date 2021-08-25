"""
implementation of the Box_dictionary class and its helper function
"""
from typing import Union,List,Dict,Tuple
from cryoloBM import constants,helper,MySketch,helper_filament
from cryolo import utils    # for type hinting purpose
from os import path
from math import sqrt as math_sqrt

class Box_dictionary:
    def __init__(self, type_case: constants.Type_case, onlyfiles: List[str], tot_slices: int = None  ) -> None:
        """
        It contains the sketches present in each image, SPA case, or slice, TOMO and TOMO_FOLDER cases.
        It is a dict of dicts. With the following structure:

            SPA case                    --> dict of list
        k1: micrograph's filename
        v1= list of sketches in the micrograph

            TOMO or TOMO_FOLDER cases   --> dict of dict of list
        k1: tomo filename
        v1= dict
            k2: number of slice of the 'k1' filename
            d2: list of sketches in the slice

        The functions 'get_sketches' and 'add_sketch' get and add sketches in the correct location

        :param type_case: Identify if the loaded case is SPA, single tomo or folder of tomo (Constant.Type_case)
        :param onlyfiles: list of the files present in the folder, single file (into a var list)in case of TOMO
        :param tot_slices: number of slices present in the TOMO. Only constants.Type_case.TOMO case
        """

        self.counter = 1    # used to assign an unique id to all the particles/filament present the dict. (it is a global counter and it counts in the tomo folder too)

        self.type_case = constants.Type_case.NOT_LOADED.value
        self.is_3D = False # True if the 3D visualization is available only in tomo cases after loading cbox

        self.is_cbox_untraced = False
        self.has_filament = False

        self.list_purefiles = list()    # list of file without extension

        # flag to detect the correct dictionary in case of filament. False select list of particles
        self.fil_start_end_vis = True

        # The following dictionary are linked by keys
        # When we change the image the boxes present in the old image will be deleted and the boxes present in the new one will be drawn
        # When we plot the new boxes we check if the boxsize or the visualization is changed from the last time they are drawn
        #   in case we transform them in real time, we update them in the particle_dictionary and the values in the other 2 dicts

        # the following dicts contain the boxes present in the images. The dict we ll use in the run depends to the context
        self.particle_dictionary = dict()       # 2D particle, it could represent the 'segmented' visualization of the filament case
        self.particle3D_dictionary = dict()     # 3D representation of 2D particle (referred to box_dict_traced in case of tracing) it could represent the 'segmented' visualization of the filament case
        self.box_dict_traced=dict()             # 2D representation of 2D untraced cbox sketches after running the tracing

        self.filament_dictionary = dict()       # 2D filament in rect_start_end visualization
        self.filament3D_dictionary = dict()     # 3D representation of 2D filament (referred to box_dict_traced in case of tracing)

        # it contains the boxsize of all the groups of sketches present in avery image and saved in particle_dictionary or filament dict
        # in filament case is referred to the base of the rect
        self.boxsize_dictionary = dict()
        # it contains the visualization of all the groups of sketches present in avery image and saved in particle_dictionary or filament dict
        self.visualization_dictionary = dict()
        # it contains the box distance between 2 sketches, which belong to a filament, only filament case
        self.box_distance_dictionary = dict()

        self.init(type_case=type_case,onlyfiles=onlyfiles, tot_slices=tot_slices)

    def init(self,type_case: constants.Type_case, onlyfiles: List[str], tot_slices: int) -> None:
        """
        It init the vars, we need it because after resetting we have to build the structure of the dicts from scratch.
        If we was working in TOMO and then we switch to TOMO_FOLDER we cannot reuse the old structure.
        Hence in the code we call clean and then in case we open a new folder/image we will call it manually again
        :param type_case: Identify if the loaded case is SPA, single tomo or folder of tomo (Constant.Type_case)
        :param onlyfiles: list of the files present in the folder, single file (into a var list)in case of TOMO
        :param tot_slices: number of slices present in the TOMO. Only constants.Type_case.TOMO case
        """
        self.list_purefiles = [path.splitext(path.basename(f))[0] for f in onlyfiles]
        self.type_case = type_case

        if self.type_case == constants.Type_case.TOMO.value:
            f=path.splitext(path.basename(onlyfiles[0]))[0]
            self.particle_dictionary.update({f: dict()})
            self.particle3D_dictionary.update({f: dict()})
            self.box_dict_traced.update({f: dict()})
            self.boxsize_dictionary.update({f: -1})
            self.visualization_dictionary.update({f: dict()})
            self.box_distance_dictionary.update({f: dict()})
            self.filament_dictionary.update({f: dict()})
            self.filament3D_dictionary.update({f: dict()})
            self.init_single_tomo(tomo_name=f, tot_slices=tot_slices)
        else:
            self._init_dict_folder_case(onlyfiles=onlyfiles)


    def _init_dict_folder_case(self, onlyfiles:List[str])-> None:
        for f in onlyfiles:
            self.particle_dictionary.update({path.splitext(path.basename(f))[0]: list() if self.type_case == constants.Type_case.SPA.value else dict()})
            self.particle3D_dictionary.update({path.splitext(path.basename(f))[0]: list() if self.type_case == constants.Type_case.SPA.value else dict()})
            self.boxsize_dictionary.update({path.splitext(path.basename(f))[0]: list() if self.type_case == constants.Type_case.SPA.value else dict()})
            self.visualization_dictionary.update({path.splitext(path.basename(f))[0]:  None  if self.type_case == constants.Type_case.SPA.value else dict()})
            self.box_distance_dictionary.update({path.splitext(path.basename(f))[0]: None if self.type_case == constants.Type_case.SPA.value else dict()})
            self.filament_dictionary.update({path.splitext(path.basename(f))[0]: list() if self.type_case == constants.Type_case.SPA.value else dict()})
            self.filament3D_dictionary.update({path.splitext(path.basename(f))[0]: list() if self.type_case == constants.Type_case.SPA.value else dict()})
            if self.type_case != constants.Type_case.SPA.value:
                self.box_dict_traced.update({path.splitext(path.basename(f))[0]:  dict()})

    def init_single_tomo(self, tomo_name:str, tot_slices:int)-> None:
        """
        Init the dict of a generic tomo
        :param tomo_name: filenae tomo to init
        :param tot_slices: number of slices present in the TOMO.
        """
        if not self.particle_dictionary.get(tomo_name,dict()):
            self.particle_dictionary[tomo_name] = {sl: list() for sl in range(tot_slices)}
            self.particle3D_dictionary[tomo_name] = {sl: list() for sl in range(tot_slices)}
            self.box_dict_traced[tomo_name] = {sl: list() for sl in range(tot_slices)}
            self.boxsize_dictionary[tomo_name] = {sl: -1 for sl in range(tot_slices)}
            self.visualization_dictionary[tomo_name] = {sl: None for sl in range(tot_slices)}
            self.box_distance_dictionary[tomo_name] = {sl: None for sl in range(tot_slices)}
            self.filament_dictionary[tomo_name] = {sl: list() for sl in range(tot_slices)}
            self.filament3D_dictionary[tomo_name] = {sl: list() for sl in range(tot_slices)}

    def get_sketches(self,f:str, n:int=None, is_3D:bool = False, is_tracing:bool = False) ->List[MySketch.MySketch]:
        """
        returns the sketches present in the given file 'f' at the given slice 'n' (in TOMO cases)
        :param f: filename
        :param n: number of slice
        :param is_3D if True return the 3D dictionary. Always False for updating counter purposes
        :param is_tracing: if True it search into the tracing dict (box_dict_traced) otherwise (particle_dictionary)
        :return: list of Mysketch obj present in the given file 'f' at the given slice 'n'
        """
        if self.has_filament and self.fil_start_end_vis:
            dict_2D = self.filament_dictionary
            dict_3D = self.filament3D_dictionary
        else:
            dict_2D = self.box_dict_traced if is_tracing else self.particle_dictionary
            dict_3D = self.particle3D_dictionary
        if self.type_case == constants.Type_case.SPA.value:
            return dict_2D.get(f,list())
        return dict_3D.get(f,list()).get(n,list()) if is_3D else dict_2D.get(f,list()).get(n,list())

    def get_particle_dictionary_as_bbox(self,f:str)->Dict[int,List[utils.BoundBox]]:
        """
        convert the tomo dict of 'f' into a dict of bboxes. it is used only i the tracing via cryolo.grouping3d.do_tracing
        """
        d=dict()
        for n, sketches in self.particle_dictionary[f].items():
            d.update({n: [s.get_as_BBox(confidence=s.get_confidence(),z=n) for s in sketches]})
        return d

    def resize_3D(self,new_boxsize:int, use_estimated_size:bool = False)-> None:
        """
        Reset the particle3D_dictionary, copy the value in particle_dictionary, resize them and create3D for each particle
        In the process it resizes the whole 2D dict too
        :param new_boxsize: the new boxsize value
        :param use_estimated_size: if True uses the estimated value present in the box (Mysketch obj)
        """
        for f in self.particle_dictionary.keys():
            # reset the 3D dict
            for n in self.particle_dictionary[f].keys():
                self.boxsize_dictionary[f][n] =new_boxsize
                self.particle3D_dictionary[f][n] =list()
            # fill the 3D dict and resize the 2D dict
            for n,sketches in self.particle_dictionary[f].items():
                for sketch in sketches:
                    sketch.resize(sketch.get_est_size(circle=False) if use_estimated_size else new_boxsize)	        # resize the sketch of particle_dictionary
                    self.create_3D(sketch,f,n, is_start_end_filament = False)

    def _resize_all_filament(self, new_boxsize:int, f:str, n:int=None)->List[MySketch.MySketch]:
        """
        Resize and return the sketches in the present in the given file 'f'
        ONLY 2D cases
        :param new_boxsize: the new boxsize value
        :param f: filename
        :param n: number of slice. The untraced cbox are 2D but on Tomo
        :return: list of resized Mysketch obj present in the given file 'f'
        """
        starting_vis = self.has_same_visualization(visualization=constants.Visualization_cb.RECT_FILAMENT_START_END.value,f=f,n=n)

        # set temporarily to True for getting via 'get_sketches' the start_end rect
        self.fil_start_end_vis = True
        fil_start_end = self.get_sketches(f=f, n=n, is_3D=self.is_3D, is_tracing=False)
        self.fil_start_end_vis = False
        fil_segmented = self.get_sketches(f=f, n=n, is_3D=self.is_3D, is_tracing=False)
        self.fil_start_end_vis = starting_vis

        # vars to track colour and list of sketches of a single filament
        listed_sketches = {fil.id: list() for fil in fil_start_end}
        colour_sketches = {fil.id: fil.get_color() for fil in fil_start_end}

        # resize the segmented visualization
        for box in fil_segmented:
            box.resize(new_size=new_boxsize)
            listed_sketches[box.id].append(box.get_xy(circle=False))

        # resize, recrating and overwriting on self.dictionary the start-end visualization
        fil_start_end = list()
        for fil_id, xy in listed_sketches.items():
            fil = helper_filament.picked_filament(box_size=new_boxsize, is_tomo=self.type_case != constants.Type_case.SPA.value, fil_id=fil_id)
            fil.begin_fil = listed_sketches[fil_id][0][0] +new_boxsize/2, listed_sketches[fil_id][0][1] +new_boxsize/2
            fil.end_fil = listed_sketches[fil_id][-1][0] +new_boxsize/2,  listed_sketches[fil_id][-1][1] +new_boxsize/2
            fil_start_end.append(fil.get_rect_sketch(color=colour_sketches[fil_id], sketch_id=fil_id))

        # i have to set the new filament in start-end visualization otherwise they ll be not saved in filemant2D[the current image]
        self.fil_start_end_vis = True
        self._set_sketches(list_sketches=fil_start_end, f=f, n=n)
        self.fil_start_end_vis = starting_vis
        return fil_start_end if starting_vis else fil_segmented


    def resized_and_get_sketches(self, new_boxsize:int, f:str, n:int=None, use_estimated_size:bool = False)->List[MySketch.MySketch]:
        """
        Resize and return the sketches in the present in the given file 'f'
        ONLY 2D cases
        :param new_boxsize: the new boxsize value
        :param f: filename
        :param n: number of slice. The untraced cbox are 2D but on Tomo
        :param use_estimated_size: if True uses the estimated value present in the box (Mysketch obj)
        :return: list of resized Mysketch obj present in the given file 'f'
        """
        if self.has_filament:
            boxes=self._resize_all_filament(new_boxsize=new_boxsize, f=f, n=n)
        else:
            boxes = self.get_sketches(f=f,n=n, is_3D=self.is_3D,  is_tracing = False)
            for box in boxes:
                box_new_size = box.get_est_size(circle=False) if use_estimated_size else new_boxsize
                box.resize(new_size=box_new_size)

        # update the boxsize dictionary, i force it to be None in order to recalculate the boxes next time
        self.update_boxsize_dictionary(new_boxsize=None if use_estimated_size else new_boxsize, f=f, n=n)
        return boxes

    def _set_sketches(self,list_sketches: List[MySketch.MySketch],f:str, n:int=None)->None:
        """
        After changing the boxes inthe list, if it was done via for box in boxes i have to overwrite the list
        ONLY 2D cases
        :param list_sketches: the new boxsize value
        :param f: filename
        :param n: number of slice. The untraced cbox are 2D but on Tomo
        """

        dict_2D = self.filament_dictionary if self.has_filament and self.fil_start_end_vis else self.particle_dictionary
        if self.type_case == constants.Type_case.SPA.value:
            dict_2D[f] = list_sketches
        else:
            dict_2D[f][n] = list_sketches

    def change_box_distance_all(self, new_box_distance:int)->None:
        """
        change the distance between the sketches in all the dict, it is used before saving on file
        :param new_box_distance: the new distance between 2 sketches in a filament
        """
        starting_vis = self.fil_start_end_vis
        self.fil_start_end_vis = False
        for k1 in self.particle_dictionary.keys():
            if self.type_case == constants.Type_case.SPA.value:
                self.particle_dictionary[k1] = self.change_box_distance(new_box_distance=new_box_distance, f=k1, n=None, is_tracing=False)
            else:
                for k2 in self.particle_dictionary[k1].keys():
                    self.particle_dictionary[k1][k2] = self.change_box_distance(new_box_distance=new_box_distance, f=k1, n=k2,  is_tracing=False)
        self.fil_start_end_vis = starting_vis

    def set_colors_all(self, new_color:str)->None:
        """
        Set the same color for all the filaments. Used to compare the TRACED results. (called in multiple import)
        :param new_color: new color
        """
        def _set_colors(particles:List[MySketch.MySketch], filaments:List[MySketch.MySketch])->None:
            """
            Set the colors of a list of Mysketch obj present in the given lists
            :param particles: list of Mysketches obj
            :param particles: list of Mysketches obj
            """
            for p in particles:
                p.set_colour(colour=new_color)
            for f in filaments:
                f.set_colour(colour=new_color)

        dict_fil = self.filament3D_dictionary if self.is_3D else self.filament_dictionary
        dict_part = self.particle3D_dictionary if self.is_3D else self.particle_dictionary
        if self.type_case == constants.Type_case.SPA.value:
            for micrograph in dict_part.keys():
                _set_colors(particles=dict_part[micrograph], filaments=dict_fil[micrograph])
        else:
            for tomo_name in dict_part.keys():
                for z in dict_part[tomo_name].keys():
                    _set_colors(particles=dict_part[tomo_name][z], filaments=dict_fil[tomo_name][z])

    def get_boxsize(self, f:str, n:int=None)->int:
        """
        get the boxsize of a given file (and slice)
        :param f: filename
        :param n: number of slice
        :return boxsize
        """
        return self.boxsize_dictionary.get(f,-1) if self.type_case == constants.Type_case.SPA.value else self.boxsize_dictionary.get(f,list()).get(n,-1)


    def change_box_distance(self, new_box_distance:int, f:str, n:int=None, is_tracing:bool = False)-> List[MySketch.MySketch]:
        """
        change the distance between the sketches in the present in the given file 'f' at the given slice 'n' (in TOMO cases)
        :param new_box_distance: the new distance between 2 sketches in a filament
        :param f: filename
        :param n: number of slice
        :param is_tracing: if True it search into the tracing dict (box_dict_traced) otherwise (particle_dictionary)
        :return new_list
        """
        new_list = list()

        fil_segmented = self.get_sketches(f=f, n=n, is_3D=self.is_3D, is_tracing=is_tracing)
        self.fil_start_end_vis = True
        fil_start_end = self.get_sketches(f=f, n=n, is_3D=self.is_3D, is_tracing=is_tracing)
        self.fil_start_end_vis = False
        listed_sketches = {fil.id: list() for fil in fil_start_end}
        colour_sketches = {fil.id: fil.get_color() for fil in fil_start_end}

        for box in fil_segmented:
            z = int(box.z) if box.z is not None else box.z  # otherwise if z is a float it crashes in utils.resample_filament
            listed_sketches[box.id].append(box.get_as_BBox(confidence=box.get_confidence(), z=z))

        # Create the new list of boxes
        for fil_id, sketches in listed_sketches.items():
            fil = utils.Filament(boxes=sketches)
            resampled_f=utils.resample_filament(filament=fil,new_distance=new_box_distance)
            new_list.extend(helper.convert_list_bbox_to_sketch(boxes_list=resampled_f.boxes,out_dict=False,col=colour_sketches[fil_id],fil_id=fil_id))

        self._set_sketches(list_sketches=new_list,f=f, n=n)
        return new_list


    def update_boxsize_dictionary(self, new_boxsize:int, f:str,n:int=None)-> None:
        """
        Resize and return the sketches in the present in the given file 'f' at the given slice 'n' (in TOMO cases)
        :param new_boxsize: the new boxsize value
        :param f: filename
        :param n: number of slice
        """

        if self.type_case == constants.Type_case.SPA.value:
            self.boxsize_dictionary[f] = new_boxsize
        else:
            self.boxsize_dictionary[f][n] = new_boxsize

    def update_visualization_dictionary(self, new_visualization:constants.Visualization_cb, f:str, n:int=None)-> None:
        """
        Resize and return the sketches in the present in the given file 'f' at the given slice 'n' (in TOMO cases)
        :param new_visualization: the new visualization value
        :param f: filename
        :param n: number of slice
        :return: list of resized Mysketch obj present in the given file 'f' at the given slice 'n'
        """
        if self.type_case == constants.Type_case.SPA.value:
            self.visualization_dictionary[f] = new_visualization
        else:
            self.visualization_dictionary[f][n] = new_visualization

    def update_box_distance_dictionary(self, new_box_distance:int, f:str, n:int=None)-> None:
        """
        Resize and return the sketches in the present in the given file 'f' at the given slice 'n' (in TOMO cases)
        :param new_box_distance: the new distance between 2 sketches in a filament
        :param f: filename
        :param n: number of slice
        """
        if self.type_case == constants.Type_case.SPA.value:
            self.box_distance_dictionary[f] = new_box_distance
        else:
            self.box_distance_dictionary[f][n] = new_box_distance

    def delete_sketch_by_index(self, index:int, f:str, n:int=None)-> int:
        """
        remove the index sketch in the given self.boxmanager[f][n] (in case of TOMO or TOMO_FOLDER case)
        :param index: index in the dicts of Mysketch obj to remove
        :param f: filename
        :param n: number of slice
        :return mysketch id. We need it when we call this function from 'delete_filemant_by_index'
        """
        dict_2D = self.filament_dictionary if self.has_filament else self.particle_dictionary
        if self.type_case == constants.Type_case.SPA.value:
            id_part = dict_2D[f][index].id
            del dict_2D[f][index]
        else:
            id_part = dict_2D[f][n][index].id
            del dict_2D[f][n][index]
            if self.is_3D:  # the untraced cbox sketches are into a TOMO but 2D
                self.delete_3D(id_part, f, n)
        return id_part

    def delete_filemant_by_index(self, index:int, f:str, n:int=None)-> None:
        """
        remove all the sketches, rect and not, present in all the dicts form the given 'fil_id' id
        :param index: index in the dicts of Mysketch filament to remove
        :param f: filename
        :param n: number of slice
        """
        id_part = self.delete_sketch_by_index(index=index,f=f,n=n)
        d = self.particle_dictionary[f] if self.type_case == constants.Type_case.SPA.value else self.particle_dictionary[f][n]
        for i in range(len(d) - 1, -1, -1):
            if d[i].id == id_part:
                del d[i]
        if self.is_3D:
            pass #how manage it? directly in self.delete_3D?

    def get_central_n(self, id_part:int, f:str, n:int)->Union[Tuple[MySketch.MySketch,int],Tuple[None,None]]:
        """
        find the central 2D sketch of the given 'id_part' particle
        :param id_part: id particle
        :param f: filename
        :param n: number of slice that represent the center
        :return the central box and its slice's number, None in case of error
        """
        tot_slice = len(self.particle_dictionary[f])
        real_boxsize = self.get_boxsize(f=f,n=n)
        box_size = real_boxsize if real_boxsize>0 else tot_slice
        prev_slices = range(n, max(n-box_size , 0), -1)
        next_slices = range(n, min(n + box_size , tot_slice - 1))
        for slice_n in list(prev_slices) + list(next_slices):
            for b in self.get_sketches(f=f, n=slice_n, is_3D=True,  is_tracing = False):
                if b.id == id_part and not b.only_3D_visualization:
                    return b,slice_n
        return None,None


    def delete_3D(self, id_part:int, f:str, n:int)-> None:
        """
        remove the sketches that belong to the 'id_part' particle
        :param id_part: id particle
        :param f: filename
        :param n: number of slice that represent the center
        """
        tot_slice = len(self.particle_dictionary[f])
        real_boxsize = self.get_boxsize(f=f, n=n)
        box_size = real_boxsize if real_boxsize > 0 else tot_slice
        prev_slices = range(n, max(int(n - box_size / 2), 0), -1)
        next_slices = range(n, min(int(n + box_size / 2), tot_slice - 1))
        for slice_n in list(prev_slices)+list(next_slices):
            ref_list = self.get_sketches(f=f, n=slice_n, is_3D=True,  is_tracing = False)
            for b in ref_list:
                if b.id == id_part:
                    del ref_list[ref_list.index(b)]
                    break

    def add_picked_filament(self, fil:MySketch.MySketch,f:str, n:int=None, still_picking:bool= True)-> int:
        """
        insert the given sketch in the given self.boxmanager[f][n] (in case of TOMO or TOMO_FOLDER case)
        :param fil: instance of Mysketch obj
        :param f: filename
        :param n: number of slice
        :param still_picking: True if we are still picking
        :return filament id, its list of sketches has to have the same id (each sketch of this list). I need it in the import from file
        """
        # since for the real time visualization in the picking phase we delete and replot the current filament its id has to be always the same
        fil.id = self.counter

        # we update the counter only when we start to pick (onclick function). The first has counter 0 (in this way we do not have to adapt the code after importing)
        if not still_picking:
            self.counter+=1
        if self.type_case == constants.Type_case.SPA.value:
            self.filament_dictionary[f].append(fil)
        else:
            self.filament_dictionary[f][n].append(fil)
            if self.is_3D:  # the untraced cbox sketches are into a TOMO but 2D
                self.create_3D(fil,f,n, is_start_end_filament = True)
        return fil.id



    def add_sketch(self,sketch:MySketch.MySketch, f:str, n:int=None)-> None:
        """
        insert the given sketch in the given self.boxmanager[f][n] (in case of TOMO or TOMO_FOLDER case)
        :param sketch: instance of Mysketch obj
        :param f: filename
        :param n: number of slice
        """
        # first particle id is 0
        sketch.id = self.counter
        self.counter+=1
        if self.type_case == constants.Type_case.SPA.value:
            self.particle_dictionary[f].append(sketch)
        else:
            self.particle_dictionary[f][n].append(sketch)
            if self.is_3D:  # the untraced cbox sketches are into a TOMO but 2D
                self.create_3D(sketch,f,n, is_start_end_filament = False)

    def add_sketches(self,sketches:List[MySketch.MySketch], f:str, n:int=None, id_fil = None, colour:str = 'r')-> None:
        """
        It basically use in the importing data step
        insert the given sketches in the given self.boxmanager[f][n] (in case of TOMO or TOMO_FOLDER case)
        :param sketches: list of instances of Mysketch obj
        :param f: filename
        :param n: number of slice
        :param id_fil: id particles (they have the same id if they belong to a filament)
        :param colour: colour of the sketched. In filamnet they have the same colour of the filament
        """
        # first particle id is 0
        for s in sketches:
            s.set_colour(colour=colour)
            if id_fil is not None:
                s.id = id_fil
            else:
                s.id=self.counter
                self.counter+=1
        if self.type_case == constants.Type_case.SPA.value:
            self.particle_dictionary[f].extend(sketches)
        else:
            self.particle_dictionary[f][n].extend(sketches)
            if self.is_3D:  # the untraced cbox sketches are into a TOMO but 2D
                for s in sketches:
                    self.create_3D(sketch=s,f=f,n=n, is_start_end_filament = False)

    def create_3D(self, sketch:MySketch.MySketch, f:str, n:int, is_start_end_filament:bool)-> None:
        """
        It basically use in the importing data step
        insert the 2D section of sketch in the given self.boxmanager[f][n] (in case of TOMO or TOMO_FOLDER case)
        for representing the 3D visualization of it
        :param sketch: instance of Mysketch obj of which we create the 3D visualization
        :param f: filename
        :param n: number of slice
        :param is_start_end_filament: True if it is creating a 3D for start end filament visualization
        """
        # added the given sketch to the 3D dict
        dict3D = self.filament3D_dictionary if is_start_end_filament else self.particle3D_dictionary
        dict3D[f][n].append(sketch)

        tot_slice = len(self.filament_dictionary[f]) if is_start_end_filament else len(self.particle_dictionary[f] )
        original_size = int(sketch.get_height())
        # i do not care if len(prev_slices)==len(next_slices) because 'zip' ll consider the short one length as limit
        # in real case this situation should not happened because a particle is a sphere and the whole particle
        # is into the tomo.
        # Hence cryolo will not lead us to this situation and the user ll not do either
        prev_slices = range(n - 1, max(int(n - original_size / 2), 0), -1)          # /2 because new_size-=2
        next_slices = range(n + 1, min(int(n + original_size / 2), tot_slice - 1))
        new_size = original_size - 2
        delta=1
        for prev_index, next_index in zip(prev_slices, next_slices):
            new_sketch = helper.create_sketch(sketch=sketch, delta=delta, size=new_size,is_start_end_filament=is_start_end_filament)
            dict3D[f][prev_index].append(new_sketch)
            dict3D[f][next_index].append(new_sketch)
            new_size -= 2

    def create_traced_3D(self)-> None:
        """
        Create the 3D results after running the tracing.
        The tracing result are into 'box_dict_traced'. I create the 3D version of these values
        """
        for f in self.box_dict_traced.keys():
            for n,sketches in self.box_dict_traced[f].items():
                for sketch in sketches:
                    self.create_3D(sketch=sketch,f=f,n=n,is_start_end_filament=False)

    @staticmethod
    def get_upper_lower_thres_tomo(single_box_dict:dict)->Tuple[int,int]:
        """
        The 'minimum size' and 'maximum size' of the thresholding tab.
        :param single_box_dict: box dict of a case (SPA o image TOMO)
        """
        min_size = 99999
        max_size = -99999
        for _, rectangles in single_box_dict.items():
            for rect in rectangles:
                if rect.get_est_size(circle=False) > max_size:
                    max_size = rect.get_est_size(circle=False)
                if rect.get_est_size() < min_size:
                    min_size = rect.get_est_size(circle=False)


        #in case you selected an empty folder you have to switch them
        if max_size<min_size:
            max_size,min_size=min_size,max_size

        return max_size, min_size

    def get_upper_lower_thres(self)-> Union[Tuple[int,int],Dict[str,Dict[str,int]]]:
        """
        After loading from cbox we have to set dynamically the lower and upper threshold.
        The 'minimum size' and 'maximum size' of the thresholding tab.
        In case of tomo, both the cases, return a dict
            k: filename
            v: [upper value, lower value]
        :return upper and lower values
        """

        if self.type_case == constants.Type_case.SPA.value:
            return self.get_upper_lower_thres_tomo(single_box_dict=self.particle_dictionary)
        else:
            out = dict()
            for filename in self.particle_dictionary.keys():
                mx,mn =self.get_upper_lower_thres_tomo(single_box_dict=self.particle_dictionary[filename])
                out.update({ filename:{ "upper":mx,"lower":mn}})
            return out

    def has_same_boxsize(self,boxsize:int, f:str, n:int=None)->bool:
        """
        Check if in the file 'f' slice 'n' (only tomo cases) last time it was plotted with the same boxsize
        :param boxsize: boxsize value
        :param f: filename
        :param n: number of slice
        :return: true if a resize is not needed
        """
        return boxsize == self.get_boxsize(f=f,n=n)

    def has_same_visualization(self, visualization:constants.Visualization_cb, f:str, n:int=None)->bool:
        """
        Check if in the file 'f' slice 'n' (only tomo cases) last time it was plotted with the same visualization
        :param visualization: visualization value
        :param f: filename
        :param n: number of slice
        :return: true if a resize is not needed
        """
        if self.type_case == constants.Type_case.SPA.value:
            return visualization == self.visualization_dictionary.get(f)
        return visualization == self.visualization_dictionary.get(f).get(n)


    def has_same_box_distance(self, box_distance:int, f:str, n:int=None)->bool:
        """
        Check if in the file 'f' slice 'n' (only tomo cases) last time it was plotted with the same box distance
        :param box_distance: box_distance value
        :param f: filename
        :param n: number of slice
        :return: true if a resize is not needed
        """
        if self.type_case == constants.Type_case.SPA.value:
            return box_distance == self.box_distance_dictionary.get(f)
        return box_distance == self.box_distance_dictionary.get(f).get(n)

    def is_empty(self)->bool:
        """
        Return True if there are no boxes in the particle_dictionary var
        """
        if self.type_case == constants.Type_case.SPA.value:
            for f in self.particle_dictionary.keys():
                if len(self.particle_dictionary[f]) > 0:
                    return False
        else:
            for f in self.particle_dictionary.keys():
                for n in self.particle_dictionary[f].keys():
                    if len (self.particle_dictionary[f][n]) > 0:
                        return False
        return True

    def update_counter(self, n=1):
        """
        Update the counter
        :param n: number of unit to add
        """
        self.counter+=n

    def clean(self)->None:
        """
        clean the dict
        """
        self.particle_dictionary = dict()
        self.particle3D_dictionary = dict()
        self.filament_dictionary = dict()
        self.filament3D_dictionary = dict()
        self.boxsize_dictionary = dict()
        self.visualization_dictionary = dict()
        self.box_distance_dictionary = dict()
        self.box_dict_traced = dict()
        self.type_case=constants.Type_case.NOT_LOADED.value
        self.is_3D = False
        self.counter = 1
        self.is_cbox_untraced = False
        self.list_purefiles = list()

    def set_untraced_param(self)->None:
        """
        In the TOMO when we load untraced values we are loading 2D particles
        """
        self.is_3D = False
        self.is_cbox_untraced = True

    def get_tot_filament(self,tomo_name=None)->int:
        """
        Get the total number of filament
        :param tomo_name: tomo fname, in case tomofolder with None name it ll count all the written filaments
        """
        tot = 0
        if self.type_case == constants.Type_case.SPA.value:
            for f in self.filament_dictionary.keys():
                tot+=len(self.filament_dictionary[f])
        else:
            if tomo_name is not None:
                for z in self.filament_dictionary[tomo_name].keys():
                    tot += len(self.filament_dictionary[tomo_name][z])
            else:
                for f in self.filament_dictionary.keys():
                    tot+=self.get_tot_filament(f)
        return tot

    def set_box_distance_dict_after_import(self):
        """
        After loading from file it has to calculate the box distance and set it
        """
        def calculate_dist():
            if len(sketches) > 3:
                x1, y1 = sketches[0].get_xy(circle=True)
                for sketch in sketches:
                    x2, y2 = sketch.get_xy(circle=True)
                    if x1 != x2 or y1 != y2:
                        dist = int(math_sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
                        return dist

        d=None
        if self.type_case == constants.Type_case.SPA.value:
            for sketches in self.particle_dictionary.values():
                d= calculate_dist()
                if d is not None:
                    for k in self.box_distance_dictionary.keys():
                        self.box_distance_dictionary[k]=d
                    return d
        else:
            for tomo_name in self.particle_dictionary.keys():
                for sketches in self.particle_dictionary[tomo_name].values():
                    d = calculate_dist()
                    if d is not None:
                        for tname in self.box_distance_dictionary.keys():
                            for z in self.box_distance_dictionary[tname].keys():
                                self.box_distance_dictionary[tname][z] = d
                        return d
        return d

    def reset(self)->None:
        """
        Remove all the sketches present into self.particle_dictionary.
        It is called after reset->file
        """
        self.counter = 1
        self.is_cbox_untraced = False

        for k1,v1 in self.particle_dictionary.items():
            if self.type_case == constants.Type_case.SPA.value:
                self.particle_dictionary[k1] = list()
                self.boxsize_dictionary[k1] = -1
                self.particle3D_dictionary[k1] = list()
                self.filament_dictionary[k1] = list()
                self.filament3D_dictionary[k1] = list()
                self.visualization_dictionary[k1] = None
                self.box_distance_dictionary[k1] = None
            else:
                for k2,v2 in self.particle_dictionary[k1].items():
                    self.particle_dictionary[k1][k2] = list()
                    self.boxsize_dictionary[k1][k2] = -1
                    self.particle3D_dictionary[k1][k2] = list()
                    self.filament_dictionary[k1][k2] = list()
                    self.filament3D_dictionary[k1][k2] = list()
                    self.visualization_dictionary[k1][k2] = None
                    self.box_distance_dictionary[k1][k2] = None

