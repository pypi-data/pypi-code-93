from cryoloBM import constants,helper, helper_GUI, MySketch,visualization_3D_Window, helper_tab_tracing, helper_filament
from cryolo import imagereader
from os import path
import numpy as np

from cryoloBM import boxmanager_controller # for type hinting purpose
from typing import Tuple

# EVENT_IMAGE_CHANGED FUNCTIONS
def _check_event_image_changed_validity(controller:boxmanager_controller, root_tree_item:helper_GUI.QtG.QTreeWidgetItem)->bool:
    """
    It is for internal use of 'event_image_changed'. Check if we can change the image
    :param controller: Boxmanager_controller obj
    :param root_tree_item: It is filled in automatic via PyQT
    Return False if we cannot change the image
    """
    if not root_tree_item:
        return False

    cond_true = [ controller.view.current_image_path, root_tree_item.childCount() == 0,
                 controller.model.type_case != constants.Type_case.NOT_LOADED.value]

    if not all(cond_true):
        return False
    return True

def _get_SPAimg_image_changed(controller:boxmanager_controller, old_filename:str)->Tuple[bool,np.ndarray]:
    """
    It is for internal use of 'event_image_changed'. Check if the new image has a different size
    it could happen that in a SPA case the micrographs have different size
    :param controller: Boxmanager_controller obj
    :return new_size_img: True if the size
    """
    prev_size = imagereader.read_width_height(image_path=path.join(controller.model.image_folder_path,old_filename))
    img = helper.read_image(file_path=controller.model.current_image_path, use_mmap=False)

    if prev_size[::-1] == img.shape:
        return False, img
    return True, img

def _set_and_update_boxdictionary_image_changed(controller:boxmanager_controller)->None:
    """
    When we open an image:
        -) the Boxdictionary's dictionaries has to be set
        -) the controller.model.rectangles has to be synchronized to the appropriate boxdictionary.boxdictionary entry
    :param controller: Boxmanager_controller obj
    """
    current_filename = controller.get_current_filename(with_extension=False)

    # if it is the first time we visualize the image we have to init boxsize_dictionary and visualization_dictionary
    if controller.model.box_dictionary.has_same_boxsize(boxsize=None, f=current_filename, n=controller.model.index_tomo):
        controller.model.box_dictionary.update_boxsize_dictionary(new_boxsize=controller.model.boxsize,
                                                                  f=current_filename, n=controller.model.index_tomo)
        controller.model.box_dictionary.update_visualization_dictionary(new_visualization=controller.model.visualization,
                                                                        f=current_filename, n=controller.model.index_tomo)

    # update the visualization
    if not controller.model.box_dictionary.has_same_visualization(visualization=controller.model.visualization,
                                                                  f=current_filename, n=controller.model.index_tomo):
        controller.model.box_dictionary.update_visualization_dictionary(
            new_visualization=controller.model.visualization,f=current_filename, n=controller.model.index_tomo)

    # load the sketches present in the current image/slice. If i need i resize them
    # NB the untraced cbox sketches are treat as 2D particle
    if not controller.model.is_cbox_untraced and  controller.model.box_dictionary.has_same_boxsize(boxsize=controller.model.boxsize, f=current_filename, n=controller.model.index_tomo):
        controller.model.rectangles = controller.model.box_dictionary.get_sketches(f=current_filename,
                                                        n=controller.model.index_tomo, is_3D =controller.model.has_3d,  is_tracing = False)
    else:
        controller.model.rectangles = controller.model.box_dictionary.resized_and_get_sketches(
            new_boxsize=controller.model.boxsize, f=current_filename, n=controller.model.index_tomo,use_estimated_size=controller.model.use_estimated_size)

    # When we load the filament, their particles have different size hence we do not want to lose these info and we do not allow to change the box distamce
    if controller.model.visualization in [constants.Visualization_cb.CIRCLE_SEGMENTED.value,constants.Visualization_cb.RECT_FILAMENT_SEGMENTED.value] and \
            (not controller.model.box_dictionary.has_same_box_distance(box_distance=controller.model.box_distance_filament, f=current_filename, n=controller.model.index_tomo) or controller.model.has_3d):
        controller.model.rectangles =controller.model.box_dictionary.change_box_distance(new_box_distance=controller.model.box_distance_filament, f=current_filename, n=controller.model.index_tomo)
    return

