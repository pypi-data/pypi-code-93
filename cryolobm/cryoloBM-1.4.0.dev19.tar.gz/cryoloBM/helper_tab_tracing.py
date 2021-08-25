from cryoloBM import constants, helper_GUI, helper, visualization_3D_Window
from cryolo import grouping3d,  utils

from cryoloBM import boxmanager_controller, MySketch # for type hinting purpose
from typing import List, Union

def check_and_run_preview(controller:boxmanager_controller, only_reload:bool)->None:
    """
    :param controller: Boxmanager_controller obj
    :param only_reload: If True it plot the result on the current image
    """
    if controller.view.preview_is_on and not controller.model.has_filament:
        preview_run(controller=controller,only_reload=only_reload)

def searchRange_changed(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    controller.model.trace_all = False
    purefilename = controller.get_current_filename(with_extension=False)
    value = int(controller.view.search_range_slider.value())
    try:
        if 0 <= value < controller.model.smallest_image_dim[purefilename] - 1:
            controller.model.search_range = value
        else:
            controller.view.err_message(msg= f"the value has to be in [0 - {controller.model.smallest_image_dim[purefilename] - 1}]")
        if not controller.view.is_updating_params and controller.model.type_case == constants.Type_case.TOMO_FOLDER.value and not controller.view.is_slider_pressed:
            update_all =controller.view.apply_to_all_the_tomo_question( name_param = "Search range") == controller.view.clicked_yes()
            if update_all:
                controller.model.trace_all = True
                for p in controller.model.params.values():
                    p.search_range = controller.model.search_range
            else:
                controller.model.params[purefilename].search_range = controller.model.search_range
    except ValueError:
        return

    controller.view.line_setText(line=controller.view.search_range_line,value=str(controller.model.search_range))
    check_and_run_preview(controller=controller,only_reload=True)

def searchRange_label_changed(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    try:
        purefilename = controller.get_current_filename(with_extension=False)
        new_value = int(controller.view.search_range_line.text())
        if new_value > controller.model.smallest_image_dim[purefilename] or new_value < 0:
            return
    except ValueError:
        return
    controller.model.search_range = new_value
    controller.view.search_range_slider.setValue(new_value)
    check_and_run_preview(controller=controller, only_reload=True)

def memory_changed(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    controller.model.trace_all = False
    purefilename = controller.get_current_filename(with_extension=False)
    value = int(controller.view.memory_slider.value())
    try:
        if 0 <= value < controller.model.tot_frames[purefilename] - 1:
            controller.model.memory = value
        else:
            controller.view.err_message(msg=f"the value has to be in [0 - {controller.model.tot_frames[purefilename] - 1}]")

        if not controller.view.is_updating_params and controller.model.type_case == constants.Type_case.TOMO_FOLDER.value and not controller.view.is_slider_pressed:
            update_all =controller.view.apply_to_all_the_tomo_question( name_param = "Memory") == controller.view.clicked_yes()
            if update_all:
                controller.model.trace_all = True
                for p in controller.model.params.values():
                    p.memory = controller.model.memory
            else:
                controller.model.params[purefilename].memory = controller.model.memory
    except ValueError:
        return

    controller.view.line_setText(line=controller.view.memory_line, value=str(controller.model.memory))
    check_and_run_preview(controller=controller,only_reload=True)

def memory_label_changed(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    try:
        purefilename = controller.get_current_filename(with_extension=False)
        new_value = int(controller.view.memory_line.text())
        if new_value > controller.model.smallest_image_dim[purefilename] or new_value < 0:
            return
    except ValueError:
        return
    controller.model.memory = new_value
    controller.view .memory_slider.setValue(new_value)
    check_and_run_preview(controller=controller,only_reload=True)

def min_length_changed(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    purefilename = controller.get_current_filename(with_extension=False)
    controller.model.trace_all = False
    value = int(controller.view.min_length_slider.value())
    try:
        if 0 <= value < controller.model.tot_frames[purefilename] - 1:
            controller.model.min_length = value
        else:
            controller.view.err_message(msg=f"the value has to be in [0 - {controller.model.tot_frames[purefilename] - 1}")

        if not controller.view.is_updating_params and controller.model.type_case == constants.Type_case.TOMO_FOLDER.value and not controller.view.is_slider_pressed:
            update_all = controller.view.apply_to_all_the_tomo_question(name_param="Minimum length") == controller.view.clicked_yes()
            if update_all:
                controller.model.trace_all = True
                for p in controller.model.params.values():
                    p.min_length = controller.model.min_length
            else:
                controller.model.params[purefilename].min_length = controller.model.min_length
    except ValueError:
        return

    controller.view.line_setText(line=controller.view.min_length_line, value=str(controller.model.min_length))
    check_and_run_preview(controller=controller,only_reload=True)

def min_length_label_changed(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    try:
        purefilename = controller.get_current_filename(with_extension=False)
        new_value = int(controller.view.min_length_line.text())
        if new_value > controller.model.smallest_image_dim[purefilename] or new_value < 0:
            return
    except ValueError:
        return
    controller.model.min_length = new_value
    controller.view.min_length_slider.setValue(new_value)
    check_and_run_preview(controller=controller, only_reload=True)

def min_edge_weight_changed(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    purefilename = controller.get_current_filename(with_extension=False)
    controller.model.trace_all = False
    try:
        controller.model.min_edge_weight = float(controller.view.min_edge_weight_slider.value()) / 100

        if not controller.view.is_updating_params and controller.model.type_case == constants.Type_case.TOMO_FOLDER.value and not controller.view.is_slider_pressed:
            update_all = controller.view.apply_to_all_the_tomo_question(name_param="Minimum edge weigh") == controller.view.clicked_yes()
            if update_all:
                controller.model.trace_all = True
                for p in controller.model.params.values():
                    p.min_edge_weight = controller.model.min_edge_weight
            else:
                controller.model.params[purefilename].min_edge_weight = controller.model.min_edge_weight
    except ValueError:
        return

    controller.view.line_setText(line=controller.view.min_length_line, value=str(controller.model.min_length))
    check_and_run_preview(controller=controller,only_reload=True)

def min_edge_weight_label_changed(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    try:
        old_value = controller.model.min_edge_weight
        new_value = float(controller.view.min_edge_weight_line.text())
        if new_value > 1.0 or new_value < 0:
            controller.view.line_setText(line=controller.view.min_edge_weight_line, value=str(old_value))
            return
    except ValueError:
        return
    controller.model.min_edge_weight = new_value
    controller.view.min_edge_weight_slider.setValue(new_value * 100)

            #this
    #if self.preview_is_on:
    #    self.preview_win.set_list_patches(self.get_patches())
    #    self.preview_win.display_img(self.current_image_path, None, self.index_3D_tomo)

            # or this???
    check_and_run_preview(controller=controller, only_reload=True)

def win_size_changed(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    controller.model.trace_all = False
    purefilename = controller.get_current_filename(with_extension=False)
    value = int(controller.view.win_size_slider.value())
    try:
        if value >= 0:
            controller.model.win_size = value
        else:
            controller.view.err_message(msg=f"the value has to be > 0")

        if not controller.view.is_updating_params and controller.model.type_case == constants.Type_case.TOMO_FOLDER.value and not controller.view.is_slider_pressed:
            update_all =controller.view.apply_to_all_the_tomo_question( name_param = "Window size") == controller.view.clicked_yes()
            if update_all:
                controller.model.trace_all = True
                for p in controller.model.params.values():
                    p.win_size = controller.model.win_size
            else:
                controller.model.params[purefilename].win_size = controller.model.win_size
    except ValueError:
        return

    controller.view.line_setText(line=controller.view.win_size_line, value=str(controller.model.win_size))
    check_and_run_preview(controller=controller,only_reload=True)

def win_size_label_changed(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    try:
        new_value = float(controller.view.win_size_line.text())
        if new_value < 0:
            return
    except ValueError:
        return
    controller.model.win_size = new_value
    controller.view.win_size_slider.setValue(new_value)
    check_and_run_preview(controller=controller, only_reload=True)


def preview(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    if controller.view.is_updating_params:
        return
    if controller.model.current_tomoimage_mmap is None:
        controller.view.err_message(msg="Please open a tomo image or a folder of tomo images first")
        return

    controller.view.preview_is_on = controller.view.preview_checkbox.isChecked()

    if controller.view.preview_is_on:
        preview_run(controller=controller,only_reload = False)

def trace(controller:boxmanager_controller)->None:
    """
    This button traces the particles and show them in the 'preview' 3D windows.
    The button is visible only if 'preview' checkbox is not checked
    :param controller: Boxmanager_controller obj
    """
    if controller.model.current_tomoimage_mmap is None:
        controller.view.err_message(msg="Please open a tomo image or a folder of tomo images first")
        return

    #check the preview checkbox if it is not checked
    if not controller.view.preview_is_on:
        controller.view.is_updating_params = True
        controller.view.check_preview_checkbox(check=True)
        controller.view.is_updating_params = False
        controller.view.preview_is_on = True

    controller.model.trace_all = False
    if controller.model.type_case == constants.Type_case.TOMO_FOLDER.value:
        if controller.view.qtmessage( msg="Do you want to apply the trace to all tomographies?",has_cancel=False) == controller.view.clicked_yes():
            controller.model.trace_all = True
            for p in controller.model.params.values():
                p.memory = controller.model.memory
                p.search_range = controller.model.search_range
                p.min_length = controller.model.min_length
                p.win_size = controller.model.win_size
                p.min_edge_weight = controller.model.min_edge_weight
    preview_run(controller=controller,only_reload = False)

def trace_values(controller:boxmanager_controller, fname:Union[str,None])->List[utils.BoundBox]:
    """
    :param controller: Boxmanager_controller obj
    :param fname: in folder case it is the name of the tomo on which perform the trace, otherwise None
    """
    if fname:
        param = controller.model.params[fname]
    else:
        fname = controller.get_current_filename(with_extension=False)
        param =helper.Params(fname, controller.model.filter_freq,
                             controller.model.boxsize,
                             controller.model.upper_size_thresh,
                             controller.model.lower_size_thresh,
                             controller.model.current_conf_thresh,
                             controller.model.current_num_boxes_thresh,
                             controller.model.min_edge_weight,
                             controller.model.search_range,
                             controller.model.memory,
                             controller.model.min_length,
                             controller.model.boxsize)


    if controller.model.has_filament:
        filament_dict = dict()#todo self.filament_dict[fname] if self.is_folder_3D_tomo else self.filament_dict
        return grouping3d.do_tracing_filaments(filament_dict, param.search_range, param.memory, param.conf_thresh,
                                               param.min_edge_weight, param.win_size)
    else:
        d = grouping3d.do_tracing(controller.model.box_dictionary.get_particle_dictionary_as_bbox(fname) , param.search_range, param.memory, param.conf_thresh, param.min_length)
        if d:
            d = utils.non_maxima_suppress_fast_3d(d, 0.3, param.conf_thresh)
    return d

def display_preview(controller:boxmanager_controller, only_reload:bool)->None:
    """
    Displays the results of the tracing.
    It is used in the confidence thresholding too, where i have just to filter the data
        :param controller: Boxmanager_controller obj
    :param only_reload: If True it show the result on the current image
    """
    patches = get_patches(controller=controller)
    if not controller.view.preview_win:
        # I should not be here after changing a threshold option
        controller.view.preview_win = visualization_3D_Window.PreviewWindow(controller.view.font, patches)
        only_reload = False
    else:
        controller.view.preview_win.set_list_patches(patches)

    if only_reload:
        controller.view.preview_win.reload_img()
    else:
        img = controller.model.current_tomoimage_mmap[controller.model.index_tomo, :, :]
        controller.view.preview_win.display_img(controller.get_current_filename(with_extension=True), img, controller.model.index_tomo)

def preview_run(controller, only_reload = False)->None:
    """
    This function will collect the params, run the tracing and show the result
    :param controller: Boxmanager_controller obj
    :param only_reload: If True it show the result on the current image
    """
    purefilename = controller.get_current_filename(with_extension=False)

    # run trace and convert the results from bboxes to sketches and save them into box_dictionary.box_dict_traced
    if controller.model.trace_all:
        for f in [*controller.model.box_dictionary.box_dict_traced]:
            controller.model.box_dictionary.box_dict_traced[f] = helper.convert_list_bbox_to_sketch(boxes_list=trace_values(controller=controller, fname=f),out_dict=True,col='r',fil_id=None)
    else:
        res = trace_values(controller=controller, fname=None)
        controller.model.box_dictionary.box_dict_traced[purefilename] =helper.convert_list_bbox_to_sketch(boxes_list=res,out_dict=True,col='r',fil_id=None)


    if not controller.model.has_filament:
        controller.model.box_dictionary.create_traced_3D()
    else:
        pass
        """
        if self.is_folder_3D_tomo:
            for f in [*self.box_dict_traced]:
                self.box_dictionary_3D_view.update({f: dict()})
                self.convert_filamentList_to_box_dictionary(self.box_dictionary_3D_view, self.box_dict_traced[f], f)
        else:
            self.convert_filamentList_to_box_dictionary(self.box_dictionary_3D_view, d)
        """

    display_preview(controller=controller, only_reload=only_reload)


def get_patches(controller:boxmanager_controller)->List[MySketch.MySketch]:
    """
    :param controller: Boxmanager_controller obj
    """
    filename = controller.get_current_filename(with_extension=False)
    use_circle = controller.model.visualization == constants.Visualization_cb.CIRCLE.value
    current_conf_thresh, upper_size_thresh, lower_size_thresh, current_num_boxes_thresh = controller.model.get_threshold_params(filename)
    visible_rects = [box.getSketch(circle =use_circle) for box in controller.model.box_dictionary.get_sketches(f=filename,n=controller.model.index_tomo,is_3D=True,  is_tracing = False) if
                     helper.check_if_should_be_visible(box,current_conf_thresh, upper_size_thresh, lower_size_thresh, current_num_boxes_thresh, is_filament = controller.model.has_filament)]
    return visible_rects