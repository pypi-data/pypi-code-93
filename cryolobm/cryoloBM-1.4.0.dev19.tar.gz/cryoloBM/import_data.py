"""
All the functions used to load data from file
"""
from cryoloBM import helper_filament, helper_image, constants, helper, MySketch
from cryolo import CoordsIO,utils

from math import isnan
from os import path,listdir, stat as os_stat
import random
import time

from cryoloBM import boxmanager_controller # for type hinting purpose
from typing import Union, List

COLORS = ["b", "r", "c", "m", "y", "k", "w"]


def box_to_sketch(controller:boxmanager_controller ,box:utils.BoundBox, color)->MySketch.MySketch:
    """
    Convert a bbox obj in a sketch. It is the old 'box_to_rectangle' function
    :param controller: Boxmanager_controller obj
    :param box: the bbox obj
    :param color: the color of the contour of the sketch
    :return : the converted mysketch obj
    """
    is_tomo = controller.model.type_case in [constants.Type_case.TOMO.value, constants.Type_case.TOMO_FOLDER.value]
    num_boxes = 1
    # controller.model.boxsize = avg_size # avg_size = (int(box.w) + int(box.h)) // 2 #todo: do i need this????? it is related to helper_GUI.show_loaded_boxes
    est_size = (int(box.w) + int(box.h)) // 2
    meta = None
    if "est_box_size" in box.meta:
        meta = {"est_box_size": box.meta["est_box_size"]}
        est_size = (box.meta["est_box_size"][0] + box.meta["est_box_size"][1]) // 2
    if 'num_boxes' in box.meta and controller.model.is_cbox and isnan(box.meta["num_boxes"]) is False:
        num_boxes = box.meta["num_boxes"]

    confidence = box.c if box.c is not None else 1
    return  MySketch.MySketch(xy =(int(box.x), int(box.y)), width=int(box.w), height=int(box.h), is_tomo=is_tomo,
                              angle=0.0, est_size=est_size, confidence=confidence, only_3D_visualization=False,
                              num_boxes=num_boxes, meta=meta, z=box.z,
                              linewidth=1, edgecolor=color, facecolor="none")

def _remove_old_boxes(controller:boxmanager_controller)->None:
    """
    Delete old boxes and reset boxdictionary's dictionaries
    Called if the user want remove the old boxes:  "Keep old boxes loaded and show the new ones in a different color?"
    :param controller: Boxmanager_controller obj
    """
    # delete these sketches from the figure
    helper_image.delete_all_patches(controller=controller)
    # reset the dictionaries
    controller.model.box_dictionary.reset()
    # uncheck all the slides
    controller.view.uncheck_all_slides(type_case=controller.model.type_case)
    # reset the counters
    controller.view.update_tree_boxsizes( update_current=False, all_tomos=False)
    controller.view.update_global_counter()

    # restore the clean canvas
    if controller.view.background_current:
        controller.view.fig.canvas.restore_region(controller.view.background_current)

def _update_entries_empty_file(f:str , updated_entries:List[str], is_star_startend:bool, is_helicon:bool, is_eman1_startend:bool)->str:
    """
    Update entries for empty file
    if the file is empty i want just to check the related checkbox
    :param f: filename
    :param updated_entries: list of entries to update
    :param is_eman1_startend: True if 'f' is 'eman1_startend' file
    :param is_helicon: True if 'f' is 'is_helicon' file
    :param is_eman1_startend: True if 'f' is 'is_eman1_startend' file
    :return : the entry name
    """
    dict_entry_name = path.splitext(f)[0]
    if is_star_startend:
        dict_entry_name = f[:-5]
    elif is_helicon or is_eman1_startend:
        dict_entry_name = f[:-4]
    updated_entries.append(dict_entry_name)
    return dict_entry_name


