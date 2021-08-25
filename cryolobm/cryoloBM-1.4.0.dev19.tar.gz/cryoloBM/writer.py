from os import path,makedirs, remove as os_remove
from cryoloBM import helper_GUI,constants,helper,helper_filament
from cryolo import CoordsIO
from cryolo.utils import BoundBox,Filament

from cryoloBM import boxmanager_controller,boxmanager_view,MySketch,box_dictionary # for type hinting purpose
from typing import Union,List,Dict,Tuple,Callable

def save_on_files(controller:boxmanager_controller)->None:
    """
    Save on file the results
    :param controller: Boxmanager_controller obj
    """
    selected_slices=get_selected_slice(controller=controller)
    box_dir = get_box_dir_path(view=controller.view)

    if not box_dir:
        return

    # i do not want to change the GUI var, it is used for saving purpose
    box_distance_filament = None
    if controller.model.has_filament:
        box_distance_filament, result =controller.view.get_inter_box_distance(value=controller.model.box_distance_filament)
        if not result:
            return
        elif box_distance_filament < 1:
            controller.view.err_message( msg="Invalid Box distance value. It has to be higher than 0")
            return

    if controller.model.is_cbox_untraced and not controller.model.has_filament: # not self.has_filament because in this version we cannot trace in filament case
        write_all_type_optimization(controller=controller,box_dir=box_dir, selected_slices=selected_slices)
    else:
        fil_start_end_vis = controller.model.box_dictionary.fil_start_end_vis
        controller.model.box_dictionary.fil_start_end_vis= False
        write_all_type_classic(controller=controller,box_dir=box_dir, selected_slices=selected_slices, box_distance_filament=box_distance_filament)
        controller.model.box_dictionary.fil_start_end_vis = fil_start_end_vis

    controller.model.unsaved_changes = False

def write_all_type_classic(controller:boxmanager_controller, box_dir:str, selected_slices:Union[List[str],Dict[str,str]], box_distance_filament:int)->None:
    """
    It saves on file the results after a classic picking ( no optimizing result case)
    :param controller: Boxmanager_controller obj
    :param box_dir: main directory where save the results
    :param selected_slices: list or dict ( in case of folder of tomo) of slices to save
    :param box_distance_filament: distance between boxes in case of filament
    """

    if controller.model.has_filament:
        #set the box_distance_filament
        controller.model.box_dictionary.change_box_distance_all(new_box_distance=box_distance_filament)

    box_dictionary_to_save, ignored_slice, empty_slice = prepare_output(controller= controller, slices=selected_slices,is_tracing=False)


    is_tomo = controller.model.type_case != constants.Type_case.SPA.value
    for file_type in ["STAR", "CBOX", "EMAN"]:
        is_cbox = file_type == "CBOX"

        # the picked filament will be saved only in cbox format
        if controller.model.has_filament and not is_cbox :
            continue

        d = path.join(box_dir, file_type)
        file_ext, write_coords_ = prepare_vars_for_writing(controller = controller, box_dir=box_dir, file_type=file_type)

        pd = controller.view.create_progress_dialog(title="Write box files to " + d)
        pd.show()

        if is_tomo:
            if is_cbox:
                if controller.model.has_filament:
                    d+=constants.Writer_filament_suffix.CBOX_FILAMENT_SUFFIX.value
                    box_dictionary_to_save=create_box_dict_of_filament_obj(controller.model.box_dictionary,controller.model.box_distance_filament)
                else:
                    # we want to save ANYWAY all the selected boxes
                    box_dictionary_to_save = controller.model.box_dictionary.particle_dictionary
                write_coordinates_tomo(controller=controller,
                                       box_dict_to_save=box_dictionary_to_save,
                                       pd=pd, empty_slice=empty_slice, ignored_slice=ignored_slice,
                                       is_cbox=is_cbox, write_coords_=write_coords_,
                                       file_ext=file_ext, box_dir=d,has_filament=controller.model.has_filament)
            pd.close()
            continue

        # create an empty file name for the checked micrograph file
        save_empty_file_SPA(controller=controller,file_ext=file_ext, d=d, empty_slice=empty_slice)

        if is_cbox:
            if controller.model.has_filament:
                d+=constants.Writer_filament_suffix.CBOX_FILAMENT_SUFFIX.value
                box_dictionary_to_save = create_box_dict_of_filament_obj(controller.model.box_dictionary,
                                                                         controller.model.box_distance_filament)
            write_coordinates_micrograph(controller=controller, pd=pd, box_dict_to_save=box_dictionary_to_save,
                                         box_dir=d, file_ext=file_ext, is_cbox=is_cbox, write_coords_=write_coords_,has_filament=controller.model.has_filament)

        elif file_type == "EMAN" and controller.model.has_filament:
            for write_coords in write_coords_:
                suffix = constants.Writer_filament_suffix.HELICON_SUFFIX.value if "write_eman1_helicon" in str(
                    write_coords) else constants.Writer_filament_suffix.EMAN_STAR_FILAMENT_SUFFIX.value
                box_dir = d + suffix
                write_coordinates_micrograph(controller=controller, pd=pd, box_dict_to_save=box_dictionary_to_save,
                                             box_dir=box_dir, file_ext=file_ext, is_cbox=is_cbox, write_coords_=write_coords_,has_filament=False)


        else:
            if controller.model.has_filament:
                d += constants.Writer_filament_suffix.EMAN_STAR_FILAMENT_SUFFIX.value
            write_coordinates_micrograph(controller=controller, pd=pd, box_dict_to_save=box_dictionary_to_save,
                                         box_dir=d, file_ext=file_ext, is_cbox=is_cbox, write_coords_=write_coords_,has_filament=False)

        pd.close()

    del box_dictionary_to_save