def event_image_changed(controller:boxmanager_controller, root_tree_item:helper_GUI.QtG.QTreeWidgetItem)->None:
    """
    Manage the 'image changes' event. It is called when we click on a micrograph's filename (or slice of a tomo)
    in the main window
    Change the displayed image and set all the internal vars
    :param controller: Boxmanager_controller obj
    :param root_tree_item: It is filled in automatic via PyQT
    """
    not_the_same_tomo = False  # var used to close the preview win (trace option) in tomo folder case
    if not _check_event_image_changed_validity(controller=controller, root_tree_item=root_tree_item):
        return

    # i do not need to call h_keypress() but only reset its related flag
    if controller.model.toggle:
        controller.model.toggle = False

    controller.view.current_tree_item = root_tree_item
    previous_filename = controller.get_current_filename(with_extension = True)

    # delete the patches present in the previous image/slice and load the patches present in the current one
    # they are already present in controller.model.rectangle
    if controller.model.box_dictionary:
        delete_all_patches(controller=controller)

        # set vars to identify current image/slice
        if controller.model.type_case == constants.Type_case.SPA.value:
            helper.set_current_image_path(controller=controller, current_image_path=path.join(controller.model.image_folder_path,
                                                    str(controller.view.current_tree_item.text(0))))
        else:
            if controller.model.type_case == constants.Type_case.TOMO_FOLDER.value:
                helper.set_current_image_path(controller=controller,
                                              current_image_path= path.join(controller.model.image_folder_path,root_tree_item.parent().text(0)))
            # set tomo vars
            controller.model.index_tomo = int(controller.view.current_tree_item.text(0))
            controller.model.last_index_tomo = controller.model.index_tomo

        # update the boxdictionary's dictionaries and set controller.model.rectangles
        _set_and_update_boxdictionary_image_changed(controller=controller)

    # it could happen that in a SPA case the micrographs have different size
    new_size_img = False

    if controller.model.type_case == constants.Type_case.SPA.value:
        title = controller.get_current_filename(with_extension = True)

        new_size_img,img = _get_SPAimg_image_changed(controller=controller, old_filename=previous_filename)

    else:
        if controller.model.type_case == constants.Type_case.TOMO.value:
            pass
        else:
            if previous_filename != controller.get_current_filename(with_extension = True):
                not_the_same_tomo = True
                pure_filename =controller.get_current_filename(with_extension = False)
                controller.view.memory_slider.setMaximum(controller.model.tot_frames[pure_filename] - 1)
                controller.view.min_length_slider.setMaximum(controller.model.tot_frames[pure_filename] - 1)
                controller.view.search_range_slider.setMaximum(controller.model.smallest_image_dim[pure_filename] - 1)
                controller.model.current_tomoimage_mmap = helper.read_image(file_path=controller.model.current_image_path, use_mmap=True)
                helper.load_tomo_params(controller=controller,pure_filename=pure_filename)

        img = controller.model.current_tomoimage_mmap[controller.model.index_tomo, :, :]
        title = f"{controller.get_current_filename(with_extension=True)} \tslice: {controller.model.index_tomo}"

    # set image properties and show it
    if new_size_img:
        controller.view.im = controller.view.ax.imshow(img, origin="lower", cmap="gray", interpolation="Hanning")
    else:
        controller.view.im.set_data(img)
    controller.view.setWindowTitle_viewPlot(title=title)
    controller.view.fig.canvas.draw()
    controller.view.background_current = controller.view.fig.canvas.copy_from_bbox(controller.view.ax.bbox)
    controller.view.background_current_onmove = controller.view.background_current

    # draw the sketches present in the current image/slice
    if controller.model.rectangles:
        draw_all_patches(controller=controller)

    if controller.view.preview_win and controller.view.preview_win.is_visible():
        if not_the_same_tomo:
            controller.view.preview_win.plot.close()
            if controller.model.box_dictionary.box_dict_traced[controller.get_current_filename(with_extension = True)]:
                controller.view.preview_win = visualization_3D_Window.PreviewWindow(controller.view.font, helper_tab_tracing.get_patches(controller))
                controller.view.preview_win.display_img(controller.get_current_filename(with_extension = False), img, controller.model.index_tomo)
        else:
            controller.view.preview_win.set_list_patches(helper_tab_tracing.get_patches(controller))
            controller.view.preview_win.display_img(controller.get_current_filename(with_extension = False), img, controller.model.index_tomo)



# ONCLICK FUNCTIONS
def _check_onclick_validity(controller:boxmanager_controller, event:helper_GUI.plt_qtbackend)->bool:
    """
    It is for internal use of 'onclick'. Check if we can interact, drawing or deleting sketch, to the image
    :param controller: Boxmanager_controller obj
    :param event: the click event
    Return False if we cannot interact with the image
    """
    if controller.view.plot and controller.view.plot.toolbar:
        # in case we are using the toolbar for zoom or pan
        return not controller.view.plot.toolbar.mode in ["zoom rect","pan/zoom"]

    if controller.model.has_filament and controller.model.has_3d:
        # We loaded traced filaments
        controller.view.err_message(msg="Picking is disabled.")
        return False

    if controller.model.has_filament and controller.model.visualization != constants.Visualization_cb.RECT_FILAMENT_START_END.value:
        controller.view.err_message( msg="Only the 'Rectangle (Filament Start-end)' visualization is enabled when picking filaments")
        return False

    if event.xdata is None or event.ydata is None or event.xdata < 0 or event.ydata < 0:
        controller.view.err_message( msg="Picked out of the image")
        return False
    return True