def _check_correct_import_data(controller:boxmanager_controller, keep:bool, boxes:List[Union[utils.Filament,utils.BoundBox]])->bool:
    """
    When load data keeping the old data i have to make sure that:
        -) we do not load particle after filament and viceversa
        -) when we are visualizing traced filament we do not load untraced and viceversa (only tomo cases)
    :param controller: Boxmanager_controller obj
    :param keep: True if you will keep the old data
    :param boxes
    :return True if everything ok
    """
    if keep is False:
        return True

    err_msg=""
    if controller.model.has_filament and not isinstance(boxes[0], utils.Filament):
        err_msg="Error: You tried to load particles after loading filaments"
    elif not controller.model.has_filament and isinstance(boxes[0], utils.Filament):
        err_msg = "Error: You tried to load filaments after loading particles"
    elif controller.model.has_filament and controller.model.type_case != constants.Type_case.SPA.value:
        # it is not possible load untraced filament when are visualizing the traced and viceversa
        loading_untraced = helper.is_cbox_untraced(boxes[0].boxes[0])
        if controller.model.is_cbox_untraced and not loading_untraced:
            err_msg ="Error: You tried to load traced filaments after loading untraced filaments"
        if not controller.model.is_cbox_untraced and loading_untraced:
            err_msg = "Error: You tried to load untraced filaments after loading traced filaments"
    else:
        return True

    controller.view.err_message(msg=err_msg)
    return False

def _load_data(controller:boxmanager_controller, pathfile:str, keep:bool, t_start:float)->List[Union[utils.Filament, utils.BoundBox]]:
    boxes = list()
    controller.model.is_cbox = False
    if pathfile.endswith(".box"):
        boxes = CoordsIO.read_eman1_boxfile(path=pathfile, is_SPA=True,box_size_default=200)
    if pathfile.endswith(".star"):
        boxes = CoordsIO.read_star_file(path=pathfile, box_size=controller.model.boxsize)
    if pathfile.endswith(".cbox"):
        boxes = CoordsIO.read_cbox_boxfile(path=pathfile,min_dist_boxes_filament=0)
        print(f"loading {time.time() - t_start}")
        controller.model.is_cbox = True
        if boxes:
            if not _check_correct_import_data(controller=controller,keep=keep, boxes=boxes):
                return list()

            controller.model.has_filament = isinstance(boxes[0], utils.Filament)
            b = boxes[0].boxes[0] if controller.model.has_filament else boxes[0]
            sketch = box_to_sketch(controller=controller, box=b, color=None)
            helper_image.box_size_changed(controller=controller, box_size_from_file=sketch.get_width())
            controller.model.est_box_from_cbox = sketch.get_est_size()
            controller.model.box_dictionary.update_boxsize_dictionary(new_boxsize=sketch.get_width(),f=path.splitext(pathfile)[0].split("/")[-1], n=controller.model.index_tomo)
    return boxes