def write_all_type_optimization(controller:boxmanager_controller, box_dir:str, selected_slices:Union[List[str],Dict[str,str]]):
    """
    It saves on file the results after the optimization ( cbox_untraced case)
    We save on file the result of the tracing
    :param controller: Boxmanager_controller obj
    :param box_dir: main directory where save the results
    :param selected_slices: list or dict ( in case of folder of tomo) of slices to save
    """

    for file_type in ["STAR", "CBOX_3D", "EMAN_3D", "CBOX_UNTRACED", "COORDS"]:

        is_cbox = "CBOX" in file_type or "EMAN_3D" in file_type       # because in EMAN_3D output we want to have the same as in CBOX_3D


        d = path.join(box_dir, file_type)

        file_ext, write_coords_ = prepare_vars_for_writing(controller=controller, box_dir=box_dir, file_type=file_type)

        if file_type == "COORDS":
            write_coords_ = CoordsIO. write_coords_file

        pd = controller.view.create_progress_dialog(title="Write box files to " + d)
        pd.show()

        if file_type == "CBOX_UNTRACED":
            box_dictionary_to_save, ignored_slice, empty_slice = prepare_output(controller= controller, slices=selected_slices,is_tracing=True)

            # at 19.02.21 the picking filament is not enabled
            # after the tracing we save into 'CBOX_UNTRACED' the input value gave to 'grouping3d.do_tracing' called int 'helper_tab_tracing.trace_values'
            # hence the model.box_dictionary.particle_dictionary
            write_coordinates_tomo(controller=controller,
                                   box_dict_to_save=controller.model.box_dictionary.particle_dictionary,
                                   pd=pd, empty_slice=empty_slice, ignored_slice=ignored_slice,
                                   is_cbox=is_cbox, write_coords_=write_coords_,
                                   file_ext=file_ext, box_dir=d,has_filament=False)
            pd.close()
            continue


        # we want to save ANYWAY all the selected boxes
        write_coordinates_tomo(controller=controller,
                               box_dict_to_save=controller.model.box_dictionary.box_dict_traced,
                               pd=pd, empty_slice=[], ignored_slice=[],
                               is_cbox=is_cbox, write_coords_=write_coords_,
                               file_ext=file_ext, box_dir=d,has_filament=False)

        pd.close()
    controller.view.warning_retrain()
    return