def onclick(controller,event:helper_GUI.plt_qtbackend)->None:
    """
    It is called when we click on the image
    :param controller: Boxmanager_controller obj
    :param event: the click event
    """

    controller.model.has_filament = controller.view.get_picking_filament_cb_text() == constants.Picking_cb.FILAMENT.value
    is_tomo = controller.model.type_case in [constants.Type_case.TOMO.value, constants.Type_case.TOMO_FOLDER.value]

    if not _check_onclick_validity(controller=controller, event=event):
        return

    # after starting picking is not possible to switch from picking box and filament. you have to reset
    controller.view.blur_picking_combobox(has_filament=controller.model.has_filament, is_importing=False)

    y = event.ydata - controller.model.boxsize / 2
    x = event.xdata - controller.model.boxsize / 2

    # load the sketches present in the current image (or slice)
    pure_filename = controller.get_current_filename(with_extension=False)
    controller.model.rectangles = controller.model.box_dictionary.get_sketches(f=pure_filename,
                                                                               n=controller.model.index_tomo,
                                                                               is_3D=controller.model.has_3d,  is_tracing = False)

    if controller.model.has_filament:

        if controller.view.control_modifier_is_clicked():
            remove_picked_filament(controller=controller, x=event.xdata, y=event.ydata,f=pure_filename, n=controller.model.index_tomo)
            # check or uncheck the related checkbox
            controller.view.check_item_checkbox(item=controller.view.tree.selectedItems()[0], check=len(controller.model.rectangles) > 0)
            return
        """

        # if we load from file and we want to add filament we have to insert the loaded filament in the picked_filament_list
        if self.picked_filament_list == list():
            if self.is_folder_3D_tomo and pure_filename in self.picked_filament_dictionary and self.index_3D_tomo in \
                    self.picked_filament_dictionary[pure_filename]:
                self.picked_filament_list = self.picked_filament_dictionary[pure_filename][self.index_3D_tomo]
            elif self.is_folder_3D_tomo is False and pure_filename in self.picked_filament_dictionary:
                self.picked_filament_list = self.picked_filament_dictionary[pure_filename]
            self.picked_filament_as_rect_dictionary = [fil.get_rect_sketch() for fil in self.picked_filament_list]
        """
        controller.model.current_pick_filament = helper_filament.picked_filament(box_size=controller.model.boxsize, is_tomo=is_tomo)
        controller.model.current_pick_filament.set_first(event=event)
        controller.view.check_item_checkbox(item=controller.view.tree.selectedItems()[0], check=True)
        controller.model.box_dictionary.add_picked_filament(still_picking=True,
                                                            fil = controller.model.current_pick_filament.get_rect_sketch(),
                                                            f = controller.get_current_filename(with_extension=False), n = controller.model.index_tomo)

        return

    box = helper.get_corresponding_box(x=x, y=y, get_low=False,
                                       rectangles=controller.model.rectangles,
                                       current_conf_thresh=controller.model.current_conf_thresh,
                                       box_size=controller.model.boxsize
                                       )

    if controller.view.control_modifier_is_clicked() or controller.view.meta_modifier_is_clicked():
        delete_box(controller=controller,box=box,f=pure_filename, n=controller.model.index_tomo)
    else:
        if controller.model.has_3d and box and box.only_3D_visualization:
            _, index = controller.model.box_dictionary.get_central_n(id_part=box.id,
                                                                       f=pure_filename, n=controller.model.index_tomo)
            controller.view.err_message(msg= f"for moving the box you have to click on its center, that is in slice number '{ index}'")
            return
        controller.model.moving_box = box
        if not controller.model.moving_box:
            # Delete lower confidence box if available
            box = helper.get_corresponding_box(x=x, y=y, get_low=True,
                                               rectangles=controller.model.rectangles,
                                               current_conf_thresh=controller.model.current_conf_thresh,
                                               box_size=controller.model.boxsize
                                               )
            if box:
                controller.model.rectangles.remove(box)
            # Create new box
            est_size=controller.model.boxsize

            rect = MySketch.MySketch(xy=(x, y), width=controller.model.boxsize, height=controller.model.boxsize,
                                     is_tomo=is_tomo, angle=0.0, est_size=est_size, confidence=1,
                                     only_3D_visualization=False, num_boxes=1, meta=None, z=None,
                                     linewidth=1, edgecolor="r", facecolor="none")

            # update dicts and controller.model.rectangles (it is a reference to controller.model.box_dictionary)
            controller.model.box_dictionary.counter+=1
            rect.id = controller.model.box_dictionary.counter
            controller.model.moving_box = rect
            controller.model.box_dictionary.add_sketch(sketch=rect, f=pure_filename, n=controller.model.index_tomo)

            # Add the patch to the Axes
            use_circle = controller.model.visualization == constants.Visualization_cb.CIRCLE.value
            controller.view.ax.add_patch(rect.getSketch(circle=use_circle))
            controller.view.ax.draw_artist(rect.getSketch(circle=use_circle))
            controller.view.fig.canvas.blit(controller.view.ax.bbox)

    # update_current=false because in case of deletion of 3D particle we could visualize the image where the center does not stay
    controller.view.update_tree_boxsizes(update_current=False, all_tomos=False)
    controller.view.update_global_counter(childid=None)

    controller.model.unsaved_changes = True

    # check or uncheck the related checkbox
    controller.view.check_item_checkbox(item=controller.view.tree.selectedItems()[0], check=len(controller.model.rectangles) > 0)