def _collect_filament(controller:boxmanager_controller, filaments:List[utils.Filament], dict_entry_name:str, keep:bool)->int:
    """
    Collect the filament, set all the 'filaments'' variables and return the number of collected filaments
    :param controller: controller
    :param filaments: list of filaments
    :param dict_entry_name: filename  file filename in case of SPA, tomo filename in case of folder
    """

    colour = "r"
    colors_ = ["b", "r", "c", "m", "y", "k", "w"]
    is_tomo = controller.model.type_case in [constants.Type_case.TOMO.value, constants.Type_case.TOMO_FOLDER.value]

    # i need to fix these 2 internal vars to be able to create the 3D values
    controller.model.box_dictionary.has_filament = True
    controller.model.box_dictionary.is_3D = not helper.is_cbox_untraced(b=filaments[0].boxes[0]) if is_tomo and filaments[0] and filaments[0].boxes[0] else False

    for fil_id, fil in enumerate(filaments):
        rects_ = []
        # load the boxes, because the filament could be curvy
        if fil.boxes:

            # in case of multiple import we want to have all the 'new' filament with a given color
            if keep:
                new_rand_color="b"
            else:
                new_rand_color = random.choice(colors_)
                while new_rand_color == colour:
                    new_rand_color = random.choice(colors_)
                colour = new_rand_color
            rects_.extend([box_to_sketch(controller,box, new_rand_color) for box in fil.boxes])

            # load the filament data, we will transform the curvy filaments in straight lines
            box_size = fil.boxes[0].w
            offset = box_size / 2  # for convertion cryolo.BBox to MySketch obj
            filament=helper_filament.picked_filament(box_size=box_size, is_tomo=is_tomo)
            filament.begin_fil = [fil.boxes[0].x + offset, fil.boxes[0].y + offset]
            filament.end_fil = [fil.boxes[-1].x + offset, fil.boxes[-1].y + offset]

            #fill the box_dictionary.filament2D
            z = int(fil.boxes[0].z) if is_tomo else None
            id_fil = controller.model.box_dictionary.add_picked_filament(fil=filament.get_rect_sketch(color=new_rand_color),
                                                                         f=dict_entry_name, n=z,still_picking=False)
            # fill the box_dictionary.particle2D
            controller.model.box_dictionary.add_sketches(
                sketches=rects_, f=dict_entry_name,n=z, id_fil=id_fil, colour=new_rand_color)
            controller.model.box_dictionary.update_boxsize_dictionary(new_boxsize=box_size, f=dict_entry_name, n=z)
    controller.model.box_dictionary.has_filament=True
    controller.model.has_filament = True
    return len(filaments)

def import_SPA(controller:boxmanager_controller, box_dir:str, keep:bool)->None:
    """
    Import the boxes from files in the SPA case
    :param controller: Boxmanager_controller obj
    :param box_dir: path to the folder contains the files
    :param keep: False if we want to discard the data
    """
    t_start = time.time()
    box_imported, filaments_imported = 0, 0
    boxes = list()
    updated_entries = list()
    dict_entry_name = None

    if not path.isdir(box_dir):
        fname=path.splitext(path.basename(box_dir))
        onlyfiles = [fname[0]+fname[1]]
        box_dir = path.dirname(controller.model.box_dir)
    else:
        onlyfiles = [
            f for f in listdir(box_dir)
            if path.isfile(path.join(box_dir, f))
               and not f.startswith(".")
               and path.splitext(f)[0] in helper.get_all_loaded_filesnames(root=controller.view.tree.invisibleRootItem().child(0))
               and (
                       f.endswith(".box")
                       or f.endswith(".txt")
                       or f.endswith(".star")
                       or f.endswith(".cbox")
               )
        ]

    if not onlyfiles:
        return

    if keep is False:
        rand_color = "r"
    else:
        #self.convert_boxdict_rect_to_list_square()
        rand_color = random.choice(COLORS)
        while rand_color == "r":
            rand_color = random.choice(COLORS)

    pd = controller.view.create_progress_dialog(title="Load box files...")
    pd.show()

    star_dialog_was_shown = False
    is_star_startend = False

    controller.view.is_updating_params = True
    for file_index, f in enumerate(onlyfiles):
        pd.setValue(int((file_index + 1) * 100 / len(onlyfiles)))
        controller.view.run_in_same_thread()

        pathfile = path.join(box_dir, f)

        is_helicon = CoordsIO.is_eman1_helicon(path=pathfile)
        is_eman1_startend = CoordsIO.is_eman1_filament_start_end(path=pathfile) if not is_helicon else False
        if not is_helicon and not is_eman1_startend:
            if not star_dialog_was_shown and f.endswith(".star"):
                is_star_startend =  controller.view.qtmessage( msg="Are the star files containing filament coordinates (start/end)?",
                                has_cancel=False) == controller.view.clicked_yes()
                star_dialog_was_shown = True

        # if the file is empty i want just to check the related checkbox
        if os_stat(path.join(box_dir, f)).st_size == 0:
            dict_entry_name = _update_entries_empty_file(f=f, updated_entries=updated_entries, is_star_startend=is_star_startend, is_helicon=is_helicon, is_eman1_startend=is_eman1_startend)
            continue

        if any([is_helicon, is_eman1_startend, is_star_startend]):
            filaments = list()
            dict_entry_name = f[:-4]
            if is_helicon:
                filaments = CoordsIO.read_eman1_helicon(pathfile)
            elif is_eman1_startend:
                filaments = CoordsIO.read_eman1_filament_start_end(pathfile)
            elif is_star_startend:
                print(f"Read filaments {pathfile}")
                filaments = CoordsIO.read_star_filament_file(
                    path=pathfile, box_width=100
                )
                dict_entry_name = f[:-5]
            filaments_imported += _collect_filament(controller,filaments, dict_entry_name, keep)
        else:
            # here it loads the filaments (from .cbox) as list of boxes too
            boxes = _load_data(controller=controller, pathfile=pathfile, keep=keep, t_start=t_start)


        dict_entry_name = path.splitext(f)[0]
        if controller.model.is_cbox and controller.model.has_filament:
            filaments_imported += _collect_filament(controller,boxes,dict_entry_name,keep)
        elif not controller.model.has_filament:
            sketches = [box_to_sketch(controller=controller,box=box, color=rand_color) for box in boxes]
            box_imported += len(sketches)
            controller.model.box_dictionary.add_sketches(sketches=sketches, f=dict_entry_name, n=controller.model.index_tomo, id_fil=None)
            # the 'boxsize_dictionary' and 'visualization_dictionary' ll be fill in real time

        updated_entries.append(dict_entry_name)

    # i have to set th boxesize to the GUI, in particle is done into _load_data
    if controller.model.has_filament and controller.model.rectangles:
        helper_image.box_size_changed(controller=controller, box_size_from_file=controller.model.rectangles[0].get_width())

    controller.view.set_checkstate_tree_leafs(item=controller.view.tree.invisibleRootItem(), entries=updated_entries, state=controller.view.checkbox_state_value(checked=True))

    print(f"Total time {time.time() - t_start}")
    print(f"Total imported filaments: {filaments_imported}" if controller.model.has_filament else f"Total imported particles: {box_imported}")

    if pd:
        pd.close()

    controller.view.is_updating_params = False
    return