def get_selected_slice(controller:boxmanager_controller)->Union[List[str],Dict[str,str]]:
    """
    Return dict (in TOMO_FOLDER case otherwise list) of all the checked micrographs/slices
    :param controller: Boxmanager_controller obj
    :return list/dict of micrograph's name/#slices
    """
    selected_slices = dict() if controller.model.type_case == constants.Type_case.TOMO_FOLDER.value else list()
    for root_index in range(controller.view.tree.invisibleRootItem().childCount()):
        root_element = controller.view.tree.invisibleRootItem().child(root_index)  # can be tomogram or a folder
        for child_index in range(root_element.childCount()):
            if controller.model.type_case == constants.Type_case.TOMO_FOLDER.value :
                selected_slice_child = list()
                for child_child_index in range(root_element.child(child_index).childCount()):
                    if root_element.child(child_index).child(child_child_index).checkState(0) == controller.view.checkbox_state_value(checked=True):
                        selected_slice_child.append(str(child_child_index))     # to be able to generalize 'prepare_output's code
                selected_slices.update({path.splitext(path.basename(root_element.child(child_index).text(0)))[
                                           0]: selected_slice_child})
            elif root_element.child(child_index).checkState(0) == controller.view.checkbox_state_value(checked=True):
                selected_slices.append(path.splitext(path.basename(root_element.child(child_index).text(0)))[0])

    # In case of single tomo the output has to be a dict as in the folder tomo case
    if controller.model.type_case == constants.Type_case.TOMO.value:
        selected_slices = {controller.get_current_filename(with_extension=False): selected_slices}
    return selected_slices


def get_box_dir_path(view:boxmanager_view)->Union[str,None]:
    """
    Ask the dir where to save and return it
    :param view: Boxmanager_view obj
    :return box dir path
    """
    box_dir = view.qt_esixting_folder(msg="Select Box Directory")

    # Remove untitled from path if untitled not exists
    if box_dir and box_dir[-8] == "untitled" and path.isdir(box_dir):
        return box_dir[:-8]

    if not box_dir:
        return None

    return box_dir


def prepare_output(controller: boxmanager_controller, slices: List[str], is_tracing: bool) -> Tuple[
                                Union[Dict[str, List[MySketch.MySketch]], Dict[str, Dict[int, List[MySketch.MySketch]]]],
                                Union[List[str], Dict[str, List[str]]],
                                Union[List[str], Dict[str, List[str]]]]:
    """
    Select the data for writing on  file
    :param controller: Boxmanager_controller obj
    :param slices: list of slices to save
    :param is_tracing: if True it search into the tracing dict (box_dict_traced) otherwise (particle_dictionary)
    :return
            box_dict: box_dict format with slice containing boxes in 'self.box_dictionary' format. (dict of dict in case 3D folder)
            slice_ignored: list of slice with boxes but their checkbox are unchecked  (dict of list in case 3D folder)
            slice_empty: list of slice without boxes but their checkbox are checked (dict of list in case 3D folder)
    """
    b_dict = controller.model.box_dictionary.box_dict_traced if is_tracing else controller.model.box_dictionary.particle_dictionary
    box_dict = dict()
    is_tomo = controller.model.type_case != constants.Type_case.SPA.value
    slice_ignored = dict() if is_tomo else list()
    slice_empty = dict() if is_tomo else list()

    if controller.model.type_case == constants.Type_case.SPA.value:
        for f in controller.model.box_dictionary.list_purefiles:
            sketches = controller.model.box_dictionary.get_sketches(f=f, n=None, is_3D=False,is_tracing=is_tracing)
            empty = len(sketches) == 0
            in_slices = f in slices
            if empty and in_slices:
                slice_empty.append(f)
            elif not empty and not in_slices:
                slice_ignored.append(f)
            elif not empty and in_slices:
                box_dict.update({f: sketches})
    else:
        for f, d in b_dict.items():
            box_dict.update({f: dict()})
            slice_ignored.update({f:list()})
            slice_empty.update({f: list()})
            for n,boxes in d.items():
                in_slices = str(n) in slices[f]
                empty= len(boxes) == 0
                if empty and in_slices:
                    slice_empty[f].append(n)
                elif not empty and not in_slices:
                    slice_ignored[f].append(n)
                elif not empty and in_slices:
                    box_dict[f].update({n: boxes})

    return box_dict, slice_ignored, slice_empty