def is_picking_filament_enable(controller)->bool:
    """
    It is called in onmove and onrelease to detect is picking is enable
    :param controller: Boxmanager_controller obj
    :return False if picking is disabled
    """
    if controller.model.has_filament and controller.model.visualization != constants.Visualization_cb.RECT_FILAMENT_START_END.value:
        # we can pick only in rect-start visualization
        return False
    if controller.model.has_filament and controller.model.has_3d:
        # We cannot pick after importing TRACED filament
        return False
    if controller.view.plot and controller.view.plot.toolbar:
        # in case we are using the toolbar for zoom or pan
        return not controller.view.plot.toolbar.mode in ["zoom rect","pan/zoom"]
    return True


def ondraw(controller, event:helper_GUI.plt_qtbackend)->None:
    """
    It is called when we use the toolbar
    :param controller: Boxmanager_controller obj
    :param event: the click event
    """
    if controller.view.zoom_update:
        controller.view.zoom_update = False
        controller.view.background_current = controller.view.fig.canvas.copy_from_bbox(controller.view.ax.bbox)
        controller.view.background_current_onmove = controller.view.fig.canvas.copy_from_bbox(controller.view.ax.bbox)
        # draw the sketches again
        draw_all_patches(controller=controller)
        controller.view.fig.canvas.blit(controller.view.ax.bbox)

def onmove(controller, event:helper_GUI.plt_qtbackend)->None:
    """
    It is called when we move the cursor over the image
    :param controller: Boxmanager_controller obj
    :param event: the click event
    """
    def create_pointer(xy ):
        """
        When we move a particle this function creates a circle pointer in the middle of the particle.
        Its width size is 20% of the original particle. Max value 40 pixel
        :param xy:  tuple with center of the controller.model.moving_box. (before starting to move it)
        """
        new_rect_width = min(40,int(rect_width / 5))
        xold,yold = xy
        new_xy = (xold - new_rect_width / 2, yold - new_rect_width / 2) if is_circle else (xold + (rect_width - new_rect_width) / 2, yold + (rect_width - new_rect_width) / 2)
        return MySketch.MySketch(xy=new_xy, width=new_rect_width, height=new_rect_width,
                                     is_tomo=False, angle=0.0, est_size=False, confidence=1,
                                     only_3D_visualization=False, num_boxes=1, meta=None, z=None,
                                     linewidth=1, edgecolor="r", facecolor="r")

    if event.inaxes != controller.view.ax or controller.view.control_modifier_is_clicked():
        return

    if not is_picking_filament_enable(controller=controller):
        return

    if event.button == 1:
        if controller.view.get_picking_filament_cb_text() == constants.Picking_cb.PARTICLE.value and controller.model.moving_box:
            # in tomo case i remove the 3D visualization BUT not the 2D original sketch that is represented by  'controller.model.moving_box'
            if controller.model.has_3d and not controller.model.is_moving:
                #remove the whole 3D particle
                controller.model.box_dictionary.delete_3D(id_part=controller.model.moving_box.id,
                                                          f=controller.get_current_filename(False),
                                                          n=controller.model.index_tomo)
                # re insert ONLY its center. the 3D ll be create in the 'onrelease'
                controller.model.box_dictionary.particle3D_dictionary[controller.get_current_filename(with_extension=False)][controller.model.index_tomo].append(controller.model.moving_box)
                controller.model.is_moving = True

            is_circle = controller.model.visualization == constants.Visualization_cb.CIRCLE.value

            rect_width = controller.model.moving_box.getSketch().get_width()
            x = event.xdata - rect_width / 2
            y = event.ydata - rect_width / 2

            # create the pointer
            pointer = create_pointer(controller.model.moving_box.get_xy(circle=is_circle))

            # set the new x,y coordinate for the rectangle sketch
            controller.model.moving_box.getSketch(circle=False).set_x(x)
            controller.model.moving_box.getSketch(circle=False).set_y(y)
            controller.model.moving_box.set_xy((x, y), circle=False)

            # set the new x,y coordinate for the circle sketch
            controller.model.moving_box.getSketch(circle=True).center = (event.xdata, event.ydata)
            controller.model.moving_box.set_xy((event.xdata, event.ydata), circle=True)

            # restore the old background image (without sketches) set in the 'event_image_changed'
            if controller.view.background_current:
                controller.view.fig.canvas.restore_region(controller.view.background_current)

            # Add al the current patches to the Axes. NB: the moving_box is a reference to a box present into this var
            for b in controller.model.rectangles:
                controller.view.ax.add_patch(b.getSketch(circle=is_circle ))
                controller.view.ax.draw_artist(b.getSketch(circle=is_circle ))

            controller.view.ax.add_patch(pointer.getSketch(circle=True))
            controller.view.ax.draw_artist(pointer.getSketch(circle=True))
            controller.view.fig.canvas.blit(controller.view.ax.bbox)
            controller.view.fig.canvas.blit(controller.view.ax.bbox)
            return
        elif controller.view.get_picking_filament_cb_text() == constants.Picking_cb.FILAMENT.value:
            controller.model.current_pick_filament.end_fil = [event.xdata,event.ydata]

            # clean the image removing the patches and save as current background
            delete_all_patches(controller=controller)
            if controller.view.background_current_onmove:
                controller.view.fig.canvas.restore_region(controller.view.background_current_onmove)

            # remove current filament and its center line
            for i in range(len(controller.model.rectangles) - 1, -1, -1):
                if controller.model.rectangles and controller.model.rectangles[i].id in [controller.model.box_dictionary.counter, constants.CENTER_LINE_ID]:
                    del controller.model.rectangles[i]

            # create center_line
            center_line = helper_filament.picked_filament(box_size=1)
            center_line.end_fil = controller.model.current_pick_filament.end_fil
            center_line.begin_fil = controller.model.current_pick_filament.begin_fil
            controller.model.rectangles.append(center_line.get_rect_sketch(sketch_id=constants.CENTER_LINE_ID))
            # fill again the current image with boxes
            controller.model.box_dictionary.add_picked_filament(still_picking=True,
                fil=controller.model.current_pick_filament.get_rect_sketch(),
                f=controller.get_current_filename(with_extension=False), n=controller.model.index_tomo)
            # draw the sketches again
            draw_all_patches(controller=controller)
            controller.view.fig.canvas.blit(controller.view.ax.bbox)