def import_tomo_folder(controller:boxmanager_controller, box_dir:str, keep:bool)->None:
    """
    Import the boxes from files in the tomo folder case
    :param controller: Boxmanager_controller obj
    :param box_dir: path to the folder contains the files
    :param keep: False if we want to discard the data
    """
    controller.model.is_cbox = False
    controller.model.is_cbox_untraced = False
    #self.eman_3D = False
    onlyfiles = [
        f for f in listdir(box_dir)
        if path.isfile(path.join(box_dir, f))
           and not f.startswith(".")
           and path.splitext(f)[0] in helper.get_all_loaded_filesnames(root=controller.view.tree.invisibleRootItem().child(0))
           and (
                   f.endswith(".box")
                   or f.endswith(".star")
                   or f.endswith(".cbox")
           )
    ]

    for index,f in enumerate(onlyfiles):
        import_single_tomo(controller=controller, path_3d_file=path.join(box_dir, path.splitext(f)[0]),index_file=index, keep=keep)
        controller.model.params[path.splitext(f)[0]].box_size = controller.model.boxsize
        controller.view.is_updating_params = True

    # set the boxsize to the current image boxsize
    controller.model.boxsize = controller.model.params[controller.get_current_filename(with_extension=False)].box_size
    controller.view.line_setText(line=controller.view.boxsize_line,value=str(controller.model.boxsize))
    controller.view.is_updating_params = False
    return