def prepare_vars_for_writing(controller:boxmanager_controller, box_dir:str, file_type:str)->Tuple[str,Union[Callable,List[Callable]]]:
    """
    Function to detect which cryolo function use for saving data on file and with which suffix.
    It create all the output folder !!
    :param controller: Boxmanager_controller obj
    :param box_dir: main directory where save the results
    :param file_type: filetype ("STAR", "CBOX" or "EMAN")
    """
    file_ext = ""
    write_coords_= None
    if controller.model.has_filament:
        if file_type == "EMAN":
            file_ext = ".box"
            write_coords_ = [CoordsIO.write_eman1_filament_start_end, CoordsIO.write_eman1_helicon]
            makedirs(path.join(box_dir, file_type + constants.Writer_filament_suffix.HELICON_SUFFIX.value ), exist_ok=True)
            makedirs(path.join(box_dir, file_type + constants.Writer_filament_suffix.EMAN_STAR_FILAMENT_SUFFIX.value), exist_ok=True)
        elif file_type == "STAR":
            file_ext = ".star"
            write_coords_ = CoordsIO.write_star_filemant_file
            makedirs(path.join(box_dir, file_type + constants.Writer_filament_suffix.EMAN_STAR_FILAMENT_SUFFIX.value), exist_ok=True)
        elif file_type == "CBOX":
            file_ext = ".cbox"
            write_coords_ = CoordsIO.write_cbox_file
            makedirs(path.join(box_dir, file_type + constants.Writer_filament_suffix.CBOX_FILAMENT_SUFFIX.value), exist_ok=True)
        return file_ext, write_coords_

    is_spa = controller.model.type_case == constants.Type_case.SPA.value
    d = path.join(box_dir, file_type)
    makedirs(d, exist_ok=True)
    file_ext = ".box"
    write_coords_ = CoordsIO.write_eman1_boxfile if is_spa  else  CoordsIO.write_eman_boxfile3d

    if file_type == "STAR":
        file_ext = ".star"
        write_coords_ = CoordsIO.write_star_file
    elif file_type in ["CBOX", "CBOX_3D", "EMAN_3D", "CBOX_UNTRACED"]:
        file_ext = ".cbox"
        write_coords_ = CoordsIO.write_cbox_file
    return file_ext, write_coords_


def save_empty_file_SPA(controller:boxmanager_controller, file_ext:str, d:str, empty_slice:List[str])->None:
    """
    Create the empty files in SPA case
    """
    if not controller.model.has_filament:
        for f in empty_slice:
            with open(path.join(d, f + file_ext), "w"):
                pass
        return

    directories = list()
    if file_ext == ".cbox":
        directories = [d + constants.Writer_filament_suffix.CBOX_FILAMENT_SUFFIX.value]
    elif file_ext == ".star":
        directories = [d + constants.Writer_filament_suffix.EMAN_STAR_FILAMENT_SUFFIX.value]
    elif file_ext == ".box":
        directories = [d + constants.Writer_filament_suffix.HELICON_SUFFIX.value,d + constants.Writer_filament_suffix.EMAN_STAR_FILAMENT_SUFFIX.value]

    for d in directories:
        for f in empty_slice:
            with open(path.join(d, f + file_ext), "w"):
                pass