def onrelease(controller,event:helper_GUI.plt_qtbackend)->None:
    """
    It is called when we release the mouse button
    :param controller: Boxmanager_controller obj
    :param event: the click event
    """
    if not is_picking_filament_enable(controller=controller):
        return

    # clean the image removing the patches and save as current background
    delete_all_patches(controller=controller)
    if controller.view.background_current_onmove:
        controller.view.fig.canvas.restore_region(controller.view.background_current_onmove)


    pure_filename=controller.get_current_filename(with_extension=False)
    if controller.view.get_picking_filament_cb_text() == constants.Picking_cb.PARTICLE.value:
        # in tomo case i have to create the 'moving_box' 3D structure
        if controller.model.has_3d and controller.model.is_moving:
            controller.model.is_moving = False
            controller.model.box_dictionary.create_3D(sketch=controller.model.moving_box,
                                                      f=pure_filename,
                                                      n=controller.model.index_tomo)

        controller.model.moving_box = None
    elif not controller.model.removing_picked_filament:
        # remove current center line
        for i in range(len(controller.model.rectangles) - 1, -1, -1):
            if controller.model.rectangles and controller.model.rectangles[i].id == constants.CENTER_LINE_ID:
                del controller.model.rectangles[i]
                break

        controller.model.box_dictionary.add_sketches(sketches=controller.model.current_pick_filament.get_sketches(box_distance=controller.model.box_distance_filament, as_bbox=False, z=controller.model.index_tomo),
                                                     f=pure_filename, n=controller.model.index_tomo, id_fil=controller.model.box_dictionary.counter)
        #update the total counter
        controller.model.box_dictionary.update_counter(n=1)

    # draw the sketches again
    draw_all_patches(controller=controller)
    controller.view.fig.canvas.blit(controller.view.ax.bbox)
    # update the counters
    controller.view.update_tree_boxsizes()
    controller.view.update_global_counter()
    controller.model.removing_picked_filament = False

def myKeyPressEvent(controller:boxmanager_controller, event:helper_GUI.plt_qtbackend)->None:
    """
    It is called when we press the keyboard
    :param controller: Boxmanager_controller obj
    :param event: the press keyboard event
    """
    def get_number_current_tomo():
        for index,name in enumerate(controller.model.tot_frames.keys()):
            if name == current_tomo_name:
                return index
        return 0

    if event.name == "key_press_event":
        is_tomo = controller.model.type_case in [constants.Type_case.TOMO.value, constants.Type_case.TOMO_FOLDER.value]
        if event.key == "h":
            h_keypress(controller=controller)
        elif is_tomo and event.key in ["down","up"]:
            current_tomo_name = controller.get_current_filename(with_extension=False)
            controller.model.index_tomo = max(0,controller.model.index_tomo-1) if event.key == "down" else min(controller.model.tot_frames[current_tomo_name]-1,controller.model.index_tomo+1)
            controller.view.setCurrentItem_viewTree(is_tomo_folder=controller.model.type_case == constants.Type_case.TOMO_FOLDER.value, number_tomo=get_number_current_tomo(), z=controller.model.index_tomo)
            event_image_changed(controller=controller,root_tree_item=controller.view.tree.currentItem())


def h_keypress(controller:boxmanager_controller)->None:
    currentfile = controller.get_current_filename(with_extension=False)

    # delete the sktches
    if controller.model.rectangles:
        delete_all_patches(controller=controller)
        controller.view.fig.canvas.draw()
        controller.view.background_current = controller.view.fig.canvas.copy_from_bbox(controller.view.ax.bbox)
    # switch the toggle value
    controller.model.toggle = not controller.model.toggle

    # I have to colelct the data to show
    controller.model.rectangles = list() if controller.model.toggle else controller.model.box_dictionary.get_sketches(
        f=currentfile, n=controller.model.index_tomo, is_3D=controller.model.has_3d,  is_tracing = False)

    # plot the sketches
    if controller.model.rectangles:
        draw_all_patches(controller=controller)
        controller.view.fig.canvas.blit(controller.view.ax.bbox)

