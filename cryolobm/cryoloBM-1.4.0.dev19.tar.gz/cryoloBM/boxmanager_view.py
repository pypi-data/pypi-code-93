from cryoloBM import boxmanager_view_ABC,boxmanager_controller,boxmanager_toolbar, helper, constants
import numpy as np
from os import path

class Boxmanager_view(boxmanager_view_ABC.Boxmanager_view_ABC):

    def __init__(self,font):
        """
        :param font. Qfont type got at the start of the code in the boxmanager.py. It is the only rererence to PyQT
        """
        super(Boxmanager_view, self).__init__(font)
        self.controller = None

    def setup(self,controller:boxmanager_controller):
        """
        :param controller: Boxmanager_controller obj
        """
        self.setup_()
        self.controller = controller

    def reset_config(self) -> None:
        self.controller.reset_config()

    def close_boxmanager(self):
        self.controller.close_boxmanager()

    def picking_filament_changed(self) -> None:
        """
        It is connected to the combobox picking_filament_combox to select if picking particle or filament
        """
        # make it visible or not in function of the current picking type
        is_filament = self.picking_filament_combox.currentText() == constants.Picking_cb.FILAMENT.value

        # set the 'has_filament' var of 'box_dictionary
        if self.controller.model.box_dictionary:
            self.controller.model.box_dictionary.has_filament = is_filament

        self.set_visualization_combobox(is_picking_particles=not is_filament)
        self.controller.model.picking_combobox_value = self.picking_filament_combox.currentText()
        self.controller.model.visualization = self.visualization_combobox.currentText()
        # update the visualization
        current_filename = self.controller.get_current_filename(with_extension=False)
        if self.controller.model.box_dictionary and not self.controller.model.box_dictionary.has_same_visualization(visualization=self.controller.model.visualization,
                                                                    f=current_filename,n=self.controller.model.index_tomo):
            self.controller.model.box_dictionary.update_visualization_dictionary(
                new_visualization=self.controller.model.visualization, f=current_filename, n=self.controller.model.index_tomo)

    def searchRange_label_changed(self)->None:
        self.controller.searchRange_label_changed()

    def searchRange_changed(self)->None:
        self.controller.searchRange_changed()

    def show_size_distribution(self)->None:
        """
        Function to show the size distribution
        """
        self.controller.show_size_distribution()

    def show_confidence_histogram(self)->None:
        """
        Function to to show the confidence histogram
        """
        self.controller.show_confidence_histogram()

    def open_SPA_folder(self, via_cli:bool = False)->None:
        """
        Function to read micrograph's images from a folder
        :param via_cli: True if we run from command line
        """
        self.controller.open_SPA_folder(via_cli=via_cli)

    def open_SPA_image(self, via_cli:bool = False)->None:
        """
        Function to read a single micrograph's image
        :param via_cli: True if we run from command line
        """
        self.controller.open_SPA_image(via_cli=via_cli)

    def open_tomo_folder(self, via_cli:bool = False)->None:
        """
        Function to read tomo's images from a folder
        :param via_cli: True if we run from command line
        """
        self.controller.open_tomo_folder(via_cli=via_cli)

    def open_tomo_image(self, via_cli:bool = False)->None:
        """
        Function to read a single tomo's image
        :param via_cli: True if we run from command line
        """
        self.controller.open_tomo_image(via_cli=via_cli)

    def import_box_files(self)->None:
        """
        Function to import box files from file
        """
        self.controller.import_box_files()

    def save_on_files(self)->None:
        """
        Function to to save the results on file. It write all the possible formats.
        It was write_all_type in the old version
        """
        self.controller.save_on_files()

    def apply_filter(self)->None:
        """
        It applies the lowpass filter present in filtering tab.
        """
        self.controller.apply_filter()

    def box_size_changed(self)->None:
        """
        It changes the value of the "box size" filling the 'box size' line in the visualization tab.
        It is triggered pressing enter (when the cursor is into the line) or button 'set'
        """
        self.controller.box_size_changed()

    def box_distance_filament_changed(self):
        """
        It changes the value of the "Box distance" filling the 'Box distance' line in the visualization tab.
        It is triggered pressing enter (when the cursor is into the line) or button 'set'
        """
        self.controller.box_distance_filament_changed()

    def visualization_changed(self)->None:
        """
        It changes the value of the "visualization_combobox" changing the 'visualization' combobox in the visualization tab.
        It is triggered when the combobox is changed
        """
        self.controller.visualization_changed()
        is_visible = self.get_visualization_cb_text() in [constants.Visualization_cb.CIRCLE_SEGMENTED.value,constants.Visualization_cb.RECT_FILAMENT_SEGMENTED.value]
        self.set_visibility_box_distance(is_visible=is_visible)

    def use_estimated_size_changed(self)->None:
        """
        It changes the value of the "box size" filling the 'box size' line in the visualization tab.
        It is usable only after loading data from cbox file. It gets the new "box size" from these files
        Pay attention: each particle will have its own estimated size
        It is triggered pressing enter (when the cursor is into the line) or button 'set'
        """
        self.controller.use_estimated_size_changed()

    def lower_size_thresh_changed(self)->None:
        self.controller.lower_size_thresh_changed()

    def lower_size_label_changed(self)->None:
        self.controller.lower_size_label_changed()

    def upper_size_thresh_changed(self)->None:
        self.controller.upper_size_thresh_changed()

    def upper_size_label_changed(self)->None:
        self.controller.upper_size_label_changed()

    def conf_thresh_changed(self)->None:
        self.controller.conf_thresh_changed()

    def conf_thresh_label_changed(self)->None:
        self.controller.conf_thresh_label_changed()

    def memory_changed(self)->None:
        self.controller.memory_changed()

    def memory_label_changed(self)->None:
        self.controller.memory_label_changed()

    def min_length_changed(self)->None:
        self.controller.min_length_changed()

    def min_length_label_changed(self)->None:
        self.controller.min_length_label_changed()

    def min_edge_weight_changed(self)->None:
        self.controller.min_edge_weight_changed()

    def min_edge_weight_label_changed(self)->None:
        self.controller.min_edge_weight_label_changed()

    def win_size_changed(self)->None:
        self.controller.win_size_changed()

    def win_size_label_changed(self)->None:
        self.controller.win_size_label_changed()

    def preview(self)->None:
        self.controller.preview()

    def trace(self)->None:
        self.controller.trace()


    # wrapper function set_first_image
    def create_plot_toolbar(self):
        return boxmanager_toolbar.Boxmanager_Toolbar( self.controller)

    def onclick(self, event)->None:
        """
        It is called when we click on the image
        :param event: the click event
        """
        self.controller.onclick(event=event)

    def myKeyPressEvent(self, event)->None:
        """
        It is called when we click on the image
        :param event: the click event
        """
        self.controller.myKeyPressEvent(event=event)

    def onrelease(self, event)->None:
        """
        It is called when we click on the image
        :param event: the click event
        """
        self.controller.onrelease(event=event)

    def onmove(self, event)->None:
        """
        It is called when we release the mouse button
        :param event: the click event
        """
        self.controller.onmove(event=event)

    def event_image_changed(self):
        return self.controller.event_image_changed(self.tree.currentItem())

    def update_tree_boxsizes(self, update_current:bool =False, all_tomos:bool =False)->None:
        """
        Update the counter into the filename images tree
        """
        def update(filename:str)->None:
            has_filament = self.controller.model.picking_combobox_value == constants.Picking_cb.FILAMENT.value
            current_conf_thresh, upper_size_thresh, lower_size_thresh, current_num_boxes_thresh = self.controller.model.get_threshold_params(filename)
            res = [helper.check_if_should_be_visible(box=box, current_conf_thresh=current_conf_thresh, upper_size_thresh=upper_size_thresh, lower_size_thresh=lower_size_thresh,
                                                     num_boxes_thresh=current_num_boxes_thresh, is_filament=has_filament) for box in boxes]
            num_box_vis = int(np.sum(res))
            msg = "" if len(res) == 0 else "{0:> 4d}  / {1:> 4d}".format(num_box_vis, len(res))
            item.setText(1, msg)



        if self.controller.model.box_dictionary:
            # in case of imported filament via GUI i have to count the start_end filament
            start_vis = self.controller.model.box_dictionary.fil_start_end_vis
            self.controller.model.box_dictionary.fil_start_end_vis = True

            # the counter has to be set counting from the 2D particle dict
            no_3D = False
            no_tracing = False
            current_filename=self.controller.get_current_filename(with_extension=False)

            if update_current:
                item=self.tree.currentItem()
                boxes = self.controller.model.box_dictionary.get_sketches(f=current_filename,
                                                                     n=self.controller.model.index_tomo, is_3D = no_3D,  is_tracing = no_tracing)
                update(filename=current_filename)
            else:
                root = self.tree.invisibleRootItem().child(0)
                if not root:
                    return

                for i in range(root.childCount()):
                    self.run_in_same_thread()
                    item_root = root.child(i)
                    filename = path.splitext(item_root.text(0))[0]

                    if self.controller.model.type_case == constants.Type_case.TOMO_FOLDER.value:
                        fname = path.splitext(root.child(i).text(0))[0]
                        for chld in range(item_root.childCount()):
                            if fname != current_filename and not all_tomos:
                                # in this case we want to update only the current tomo
                                continue
                            item = item_root.child(chld)
                            boxes = self.controller.model.box_dictionary.get_sketches(f=fname, n=chld, is_3D = no_3D,  is_tracing = no_tracing)
                            update(filename=fname)
                        continue

                    if self.controller.model.type_case == constants.Type_case.SPA.value:
                        boxes = self.controller.model.box_dictionary.get_sketches(f=filename, n=None, is_3D = no_3D,  is_tracing = no_tracing)
                    else:
                        boxes = self.controller.model.box_dictionary.get_sketches(f=current_filename, n=int(filename), is_3D = no_3D,  is_tracing = no_tracing)
                    item = item_root
                    update(filename=current_filename)
            self.controller.model.box_dictionary.fil_start_end_vis = start_vis



    def update_all_global_counters(self)->None:
        """
        It updates the number of total particles in all the tomo, TOMO FOLDER case
        """
        # in case of imported filament via GUI i have to count the start_end filament
        start_vis = self.controller.model.box_dictionary.fil_start_end_vis
        self.controller.model.box_dictionary.fil_start_end_vis = True

        if self.controller.model.type_case == constants.Type_case.TOMO.value:
            self.update_global_counter(childid=None)
        else:
            for child_id in range(self.tree.invisibleRootItem().child(0).childCount()):
                self.update_global_counter(childid=child_id)
        self.controller.model.box_dictionary.fil_start_end_vis = start_vis

    def update_global_counter(self, childid:int = None)->None:
        """
        It updates the number of total particles in the current tomo
        :param childid: identifies the child id in the tomo folder case. It is used after reset->file or 'import' boxes
        """
        def detect_child()->int:
            """ detect the child id, which detect the current file. Only in tomo folder case"""
            for i in range(root.childCount()):
                if path.splitext(root.child(i).text(0))[0] == current_filename:
                    return i

        root = self.tree.invisibleRootItem().child(0)

        # it happen if you run from CLI without param
        if not root:
            return

        current_filename = path.splitext(root.child(childid).text(0))[0] if childid else self.controller.get_current_filename(with_extension=False)
        tot_child,tot_num_box_vis, tot_res, child_id = 0,0, 0, None

        # get the number of slice in the current tomo
        if self.controller.model.type_case == constants.Type_case.TOMO_FOLDER.value:
            child_id = detect_child() if childid is None else childid
            tot_child = root.child(child_id).childCount()
        elif self.controller.model.type_case == constants.Type_case.TOMO.value:
            tot_child = root.childCount()

        # count the number of boxes in the whole current tomo
        has_filament = self.controller.model.picking_combobox_value == constants.Picking_cb.FILAMENT.value
        current_conf_thresh, upper_size_thresh, lower_size_thresh, current_num_boxes_thresh = self.controller.model.get_threshold_params()

        if self.controller.model.type_case != constants.Type_case.SPA.value:
            for j in range(tot_child):
                boxes = self.controller.model.box_dictionary.get_sketches(f=current_filename, n=j, is_3D = False,  is_tracing = False)
                res = [helper.check_if_should_be_visible(box=box, current_conf_thresh=current_conf_thresh, upper_size_thresh=upper_size_thresh, lower_size_thresh=lower_size_thresh,
                                                         num_boxes_thresh=current_num_boxes_thresh, is_filament=has_filament) for box in boxes]
                tot_res += len(res)
                tot_num_box_vis += int(np.sum(res))
        else:
            for f in self.controller.model.box_dictionary.list_purefiles:
                boxes = self.controller.model.box_dictionary.get_sketches(f=f, n=None, is_3D=False,is_tracing=False)
                res = [helper.check_if_should_be_visible(box=box, current_conf_thresh=current_conf_thresh, upper_size_thresh=upper_size_thresh, lower_size_thresh=lower_size_thresh,
                                                         num_boxes_thresh=current_num_boxes_thresh, is_filament=has_filament) for box in boxes]
                tot_res += len(res)
                tot_num_box_vis += int(np.sum(res))

        # write the global counter on the tomo name line
        msg = "" if tot_res == 0 else "{0:> 4d}  / {1:> 4d}".format(tot_num_box_vis, tot_res)
        if self.controller.model.type_case == constants.Type_case.TOMO_FOLDER.value:
            root.child(child_id).setText(1, msg)
        else:
            root.setText(1, msg)

    def thresholding_tab_blurring(self, is_enable: bool, kind_of_cbox: bool,has_filament: bool, type_case: int) -> None:
        """
        After loading from file we have to unblur some options in thresholding tabs
        :param is_enable: If True enable SOME options. If False disable ALL the options
        :param kind_of_cbox: True if model.is_cbox or model.is_cbox_untracved is True
        :param has_filament: If True we work with filament
        :param type_case: constants.Type_case. value
        """
        self.thresholding_tab_blurring_(is_enable=is_enable, kind_of_cbox=kind_of_cbox, has_filament=has_filament, type_case=type_case)

        if not is_enable:
            return

        # In case of cbox files (not filament case), set the minimum and maximum
        if not has_filament and kind_of_cbox:
            self.controller.view.is_updating_params = True

            if type_case == constants.Type_case.SPA.value:
                max_size, min_size = self.controller.model.box_dictionary.get_upper_lower_thres()
            else:
                temp = self.controller.model.box_dictionary.get_upper_lower_thres()
                if type_case == constants.Type_case.TOMO_FOLDER.value:
                    for filename, values in temp.items():
                        self.controller.model.params[filename].upper_size_thresh = values["upper"]
                        self.controller.model.params[filename].lower_size_thresh = values["lower"]
                    pass
                current_fname = self.controller.get_current_filename(with_extension=False)
                max_size, min_size = temp[current_fname]["upper"], temp[current_fname]["lower"]

            self.update_low_up_thresh(max_size=max_size, min_size=min_size)

    def ondraw(self, event)->None:
        """
        It is called when we use the toolbar
        :param event: the click event
        """
        self.controller.ondraw(event=event)