def write_coordinates_tomo(controller: boxmanager_controller,
                           box_dict_to_save: Dict[str, Dict[int, List[MySketch.MySketch]]],
                           pd: helper_GUI.QtG.QProgressDialog,
                           empty_slice: Union[Dict[str, List[str]],list],
                           ignored_slice: Union[Dict[str, List[str]],list],
                           is_cbox: bool,
                           write_coords_: Callable,
                           file_ext: str,
                           box_dir: str, has_filament:bool) -> None:
    num_writtin_part = 0
    for f in box_dict_to_save.keys():
        counter = 0
        overwrite = True
        boxes = []
        for n, rectangles in box_dict_to_save[f].items():

            if pd.wasCanceled():
                break
            else:
                pd.show()
                val = int((counter + 1) * 100 / len(box_dict_to_save[f].items()))
                pd.setValue(val)
            controller.view.run_in_same_thread()

            box_filename = f + file_ext
            box_file_path = path.join(box_dir, box_filename)

            if overwrite is True:
                overwrite = False
                if path.isfile(box_file_path):
                    os_remove(box_file_path)

            if has_filament:
                num_writtin_part = num_writtin_part + len(rectangles)
                boxes += rectangles
            else:
                if is_cbox:
                    rectangles = [ box for box in rectangles if
                        helper.check_if_should_be_visible(box=box, current_conf_thresh=controller.model.current_conf_thresh,
                                                          upper_size_thresh=controller.model.upper_size_thresh,
                                                          lower_size_thresh=controller.model.lower_size_thresh,
                                                          num_boxes_thresh=controller.model.current_num_boxes_thresh,
                                                          is_filament=False)
                    ]

                real_sketches = [rect.getSketch(circle=False) for rect in rectangles]
                if controller.model.use_estimated_size:
                    for sketch in real_sketches:
                        sketch.resize(controller.model.boxsize)
                num_writtin_part += len(real_sketches)

                for rect_index, rect in enumerate(real_sketches):
                    confidence = 1
                    if rectangles[rect_index].get_confidence() is not None:
                        confidence = rectangles[rect_index].get_confidence()
                    x_lowerleft = int(rect.get_x())
                    y_lowerleft = int(rect.get_y())
                    boxize = int(rect.get_width())
                    box = BoundBox(x=x_lowerleft, y=y_lowerleft, w=boxize, h=boxize, c=confidence, z=n,depth=1)
                    boxes.append(box)


            if is_cbox:
                # there is a case where i pass to this function empty_slice=ignored_slice=[]
                empty = empty_slice[f] if empty_slice else list()
                ignored = ignored_slice[f] if ignored_slice else list()
                write_coords_(box_file_path, boxes, empty, ignored)
            else:
                write_coords_(box_file_path, boxes)

            counter = counter + 1
    if controller.model.has_filament:
        print(f"{controller.model.box_dictionary.get_tot_filament(tomo_name=None)} filaments written in '{file_ext}' file.")
    else:
        print(f"{num_writtin_part} particles written in '{file_ext}' file.")