def use_estimated_size_changed(controller:boxmanager_controller)->None:
    """
    It changes the value of the "box size" filling the 'box size' line in the visualization tab.
    It is usable only after loading data from cbox file. It gets the new "box size" from these files
    Pay attention: each particle will have its own estimated size
    It is triggered pressing enter (when the cursor is into the line) or button 'set'
    """
    controller.model.use_estimated_size = controller.view.use_estimated_size_checkbox.isChecked()

    # since this optionis basically a resize_box we do not need to run 'h_keypress' or unset toggle flag

    # when we uncheck we resize with the last box_size value
    if not controller.model.use_estimated_size:
        box_size_changed(controller=controller,box_size_from_file=None)

    #remove the old patches, they are already saved in controller.model.rectangles
    if controller.model.rectangles:
        delete_all_patches(controller=controller)
        if controller.view.background_current:
            controller.view.fig.canvas.restore_region(controller.view.background_current)

    # resize the whole 3D dict
    if controller.model.has_3d:
        controller.model.box_dictionary.resize_3D(new_boxsize=controller.model.boxsize, use_estimated_size=True)

    if controller.model.rectangles:
        # collect the data to plot
        if controller.model.has_3d:
            controller.model.rectangles = controller.model.box_dictionary.get_sketches(
                f=controller.get_current_filename(with_extension=False),
                n=controller.model.index_tomo, is_3D=True,  is_tracing = False)
        else:
            controller.model.rectangles = controller.model.box_dictionary.resized_and_get_sketches(
            new_boxsize=controller.model.boxsize, f=controller.get_current_filename(with_extension=False),
                n=controller.model.index_tomo,use_estimated_size=controller.model.use_estimated_size)

        # draw the sketches present in the current image/slice
        draw_all_patches(controller=controller)
        controller.view.fig.canvas.blit(controller.view.ax.bbox)

def box_size_changed(controller:boxmanager_controller, box_size_from_file:int = None)->None:
    """
    It changes the value of the "box size" filling the 'box size' line in the visualization tab.
    It is triggered pressing enter (when the cursor is into the line) or button 'set'
    :param controller: Boxmanager_controller obj
    :param box_size_from_file: Not None when we load from file the boxes and we want to set the value
    """
    # set the boxsize in case we loaded from file (NB: it has nothing to do with estimate size, it is box.w)
    if controller.view.is_updating_params:
        controller.view.is_updating_params=False
        controller.model.boxsize = box_size_from_file
        controller.view.boxsize_line.setText(str(box_size_from_file))
        controller.view.line_setText(line=controller.view.boxsize_line, value=str(box_size_from_file))
        return

    # After clicking 'h' the boxes disappear, before acting i have to untoggle
    if controller.model.toggle:
        h_keypress(controller=controller)

    # if the use_estimated_size checkbox is checked we can change the boxsize as always but we have to uncheck the checkbox
    if controller.model.use_estimated_size:
        controller.view.check_use_estimated_size_checkbox(check=False) # call to 'use_estimated_size_changed'


    old_value = controller.model.boxsize
    try:
        value = int(float(controller.view.boxsize_line.text()))
        if value <= 0:
            controller.view.line_setText(line=controller.view.boxsize_line, value=str(old_value))
            controller.view.err_message(msg="Invalid value. It has to be a positive number")
            return
        controller.model.boxsize = value
    except ValueError:
        controller.view.line_setText(line=controller.view.boxsize_line, value=str(old_value))
        controller.view.err_message( msg="Invalid value. It has to be a positive number")
        return

    current_filename = controller.get_current_filename(with_extension=False)

    # update the params var. Since this is a high consuming time operation we perform it only in the current tomo
    if controller.model.type_case == constants.Type_case.TOMO_FOLDER.value:
        controller.model.params[current_filename].box_size = controller.model.boxsize

    if controller.model.rectangles:
        #remove the old patches, they are already saved in controller.model.rectangles
        delete_all_patches(controller=controller)
        if controller.view.background_current:
            controller.view.fig.canvas.restore_region(controller.view.background_current)

    # resize the whole 3D dict
    if controller.model.has_3d:
        controller.model.box_dictionary.resize_3D(new_boxsize=controller.model.boxsize, use_estimated_size=False)

    if controller.model.rectangles:
        # collect the data to plot
        if controller.model.has_3d:
            controller.model.rectangles = controller.model.box_dictionary.get_sketches(f=controller.get_current_filename(with_extension=False),
                                                                            n=controller.model.index_tomo,is_3D = True,  is_tracing = False)

        elif not controller.model.has_3d or controller.model.is_cbox_untraced:
            controller.model.rectangles = controller.model.box_dictionary.resized_and_get_sketches(new_boxsize=controller.model.boxsize,
                                                                                               f=controller.get_current_filename(with_extension=False),
                                                                                                   n=controller.model.index_tomo,
                                                                                                use_estimated_size=controller.model.use_estimated_size)

        # draw the sketches present in the current image/slice
        draw_all_patches(controller=controller)
        controller.view.fig.canvas.blit(controller.view.ax.bbox)