def _setting_boxdictionary_vars(controller:boxmanager_controller)->None:
    """
    After importing boxes I have to set the internal var of Box_dictionary obj
    :param controller: Boxmanager_controller obj
    """
    if controller.model.type_case != constants.Type_case.SPA.value:
        controller.model.box_dictionary.has_filament = controller.model.has_filament
        if controller.model.is_cbox:
            controller.model.box_dictionary.is_cbox = True
            controller.model.box_dictionary.is_3D = True
            controller.model.has_3d = True
        if controller.model.is_cbox_untraced:
            controller.model.has_3d = False
            controller.model.box_dictionary.set_untraced_param()


def import_single_tomo(controller:boxmanager_controller, path_3d_file:str, index_file:Union[int,None], keep:bool)->bool:
    """
    Import the boxes of a single tomo from file
    :param controller: Boxmanager_controller obj
    :param path_3d_file: path to the file
    :param index_file: To avoid to overwrite the checked checkbox into controller.view.set_checkstate_tree_leafs, None if not a folder of tomo
    :param keep: False if we want to discard the data
    """
    filaments_imported,box_imported = 0,0
    t_start = time.time()

    filename=path_3d_file.split("/")[-1]
    pd = controller.view.create_progress_dialog(title="Load box files...")
    pd.show()

    controller.view.is_updating_params = True

    if path.isfile(path_3d_file + ".star") is True:
        boxes = CoordsIO.read_star_file(path=path_3d_file + ".star", box_size=controller.model.boxsize)
    elif path.isfile(path_3d_file + ".box") is True:
        boxes = CoordsIO.read_eman1_boxfile(path=path_3d_file + ".box", is_SPA=False, box_size_default=constants.Default_settings_value.DEFAULT_BOX_SIZE.value)
        #self.eman_3D = True
    elif path.isfile(path_3d_file + ".cbox") is True:
        boxes = CoordsIO.read_cbox_boxfile(path=path_3d_file + ".cbox",min_dist_boxes_filament=0)
        if boxes:
            current_filename = path.splitext(path.basename(path_3d_file + ".cbox"))[0]
            if not _check_correct_import_data(controller=controller,keep=keep, boxes=boxes):
                return False
            if isinstance(boxes[0], utils.Filament):
                filaments_imported += _collect_filament(controller=controller,filaments=boxes,dict_entry_name=current_filename,keep=keep)
                controller.model.has_filament = True
            if boxes[0]:
                b = boxes[0].boxes[0] if controller.model.has_filament else boxes[0]
                vis = constants.Visualization_cb.CIRCLE_SEGMENTED.value if controller.model.has_filament else constants.Visualization_cb.CIRCLE.value
                controller.model.is_cbox = not helper.is_cbox_untraced(b=b)
                controller.model.has_3d = controller.model.is_cbox
                controller.model.is_cbox_untraced = helper.is_cbox_untraced(b=b)
                sketch = box_to_sketch(controller=controller, box=b, color=None)
                controller.model.est_box_from_cbox = sketch.get_est_size(circle=False)
                box_size =sketch.get_width()
                helper_image.box_size_changed(controller=controller, box_size_from_file=box_size)
                for z in controller.model.box_dictionary.boxsize_dictionary[controller.get_current_filename(with_extension=False)]:
                    controller.model.box_dictionary.update_boxsize_dictionary(new_boxsize=box_size,f=current_filename,n=z)
                    controller.model.box_dictionary.update_visualization_dictionary(new_visualization=vis, f=current_filename,n=z)
    else:
        controller.view.err_message(msg=f"Error: '{path_3d_file}' is not valid .star, .box or .cbox files")
        pd.close()
        return False

    # set cbox and filament vars into the model.box_dictionary var
    if controller.model.type_case != constants.Type_case.SPA.value:
        _setting_boxdictionary_vars(controller=controller)

    if keep is False:
        rand_color = "r"
    else:
        rand_color = random.choice(["b", "c", "m", "y", "k", "w"])

    if not controller.model.has_filament :
        for box in boxes:
            sketch = box_to_sketch(controller=controller, box=box, color=rand_color)
            box_imported += 1
            controller.model.box_dictionary.add_sketch(sketch=sketch, f=filename, n=int(box.z))

    updated_entries = [str(int(z)) for z in CoordsIO.read_cbox_include_list(path=path_3d_file + ".cbox")]
    item =  controller.view.tree.invisibleRootItem().child(0).child(index_file) if index_file is not None else controller.view.tree.invisibleRootItem()
    controller.view.set_checkstate_tree_leafs(item=item, entries=updated_entries, state=controller.view.checkbox_state_value(checked=True))

    print(f"Total time {time.time() - t_start}")
    print(f"Total imported filaments: {filaments_imported}" if controller.model.has_filament else f"Total imported particles: {box_imported}")

    pd.close()
    controller.view.is_updating_params = False
    return True