def write_coordinates_micrograph(controller:boxmanager_controller, pd:helper_GUI.QtG.QProgressDialog, box_dict_to_save:Dict[str, List[MySketch.MySketch]], box_dir:str, file_ext:str, is_cbox:bool, write_coords_:Callable, has_filament:bool)->None:
    # only in a 3D tomo image we have to delete an existing file before starting to write the new one.
    # Basically because we write in append mode on a file the selected particles slice after slice
    num_writtin_part = 0
    counter = 0
    slice_index = None
    boxes = list()
    for filename, rectangles in box_dict_to_save.items():

        if pd.wasCanceled():
            break
        else:
            pd.show()
            val = int((counter + 1) * 100 / len(box_dict_to_save.items()))
            pd.setValue(val)
        controller.view.run_in_same_thread()

        box_filename = filename + file_ext
        box_file_path = path.join(box_dir, box_filename)

        if has_filament:
            num_writtin_part = num_writtin_part + len(rectangles)
            boxes += rectangles
        else:
            if is_cbox:
                rectangles = [
                    box for box in rectangles if
                    helper.check_if_should_be_visible(box=box, current_conf_thresh=controller.model.current_conf_thresh,
                                               upper_size_thresh=controller.model.upper_size_thresh,
                                               lower_size_thresh=controller.model.lower_size_thresh,
                                               num_boxes_thresh=controller.model.current_num_boxes_thresh,
                                               is_filament=False)
                ]
                # if self.use_estimated_size_checkbox.isChecked():

            real_sketches = [rect.getSketch(circle=False) for rect in rectangles]
             # todo: why i m doing the resize only for SPA? Anyway the code works properly
            if controller.model.use_estimated_size:
                for sketch in real_sketches:
                    sketch.resize(controller.model.boxsize)

            num_writtin_part += len(real_sketches)

            for rect_index, rect in enumerate(real_sketches):
                x_lowerleft = int(rect.get_x())
                y_lowerleft = int(rect.get_y())
                boxize = int(rect.get_width())
                confidence = 1
                if rectangles[rect_index].get_confidence() is not None:
                    confidence = rectangles[rect_index].get_confidence()
                box = BoundBox(x=x_lowerleft, y=y_lowerleft, w=boxize, h=boxize, z=slice_index, c=confidence, depth=1)
                box.meta.update({'num_boxes':rectangles[rect_index].num_boxes})
                boxes.append(box)

        counter += 1
        if "write_eman1_filament_start_end" in str(write_coords_):
            write_coords_(boxes,box_file_path)
        elif "write_eman1_helicon" in str(write_coords_):
            write_coords_(boxes, box_file_path,filename)
        else:
            write_coords_(box_file_path, boxes)
        boxes = list()

    if controller.model.has_filament:
        print(f"{controller.model.box_dictionary.get_tot_filament(tomo_name=None)} filaments written in '{file_ext}' file.")
    else:
        print(f"{num_writtin_part} particles written in '{file_ext}' file.")


def create_box_dict_of_filament_obj(box_dict:box_dictionary.Box_dictionary,box_distance_filament_picking:int ):
    """
    Return the box_dictionary for writing on file.
    It is used basically for creating a list of Filament obj from a list of  filament rect box
    :param box_dict
    :param box_distance_filament_picking: distance between boxes in case of filament
    """
    def fill(fil_segmented):
        """
        fill the dict
        """
        l=list()
        listed_sketches = dict()
        if fil_segmented:
            for box in fil_segmented:
                if box.id in listed_sketches:
                    listed_sketches[box.id].append(box.get_xy(circle=False))
                else:
                    listed_sketches.update({box.id: [box.get_xy(circle=False)]})

            boxsize = fil_segmented[0].get_height() if fil_segmented else None

            for fil_id, xy in listed_sketches.items():
                fil = helper_filament.picked_filament(box_size=boxsize, is_tomo=is_tomo, fil_id=fil_id)
                fil.begin_fil = listed_sketches[fil_id][0][0] + boxsize / 2, listed_sketches[fil_id][0][1] + boxsize / 2
                fil.end_fil = listed_sketches[fil_id][-1][0] + boxsize / 2, listed_sketches[fil_id][-1][1] + boxsize / 2
                l.append(Filament(fil.fill_and_get_sketches(box_distance=box_distance_filament_picking, as_bbox=True, z=z)))
        return l

    # set temporarily to True for getting via 'get_sketches' the start_end rect
    starting_vis = box_dict.fil_start_end_vis
    box_dict.fil_start_end_vis = False

    is_tomo = box_dict.type_case != constants.Type_case.SPA.value
    z=None
    if not is_tomo:
        out = {k: list() for k in box_dict.particle_dictionary}
        for f in box_dict.particle_dictionary.keys():
            out[f] = fill(box_dict.get_sketches(f=f, n=None, is_3D=False, is_tracing=False))
    else:
        out = {tomoname: dict() for tomoname in box_dict.particle_dictionary}
        for tomoname,list_z in box_dict.particle_dictionary.items():
            for z in list_z:
                out[tomoname].update({z: fill(box_dict.get_sketches(f=tomoname, n=z, is_3D=False, is_tracing=False))})

    box_dict.fil_start_end_vis = starting_vis
    return out