def box_distance_filament_changed(controller:boxmanager_controller, box_distance:int = 1)->None:
    # After clicking 'h' the boxes disappear, before acting i have to untoggle
    if controller.model.toggle:
        h_keypress(controller=controller)

    old_value=controller.model.box_distance_filament
    try:
        value = int(float(controller.view.box_distance_filament_line.text()))
        if value <= 0:
            controller.view.line_setText(line=controller.view.box_distance_filament_line, value=str(old_value))
            controller.view.err_message(msg="Invalid value. It has to be a positive number")
            return
        controller.model.box_distance_filament = value
    except ValueError:
        controller.view.line_setText(line=controller.view.box_distance_filament_line, value=str(old_value))
        controller.view.err_message( msg="Invalid value. It has to be a positive number")
        return

    if controller.model.rectangles:
        #remove the old patches, they are already saved in controller.model.rectangles
        delete_all_patches(controller=controller)
        if controller.view.background_current:
            controller.view.fig.canvas.restore_region(controller.view.background_current)

    current_filename =controller.get_current_filename(with_extension = False)
    controller.model.box_dictionary.update_box_distance_dictionary(new_box_distance=controller.model.box_distance_filament,f=current_filename,n=controller.model.index_tomo)

    controller.model.rectangles = controller.model.box_dictionary.change_box_distance(new_box_distance=controller.model.box_distance_filament,f=current_filename,n=controller.model.index_tomo, is_tracing=False)

    # draw the sketches present in the current image/slice
    draw_all_patches(controller=controller)
    controller.view.fig.canvas.blit(controller.view.ax.bbox)

def visualization_changed(controller:boxmanager_controller)->None:
    """
    It changes the value of the "visualization_combobox" changing the 'visualization' combobox in the visualization tab.
    It is triggered when the combobox is changed
    """
    # After clicking 'h' the boxes disappear, before acting i have to untoggle
    if controller.model.toggle:
        h_keypress(controller=controller)

    if controller.model.rectangles:
        #remove the old patches (delete_all_patches recognizes the correct visualization), they are already saved in controller.model.rectangles
        delete_all_patches(controller=controller)
        # restore the canvas
        if controller.view.background_current:
            controller.view.fig.canvas.restore_region(controller.view.background_current)

    old_vis = controller.model.visualization
    current_filename = controller.get_current_filename(with_extension=False)
    controller.model.visualization = controller.view.get_visualization_cb_text()
    controller.model.box_dictionary.update_visualization_dictionary(new_visualization=controller.model.visualization,
                                                                    f=current_filename, n=controller.model.index_tomo)

    # If filaments mode i have to set the rectangles
    if controller.model.has_filament and constants.Visualization_cb.RECT_FILAMENT_START_END.value in [old_vis,controller.model.visualization]:
        controller.model.box_dictionary.fil_start_end_vis = controller.model.visualization == constants.Visualization_cb.RECT_FILAMENT_START_END.value
        controller.model.rectangles = controller.model.box_dictionary.get_sketches(f=current_filename,
                                                        n=controller.model.index_tomo, is_3D =controller.model.has_3d,  is_tracing = False)

    # draw again the patches, (draw_all_patches recognizes the correct visualization)
    draw_all_patches(controller=controller)
    controller.view.fig.canvas.blit(controller.view.ax.bbox)

# FILTERING TAB OPTION
def apply_filter(controller:boxmanager_controller)->None:
    """
    It applies the lowpass filter present in filtering tab.
    :param controller: Boxmanager_controller obj
    """
    old_value=controller.model.filter_freq
    try:
        controller.model.filter_freq = float(controller.view.filter_line.text())
    except ValueError:
        controller.view.err_message(msg="Invalid character. The Frequency value has to be a number between 0 and 0.5")
        return

    if 0 <=controller.model.filter_freq < 0.5:
        import cryolo.lowpass as lp
        if controller.model.type_case == constants.Type_case.SPA.value:
            img = lp.filter_single_image(img_path=controller.model.current_image_path,
                                         filter_cutoff=controller.model.filter_freq, resize_to_shape=None)
            im_type = constants.Filetype_name[path.splitext(controller.model.current_image_path)[1].replace(".","").upper()].value
            img = helper.normalize_and_flip(img=img, file_type=im_type)
        else:
            img = helper.read_image(file_path=controller.model.current_image_path, use_mmap=True)
            img = lp.filter_single_image_from_np_array(image=img[controller.model.index_tomo, :, :],
                                                       filter_cutoff=controller.model.filter_freq, resize_to_shape=None,
                                                       channel_specifiction=0)
        img = np.squeeze(img)
        delete_all_patches(controller=controller)
        controller.view.im.set_data(img)
        controller.view.fig.canvas.draw()
        controller.view.background_current = controller.view.fig.canvas.copy_from_bbox(controller.view.ax.bbox)
        draw_all_patches(controller=controller)
    else:
        controller.model.filter_freq = old_value
        controller.view.err_message( msg="Frequency has to be between 0 and 0.5")


# DELETE AND DRAW ON IMAGE FUNCTIONS
def delete_all_patches(controller:boxmanager_controller)->None:
    """
    Deletes all the patches present in current axes
    Since model.rectangle is a reference to a list of particle_dictionary dict it has to fill in the appropriate way
    :param controller: Boxmanager_controller obj
    """

    controller.view.ax.patches=list()

