from sys import exit as sys_exit
from os import path
from cryoloBM import logic_dropdown_menu, helper_image, import_data, helper_tab_thresholding, helper_tab_tracing,writer,constants,helper_GUI,helper
from cryoloBM import boxmanager_model, boxmanager_view   # for type hinting purpose

class Boxmanager_controller:
    def __init__(self, model:boxmanager_model, view:boxmanager_view, app:helper_GUI.QtG)->None:
        self.model = model
        self.view = view
        self.app = app


    def get_current_filename(self, with_extension:bool = False)->None:
        """
        Return only the filename of the current_image_path. With or without extension.
        Typically with extension for setting the window's title
        """
        if not self.model.current_image_path:
            return None
        f = path.splitext(path.basename(self.model.current_image_path))
        return f[0]+f[1]  if with_extension else f[0]


    def run(self)->None:
        self.view.setup(self)

        # manage the run via command line
        if self.model.image_folder_path is not None:
            self.view.image_folder_path = self.model.image_folder_path
            if self.model.is_tomo:
                if path.isdir(self.model.image_folder_path):
                    self.open_tomo_folder(via_cli= True)
                else:
                    helper.set_current_image_path(controller=self,current_image_path= self.model.image_folder_path)
                    self.open_tomo_image(via_cli=True)
            else:
                if path.isdir(self.model.image_folder_path):
                    self.open_SPA_folder(via_cli= True)
                else:
                    helper.set_current_image_path(controller=self, current_image_path=self.model.image_folder_path)
                    self.open_SPA_image(via_cli=True)
            if self.model.box_dir:
                if self.model.type_case == constants.Type_case.SPA.value:
                    import_data.import_SPA(controller=self, box_dir=self.model.box_dir, keep=False)
                elif self.model.type_case == constants.Type_case.TOMO_FOLDER.value:
                    import_data.import_tomo_folder(controller=self, box_dir=self.model.box_dir, keep=False)
                else:
                    import_data.import_single_tomo(controller=self, path_3d_file=path.splitext(self.model.box_dir)[0],index_file=None,keep=False)



                # update counters
                self.view.update_tree_boxsizes(update_current=False, all_tomos=True)
                self.view.update_all_global_counters()

                #set cbox default option
                self.view.is_updating_params = True
                kind_of_cbox = self.model.is_cbox or self.model.is_cbox_untraced
                if kind_of_cbox:
                    self.view.set_cbox_visualization(has_filament=self.model.has_filament)
                self.view.thresholding_tab_blurring(is_enable=kind_of_cbox,
                                                     kind_of_cbox=kind_of_cbox, has_filament=self.model.has_filament,
                                                     type_case=self.model.type_case)
                self.view.tracing_tab_blurring(is_enable=self.model.is_cbox_untraced,
                                                     has_filament=self.model.has_filament)
                self.view.blur_picking_combobox(has_filament=self.model.has_filament, is_importing=True)


                if self.model.box_dictionary.has_filament:
                    self.model.box_dictionary.fil_start_end_vis = False
                    self.view.set_cbox_visualization(has_filament=self.model.has_filament)

                # in case of cbox filament some options are not available
                if self.model.has_filament:
                    self.view.blur_estimated_size()
                    if not self.model.is_cbox_untraced:
                        box_dist = self.model.box_dictionary.set_box_distance_dict_after_import()
                        self.model.box_distance_filament = box_dist
                        self.view.line_setText(line=self.view.box_distance_filament_line, value=str(box_dist))

            self.view.is_updating_params = False

        sys_exit(self.app.exec_())

    def close_boxmanager(self)->None:
        """
        It is called via File->close
        Close the boxmanager script.
        """
        logic_dropdown_menu.close_boxmanager(self)

    def reset_config(self)->None:
        """
        It is called via File->Reset
        Reset all the variables of the model and restore the GUI starting layout
        """
        logic_dropdown_menu.reset_config(self)

    def import_box_files(self)->None:
        """
        Function to import box files from file
        """
        import_data.import_data(self)

    def save_on_files(self)->None:
        """
        Function to to save the results on file. It write all the possible formats.
        It was write_all_type in the old version
        """
        writer.save_on_files(self)

    def open_SPA_folder(self, via_cli:bool = False)->None:
        """
        Function to read micrograph's images from a folder
        :param via_cli: True if we run from command line
        """
        logic_dropdown_menu.open_SPA_folder(self, via_cli = via_cli)

    def open_SPA_image(self, via_cli:bool = False)->None:
        """
        Function to read a single micrograph's image
        :param via_cli: True if we run from command line
        """
        logic_dropdown_menu.open_SPA_image(self, via_cli = via_cli)

    def open_tomo_folder(self, via_cli:bool = False)->None:
        """
        Function to read tomo's images from a folder
        :param via_cli: True if we run from command line
        """
        logic_dropdown_menu.open_tomo_folder(self, via_cli = via_cli)

    def open_tomo_image(self, via_cli:bool = False)->None:
        """
        Function to read a single tomo's image
        :param via_cli: True if we run from command line
        """
        logic_dropdown_menu.open_tomo_image(self, via_cli = via_cli)

    def show_size_distribution(self)->None:
        """
        Function to show the size distribution
        """
        logic_dropdown_menu.show_size_distribution(self)

    def show_confidence_histogram(self)->None:
        """
        Function to to show the confidence histogram
        """
        logic_dropdown_menu.show_confidence_histogram(self)

    def event_image_changed(self, root_tree_item:helper_GUI.QtG)->None:
        """
        Manage the 'image changes' event
        :param root_tree_item: It is filled in automatic via PyQT
        """
        helper_image.event_image_changed(self, root_tree_item=root_tree_item)

    def onclick(self, event:helper_GUI.plt_qtbackend)->None:
        """
        It is called when we click on the image
        :param event: the click event
        """
        helper_image.onclick(self,event=event)

    def onmove(self, event:helper_GUI.plt_qtbackend)->None:
        """
        It is called when we click on the image
        :param event: the click event
        """
        helper_image.onmove(self, event=event)

    def ondraw(self, event:helper_GUI.plt_qtbackend)->None:
        """
        It is called when we use the toolbar
        :param event: the click event
        """
        helper_image.ondraw(self,event=event)

    def onrelease(self, event:helper_GUI.plt_qtbackend)->None:
        """
        It is called when we release the mouse button
        :param event: the click event
        """
        helper_image.onrelease(self, event=event)

    def myKeyPressEvent(self, event:helper_GUI.plt_qtbackend)->None:
        """
        It is called when we press the keyboard
        :param event: the press keyboard event
        """
        helper_image.myKeyPressEvent(self, event=event)

    def box_size_changed(self)->None:
        """
        It changes the value of the "box size" filling the 'box size' line in the visualization tab.
        It is triggered pressing enter (when the cursor is into the line) or button 'set'
        """
        helper_image.box_size_changed(self)

    def box_distance_filament_changed(self):
        """
        It changes the value of the "Box distance" filling the 'Box distance' line in the visualization tab.
        It is triggered pressing enter (when the cursor is into the line) or button 'set'
        """
        helper_image.box_distance_filament_changed(self)

    def use_estimated_size_changed(self)->None:
        """
        It changes the value of the "box size" filling the 'box size' line in the visualization tab.
        It is usable only after loading data from cbox file. It gets the new "box size" from these files
        Pay attention: each particle will have its own estimated size
        It is triggered pressing enter (when the cursor is into the line) or button 'set'
        """
        # otherwise it is triggered when resetting
        if not self.view.is_updating_params:
            helper_image.use_estimated_size_changed(self)


    def visualization_changed(self)->None:
        """
        It changes the value of the "visualization_combobox" changing the 'visualization' combobox in the visualization tab.
        It is triggered when the combobox is changed
        """
        if not self.view.is_updating_cb:
            helper_image.visualization_changed(self)

    # FILTERING TAB OPTION
    def apply_filter(self)->None:
        """
        It applies the lowpass filter present in filtering tab.
        """
        helper_image.apply_filter(self)

    # THRESHOLDING TAB OPTION
    def conf_thresh_changed(self)->None:
        helper_tab_thresholding.conf_thresh_changed(self)

    def conf_thresh_label_changed(self)->None:
        helper_tab_thresholding.conf_thresh_label_changed(self)

    def lower_size_thresh_changed(self)->None:
        helper_tab_thresholding.lower_size_thresh_changed(self)

    def lower_size_label_changed(self)->None:
        helper_tab_thresholding.lower_size_label_changed(self)

    def upper_size_thresh_changed(self)->None:
        helper_tab_thresholding.upper_size_thresh_changed(self)

    def upper_size_label_changed(self)->None:
        helper_tab_thresholding.upper_size_label_changed(self)

    # TRACING OPTION
    def searchRange_changed(self)->None:
        helper_tab_tracing.searchRange_changed(self)

    def searchRange_label_changed(self)->None:
        helper_tab_tracing.searchRange_label_changed(self)

    def memory_changed(self)->None:
        helper_tab_tracing.memory_changed(self)

    def memory_label_changed(self)->None:
        helper_tab_tracing.memory_label_changed(self)

    def min_length_changed(self)->None:
        helper_tab_tracing.min_length_changed(self)

    def min_length_label_changed(self)->None:
        helper_tab_tracing.min_length_label_changed(self)

    def min_edge_weight_changed(self)->None:
        helper_tab_tracing.min_edge_weight_changed(self)

    def min_edge_weight_label_changed(self)->None:
        helper_tab_tracing.min_edge_weight_label_changed(self)

    def win_size_changed(self)->None:
        helper_tab_tracing.win_size_changed(self)

    def win_size_label_changed(self)->None:
        helper_tab_tracing.win_size_label_changed(self)

    def preview(self)->None:
        helper_tab_tracing.preview(self)

    def trace(self)->None:
        helper_tab_tracing.trace(self)