def import_data(controller:boxmanager_controller)->None:
    if not controller.model.box_dictionary or (controller.model.unsaved_changes and controller.view.qtmessage(
                                msg="There are unsaved changes. Are you sure?", has_cancel=True) == controller.view.clicked_cancel()):
        return

    # False when we want to discard the boxes already present in boxdictionary
    keep = False
    if not controller.model.box_dictionary.is_empty():
        if controller.view.qtmessage(msg= "Keep old boxes loaded and show the new ones in a different color?",
                                has_cancel=False) == controller.view.clicked_yes():
            keep = True
        else:
            pass
            #self.has_filament = False
            #self.is_cbox_untraced = False


    # i do not need if self.plot is not None or self.is_folder_3D_tomo is True:
    box_dir = controller.view.qt_esixting_folder(msg="Select Box Directory")

    if not box_dir:
        return

    if not keep:
        _remove_old_boxes(controller=controller)

    if keep and controller.model.has_filament:
        controller.model.box_dictionary.set_colors_all(new_color="w")

    if controller.model.type_case == constants.Type_case.SPA.value:
        import_SPA(controller=controller, box_dir=box_dir, keep=keep)
    elif controller.model.type_case == constants.Type_case.TOMO_FOLDER.value:
        import_tomo_folder(controller=controller, box_dir=box_dir, keep=keep)
    else:
        import_single_tomo(controller=controller, path_3d_file=path.join(box_dir, controller.get_current_filename(with_extension=False)), index_file=None, keep=keep)

    kind_of_cbox =controller.model.is_cbox or controller.model.is_cbox_untraced
    controller.view.thresholding_tab_blurring(is_enable=kind_of_cbox, kind_of_cbox=kind_of_cbox, has_filament=controller.model.has_filament,type_case=controller.model.type_case)
    controller.view.tracing_tab_blurring(is_enable=controller.model.is_cbox_untraced,has_filament=controller.model.has_filament)

    controller.view.blur_picking_combobox(has_filament=controller.model.has_filament, is_importing=True)

    if kind_of_cbox or controller.model.box_dictionary.has_filament:
        controller.view.set_cbox_visualization(has_filament=controller.model.has_filament)
    # load the boxes present in the current image/slice, boxsize and visualization get from GUI (already saved in the model)
    controller.model.rectangles = controller.model.box_dictionary.get_sketches(
                                f=controller.get_current_filename(with_extension=False), n=controller.model.index_tomo, is_3D=controller.model.has_3d, is_tracing = False)

    # restore the canvas
    if controller.view.background_current:
        controller.view.fig.canvas.restore_region(controller.view.background_current)

    # draw the sketches present in the current image/slice
    helper_image.draw_all_patches(controller=controller)
    controller.view.fig.canvas.blit(controller.view.ax.bbox)

    # update counters
    controller.view.update_tree_boxsizes( update_current=False,all_tomos=True)
    controller.view.update_all_global_counters()

    # in case of cbox filament some options are not available
    if controller.model.has_filament:
        controller.view.blur_estimated_size()
        if not controller.model.is_cbox_untraced:
            box_dist = controller.model.box_dictionary.set_box_distance_dict_after_import()
            controller.model.box_distance_filament = box_dist
            controller.view.line_setText(line=controller.view.box_distance_filament_line, value=str(box_dist))