def draw_all_patches(controller:boxmanager_controller)->None:
    """
    Draws all the patches present in model.rectangle var
    Since model.rectangle is a reference to a list of particle_dictionary dict it has to fill in the appropriate way
    :param controller: Boxmanager_controller obj
    """
    current_conf_thresh, upper_size_thresh, lower_size_thresh, current_num_boxes_thresh = controller.model.get_threshold_params(filename=None)
    has_filament = controller.model.picking_combobox_value == constants.Picking_cb.FILAMENT.value
    is_circle = controller.model.visualization in [constants.Visualization_cb.CIRCLE.value,constants.Visualization_cb.CIRCLE_SEGMENTED.value]
    visible_sketches = [box.getSketch(circle=is_circle) for box in controller.model.rectangles if
                     helper.check_if_should_be_visible(box=box, current_conf_thresh=current_conf_thresh, upper_size_thresh=upper_size_thresh, lower_size_thresh=lower_size_thresh,
                                                       num_boxes_thresh=current_num_boxes_thresh, is_filament=has_filament)]

    for sketch in visible_sketches:
        if not sketch.get_visible():
            sketch.set_visible(True)

        controller.view.ax.add_patch(sketch)
        controller.view.ax.draw_artist(sketch)

def delete_box(controller:boxmanager_controller, box:MySketch.MySketch, f:str, n:int)->None:
    """
    Removed the selected box. It is identified via GUI clicking 'ctrl+left_button_mouse' into the box
    Since model.rectangle is a reference to a list of particle_dictionary dict it has to fill in the appropriate way
    :param controller: Boxmanager_controller obj
    :param box: sketch to remove
    :param f: filename
    :param n: number of slice
    """
    if box:
        # delete the current sketches from the figure
        delete_all_patches(controller=controller)

        # restore the canvas
        if controller.view.background_current:
            controller.view.fig.canvas.restore_region(controller.view.background_current)

        # removed the selected sketch from the model.box_dictionary dicts and 'controller.model.rectangles' list
        # in case we do not clicked on the central 2D section of 3D particle we have to calculate the boxes list again
        # in case we do not clicked on the central 2D section of 3D particle we have to calculate the central box
        if controller.model.has_3d and box.only_3D_visualization:
            box, index = controller.model.box_dictionary.get_central_n(id_part=box.id,f=f, n=controller.model.index_tomo)
            boxes = controller.model.box_dictionary.get_sketches(f=f, n=index, is_3D=False,  is_tracing = False)
            controller.model.box_dictionary.delete_sketch_by_index(index=boxes.index(box), f=f, n=index)
            # uncheck the checkbox if there are no more boxes there
            if not boxes:
                controller.view.set_checkstate_tree_leafs(item=controller.view.tree.invisibleRootItem(), entries=[str(index)],
                                      state=controller.view.checkbox_state_value(checked=False))
        else:
            controller.model.box_dictionary.delete_sketch_by_index(index=controller.model.rectangles.index(box),f=f,n=n)

        # draw the sketches again
        draw_all_patches(controller=controller)
        controller.view.fig.canvas.blit(controller.view.ax.bbox)

#todo it is buggy. See tests/test_remove_filament.py
def is_click_into_box(fil:MySketch.MySketch,x:float,y:float,boxsize:int,is_tomo:bool)->bool:
    """
    Return True if thce click (x,y) is into the filament
    :param fil: filamnent MySketch obj
    :param x: x coordinate of the mouse click
    :param y: y coordinate of the mouse click
    :param boxsize: boxsize
    :param is_tomo: True if it is a tomo case
    """
    filament = helper_filament.picked_filament(box_size=boxsize,is_tomo=is_tomo)
    filament.create_from_rect(rect=fil)
    rotated_corners=filament.get_rotated_coordinate_rect()
    rotated_point = filament.get_R() @ np.array((x, y)).T
    max_value = np.amax(rotated_corners,axis=1)
    min_value = np.amin(rotated_corners, axis=1)
    return min_value[0]< rotated_point[0] <max_value[0] and min_value[1]<rotated_point[1]<max_value[1]

def remove_picked_filament(controller:boxmanager_controller, x:float,y:float, f:str, n:int)->None:
    """
    Removed the selected filament. It is identified via GUI clicking 'ctrl+left_button_mouse' into the box
    Since model.rectangle is a reference to a list of particle_dictionary dict it has to fill in the appropriate way
    :param controller: Boxmanager_controller obj
    :param x: coordinate x of the click
    :param y: coordinate y of the click
    :param f: filename
    :param n: number of slice
    """
    controller.model.removing_picked_filament = True
    is_tomo = controller.model.type_case in [constants.Type_case.TOMO.value, constants.Type_case.TOMO_FOLDER.value]
    for index, fil in enumerate(controller.model.rectangles):
        if is_click_into_box(fil,x,y,boxsize=controller.model.boxsize,is_tomo=is_tomo):
            if controller.model.has_filament:
                controller.model.box_dictionary.delete_filemant_by_index(index=index, f=f,n=n)
            else:
                controller.model.box_dictionary.delete_sketch_by_index(index=index, f=f,n=n)
            controller.model.unsaved_changes = True
            # restore the canvas
            if controller.view.background_current:
                controller.view.fig.canvas.restore_region(controller.view.background_current)

            # draw the sketches again
            draw_all_patches(controller=controller)
            controller.view.fig.canvas.blit(controller.view.ax.bbox)

            # update the counters
            controller.view.update_tree_boxsizes(update_current=False)
            controller.view.update_global_counter(childid=None)
            return

