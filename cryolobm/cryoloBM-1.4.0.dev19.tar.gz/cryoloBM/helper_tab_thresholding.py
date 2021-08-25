from cryoloBM import constants, helper_GUI, helper_image, helper_tab_tracing
from cryoloBM import boxmanager_controller # for type hinting purpose

def update_after_setting(controller:boxmanager_controller,update_all:bool)->None:
    """
    Manage the operation trigged by changing a threshold param:
    -) delete old sketches on the current image
    -) draw new sketches on the current image
    -) update the counters
    :param controller: Boxmanager_controller obj
    :param update_all: True if we have to update the counters for all the tomos (only TOMO FOLDER cas)
    """

    # i do not need to call h_keypress() but only reset its related flag
    if controller.model.toggle:
        controller.model.toggle = False

    # udpate the current image visualization
    if controller.model.rectangles:
        #remove the old patches, they are already saved in controller.model.rectangles
        helper_image.delete_all_patches(controller=controller)

        # restore the canvas
        controller.view.fig.canvas.restore_region(controller.view.background_current)

        # redraw the sketches. this function will filter by threshold values
        helper_image.draw_all_patches(controller=controller)
        controller.view.fig.canvas.blit(controller.view.ax.bbox)

    # update the counters
    controller.view.update_tree_boxsizes(update_current=False, all_tomos=update_all)
    if update_all:
        controller.view.update_all_global_counters()
    else:
        controller.view.update_global_counter()

def conf_thresh_changed(controller:boxmanager_controller)->None:
    # self.trace_all = False
    update_all = None
    try:
        controller.model.current_conf_thresh = float(controller.view.conf_thresh_slide.value()) / 100
        if not controller.view.is_updating_params and controller.model.type_case == constants.Type_case.TOMO_FOLDER.value and not controller.view.is_slider_pressed:
            update_all =controller.view.apply_to_all_the_tomo_question( name_param = "confidence threshold") == controller.view.clicked_yes()
            if update_all:
                #self.trace_all = True
                for p in controller.model.params.values():
                    p.conf_thresh = controller.model.current_conf_thresh

            else:
                controller.model.params[controller.get_current_filename(with_extension=False)].conf_thresh = controller.model.current_conf_thresh
    except ValueError:
        return

    controller.view.line_setText(line=controller.view.conf_thresh_line, value=str(controller.model.current_conf_thresh))
    update_after_setting(controller=controller,update_all=update_all)
    controller.view.is_updating_params = True

def conf_thresh_label_changed(controller:boxmanager_controller)->None:
    try:
        old_value = controller.model.current_conf_thresh
        new_value = float(controller.view.conf_thresh_line.text())
        if new_value > 1.0 or new_value < 0:
            if not controller.view.is_updating_params:
                controller.view.err_message(msg=f"value has to be between 0 and 1")
                controller.view.line_setText(line=controller.view.conf_thresh_line,value=str(old_value))
            return
    except ValueError:
        return

    controller.model.current_conf_thresh = new_value
    controller.view.conf_thresh_slide.setValue(new_value * 100)
    if controller.view.preview_is_on:
        helper_tab_tracing.display_preview(controller=controller,only_reload=True)

def lower_size_thresh_changed(controller:boxmanager_controller)->None:
    #self.trace_all = False
    update_all = False
    controller.model.lower_size_thresh = int(float(controller.view.lower_size_thresh_slide.value()))
    if not controller.view.is_updating_params and controller.model.type_case == constants.Type_case.TOMO_FOLDER.value and not controller.view.is_slider_pressed:
        update_all =controller.view.apply_to_all_the_tomo_question( name_param = "lower size threshold") == controller.view.clicked_yes()
        # self.trace_all = True
        if update_all:
            for p in controller.model.params.values():
                p.lower_size_thresh = controller.model.lower_size_thresh
        else:
            controller.model.params[controller.get_current_filename(with_extension=False)].lower_size_thresh = controller.model.lower_size_thresh

    controller.view.line_setText(line=controller.view.lower_size_thresh_line, value=str(controller.model.lower_size_thresh))
    update_after_setting(controller=controller, update_all=update_all)
    controller.view.is_updating_params = True


def lower_size_label_changed(controller:boxmanager_controller)->None:
    try:
        new_value = int(float(controller.view.lower_size_thresh_line.text()))
        old_value = controller.model.lower_size_thresh
        upper_value = controller.view.upper_size_thresh_slide.value()
        lower_value = controller.view.lower_size_thresh_slide.value()
        if new_value > upper_value or new_value < lower_value:
            if not controller.view.is_updating_params:
                controller.view.err_message(msg=f"value has to be between { lower_value} and { upper_value}")
            controller.view.line_setText(line=controller.view.lower_size_thresh_line,value=str(old_value))
            return
    except ValueError:
        return

    controller.view.lower_size_thresh_slide.setValue(new_value)
    controller.model.lower_size_thresh = new_value
    if controller.view.preview_is_on:
        helper_tab_tracing.display_preview(controller=controller,only_reload=True)

def upper_size_thresh_changed(controller:boxmanager_controller)->None:
    # self.trace_all = False
    update_all = False
    controller.model.upper_size_thresh = int(float(controller.view.upper_size_thresh_slide.value()))
    if not controller.view.is_updating_params and controller.model.type_case == constants.Type_case.TOMO_FOLDER.value and not controller.view.is_slider_pressed:
        update_all = controller.view.apply_to_all_the_tomo_question(name_param="upper size threshold") == controller.view.clicked_yes()
        # self.trace_all = True
        if update_all:
            for p in controller.model.params.values():
                p.upper_size_thresh = controller.model.upper_size_thresh
        else:
            controller.model.params[controller.get_current_filename(with_extension=False)].upper_size_thresh = controller.model.upper_size_thresh

    controller.view.line_setText(line=controller.view.upper_size_thresh_line, value=str(controller.model.upper_size_thresh))
    update_after_setting(controller=controller, update_all=update_all)
    controller.view.is_updating_params = True

def upper_size_label_changed(controller:boxmanager_controller)->None:
    try:
        new_value = int(float(controller.view.upper_size_thresh_line.text()))
        old_value = controller.model.upper_size_thresh
        upper_value = controller.view.upper_size_thresh_slide.value()
        lower_value = controller.view.lower_size_thresh_slide.value()
        if new_value > upper_value or new_value < lower_value:
            if not controller.view.is_updating_params:
                controller.view.err_message(msg= f"value has to be between {lower_value} and {upper_value}")
            controller.view.line_setText(line=controller.view.upper_size_thresh_line,value=str(old_value))
            return
    except ValueError:
        return

    controller.view.upper_size_thresh_slide.setValue(new_value)
    controller.model.upper_size_thresh = new_value
    if controller.view.preview_is_on:
        helper_tab_tracing.display_preview(controller=controller,only_reload=True)