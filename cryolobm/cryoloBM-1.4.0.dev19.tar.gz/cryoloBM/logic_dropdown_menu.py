"""
In this file i declare all the logic related to the dropdown menu calls in order to improve the readibility of the
boxmanager_controller.py code letting into it only the calls to the function (of course functions like 'reset_config'
that have only fews line of code are, for now, still into the file)
"""
from cryoloBM import constants, helper, helper_GUI, helper_image
from os import path
from mrcfile import mmap as mrcfile_mmap        #it is not in the setup.py because it is already installed by cryolo
from numpy import min as np_min, max as np_max
import matplotlib.pyplot as plt

from cryoloBM import boxmanager_controller,MySketch # for type hinting purpose
from typing import Union,List,Dict,Tuple

def close_boxmanager(controller:boxmanager_controller)->None:
    """
    It is called via File->close
    Close the boxmanager script.
    :param controller: Boxmanager_controller obj
    """
    if controller.model.unsaved_changes and controller.view.qtmessage(
                msg="All loaded boxes are discarded. Are you sure?", has_cancel=True) == controller.view.clicked_cancel():
            return
    controller.view.close()

def reset_config(controller:boxmanager_controller)->None:
    """
    It is called via File->Reset
    Reset all the variables of the model and restore the GUI starting layout
    :param controller: Boxmanager_controller obj
    """
    # We draw and remove the sketches in real time in 'event_image_changed' using controller.model.rectangles var
    # we have to remove ONLY the sketches in the current image/slice
    if controller.model.box_dictionary:
        # delete sketches from the figure
        helper_image.delete_all_patches(controller=controller)
        # update the plot for avoiding weird behaviour (matplotlib tutorial suggests to delete a plot and plot a new one)
        controller.view.fig.canvas.draw()

    # the model.box_dictionary.particle_dictionary war ll be clean and as consequence when we ll load another image no
    # sketches ll be drawn
    controller.model.reset_config()
    controller.view.reset_config_()     # it is defined in the abstract class , '_' becuase 'reset_config' is triggered by signal and call this function
    controller.view.uncheck_all_slides(type_case=controller.model.type_case)
    type_case = controller.model.type_case if controller.model.type_case else None
    controller.view.thresholding_tab_blurring(is_enable=False, kind_of_cbox=False, has_filament=False,type_case=type_case)
    controller.view.tracing_tab_blurring(is_enable=False,has_filament=controller.model.has_filament)
    controller.view.display_default_params()

    # model.reset_config cleaned the Box_dictionary.box_dictionary. Hence update_tree_boxes finds 0 boxes in every image
    controller.view.update_tree_boxsizes(update_current=False,all_tomos=False)

    tot_child = 1 if controller.model.type_case != constants.Type_case.TOMO_FOLDER.value else len(controller.model.params)
    for child_id in range(tot_child):
        controller.view.update_global_counter(childid=child_id)

def open_tomo_image(controller:boxmanager_controller,via_cli:bool)->bool:
    """
    Reads a single tomo image and fills the model's var.
    :param controller: Boxmanager_controller obj
    :param via_cli: True if we run from command line
    :return False if something went wrong
    """
    # when the script is run via cli this var is already filled
    if not via_cli:
        reset_config(controller=controller)
        selected_image=controller.view.get_selected_file(unsaved_changes=controller.model.unsaved_changes)
        helper.set_current_image_path(controller=controller, current_image_path=selected_image)

        if not controller.view.current_image_path:
            return False

        if not controller.view.current_image_path.endswith(("mrc", "mrcs", "rec")):
            controller.view.err_message(msg=f"ERROR: The image '{controller.view.current_image_path}' has an invalid format. Must be in .mrc or .mrcs format")
            return False

    controller.model.set_tomo_vars()
    controller.model.current_tomoimage_mmap = helper.read_image(file_path=controller.view.current_image_path, use_mmap=True)

    if len(controller.model.current_tomoimage_mmap.shape) != 3:
        controller.view.err_message(msg=f"ERROR: The image '{controller.view.current_image_path}' is not a 3D image")
        return False

    root = controller.view.create_tree_widget_item( title=controller.view.current_image_path)
    controller.view.check_item_checkbox(item=root, check=False)

    controller.view.reset_tree(root=root, title=controller.view.current_image_path)

    if controller.model.current_tomoimage_mmap.shape[0] > 0:
        purefilename = controller.get_current_filename(with_extension=False)
        controller.model.tot_frames.update({purefilename: controller.model.current_tomoimage_mmap.shape[0]})
        controller.model.smallest_image_dim.update({purefilename: min(controller.model.current_tomoimage_mmap.data.shape[1], controller.model.current_tomoimage_mmap.data.shape[2])})
        controller.view.memory_slider.setMaximum(controller.model.tot_frames[purefilename] - 1)
        controller.view.min_length_slider.setMaximum(controller.model.tot_frames[purefilename] - 1)
        controller.view.search_range_slider.setMaximum(controller.model.smallest_image_dim[purefilename] - 1)
        controller.view.fill_root_childs(root=root, tot_slices=controller.model.current_tomoimage_mmap.shape[0], is_folder=False)

    else:
        controller.view.err_message(msg=f"ERROR: The image '{controller.view.current_image_path}' is recognized as a 3D image but has no slice (i.e.: mrc.data.shape[0]<1")
        return False

    root.setExpanded(True)

    # Show first image
    img_data= controller.model.current_tomoimage_mmap[int(root.child(0).text(0)), :, :]
    controller.view.current_tree_item = root.child(0)

    controller.model.set_rectangles ([])

    controller.model.type_case = constants.Type_case.TOMO.value
    controller.model.init_box_dictionary(onlyfiles=[controller.model.current_image_path],
                                         tot_slices=controller.model.current_tomoimage_mmap.shape[0])
    controller.view.set_first_time_img( im=img_data)
    controller.view.setWindowTitle_viewPlot(title=f"{controller.get_current_filename(with_extension=True)} \tslice: 0" )
    controller.view.setCurrentItem_viewTree(is_tomo_folder=False, number_tomo=0, z=0)

    controller.view.enable_button_apply_filter()
    controller.model.unsaved_changes = False
    return True

def open_tomo_folder(controller:boxmanager_controller, via_cli:bool)->bool:
    """
    Reads the image folder and fills the model's var.
    :param controller: Boxmanager_controller obj
    :param via_cli: True if we run from command line
    :return False if something went wrong
    """
    # when the script is run via cli this var is already filled
    if not via_cli:
        reset_config(controller=controller)
        controller.model.image_folder_path=controller.view.get_selected_folder(unsaved_changes=controller.model.unsaved_changes)
        controller.view.image_folder_path = controller.model.image_folder_path

    controller.model.set_tomo_vars()

    root, onlyfiles, all_items = helper.list_files_in_folder(controller=controller, is_list_tomo=True)

    if not onlyfiles:
        controller.view.err_message( msg=f"ERROR: The folder '{controller.model.image_folder_path}' does not have tomogram")
        return False

    if root and all_items :
        root.setExpanded(True)
        for root_child_index,f in enumerate(onlyfiles):
            purefilename = path.splitext(path.basename(f))[0]
            controller.model.fill_params(list_files=[purefilename])
            with mrcfile_mmap(path.join(controller.model.image_folder_path, f), permissive=True, mode="r") as mrc:
                controller.model.tot_frames.update({purefilename: mrc.data.shape[0]})
                controller.model.smallest_image_dim.update({purefilename: min(mrc.data.shape[1], mrc.data.shape[2])})
                controller.view.memory_slider.setMaximum(controller.model.tot_frames[purefilename] - 1)
                controller.view.min_length_slider.setMaximum(controller.model.tot_frames[purefilename] - 1)
                controller.view.search_range_slider.setMaximum(controller.model.smallest_image_dim[purefilename] - 1)
                if mrc.data.shape[0] > 0:
                    if controller.model.current_tomoimage_mmap is None:
                        helper.set_current_image_path(controller=controller, current_image_path=path.join(controller.model.image_folder_path, f))
                        controller.model.current_tomoimage_mmap = helper.read_image(file_path=controller.model.current_image_path, use_mmap=True)
                        controller.model.type_case = constants.Type_case.TOMO_FOLDER.value
                        controller.model.init_box_dictionary(onlyfiles=onlyfiles, tot_slices=None)
                    controller.model.box_dictionary.init_single_tomo(tomo_name=path.splitext(f)[0],
                                                                     tot_slices=mrc.data.shape[0])
                    controller.view.fill_root_childs(root=root, is_folder=True, root_child_index=root_child_index,
                                                tot_slices=mrc.data.shape[0])
                mrc.close()

        if controller.model.current_tomoimage_mmap  is not None:
            controller.view.set_first_time_img(im=controller.model.current_tomoimage_mmap[0, :, :])
            controller.view.setWindowTitle_viewPlot(title=f"{controller.get_current_filename(with_extension=True)} \tslice: 0")
            controller.view.setCurrentItem_viewTree(is_tomo_folder=True, number_tomo=0, z=0)

            controller.view.enable_button_apply_filter()
            controller.model.unsaved_changes = False
            return True

        controller.view.err_message(msg = f"ERROR: Cannot open '{controller.model.current_image_path}' tomogram")
        return False

def open_SPA_image(controller:boxmanager_controller, via_cli:bool)->bool:
    """
    Reads the image folder and fills the model's var.
    :param controller: Boxmanager_controller obj
    :param via_cli: True if we run from command line
    :return False if something went wrong
    """
    # when the script is run via cli this var is already filled
    if not via_cli:
        reset_config(controller=controller)
        selected_image=controller.view.get_selected_file(unsaved_changes=controller.model.unsaved_changes)
        helper.set_current_image_path(controller=controller, current_image_path=selected_image)

        if not controller.view.current_image_path:
            return False
    controller.model.image_folder_path = path.dirname(controller.view.current_image_path)
    controller.view.image_folder_path = controller.model.image_folder_path
    controller.model.has_3d = False


    fname =path.splitext(path.basename(controller.view.current_image_path))
    fname=fname[0]+fname[1]

    title = path.join(str(controller.model.image_folder_path),controller.model.wildcard) if controller.model.wildcard else str(controller.model.image_folder_path)
    root = controller.view.create_tree_widget_item( title=fname)

    controller.view.check_item_checkbox(item=root,check=False)
    controller.view.reset_tree(root, title)
    controller.model.set_rectangles(rectangles=[])

    all_items = [controller.view.create_tree_widget_item( title=fname)]

    for item_index, item in enumerate(all_items):
        controller.view.run_in_same_thread()
        controller.view.check_item_checkbox(item=item, check=False)
        root.addChild(item)

    root.setExpanded(True)
    # Show first image

    controller.view.current_tree_item = root.child(0)
    im = helper.read_image(file_path=controller.model.current_image_path, use_mmap=False)

    if len(im.shape) != 2:
        controller.view.err_message( msg="Please open an image folder with micrographs")
        return False

    controller.model.set_rectangles(rectangles=[])

    controller.model.type_case = constants.Type_case.SPA.value
    controller.model.init_box_dictionary(onlyfiles=[fname], tot_slices=None)
    controller.view.set_first_time_img( im=im)

    controller.view.setCurrentItem_viewTree(is_tomo_folder=False, number_tomo=0, z=0)
    controller.view.setWindowTitle_viewPlot(title=controller.get_current_filename(with_extension=True))
    controller.view.enable_button_apply_filter()
    controller.model.unsaved_changes = False

    return True

def open_SPA_folder(controller:boxmanager_controller, via_cli:bool)->bool:
    """
    Reads the image folder and fills the model's var.
    :param controller: Boxmanager_controller obj
    :param via_cli: True if we run from command line
    :return False if something went wrong
    """
    # when the script is run via cli this var is already filled
    if not via_cli:
        reset_config(controller=controller)
        controller.model.image_folder_path=controller.view.get_selected_folder(unsaved_changes=controller.model.unsaved_changes)
        controller.view.image_folder_path = controller.model.image_folder_path

    controller.model.has_3d = False

    # do not clean the self.box_dictionary because for the SPA case it ll be overwrite in the 'init_box_dictionary'

    root, onlyfiles, all_items = helper.list_files_in_folder(controller=controller, is_list_tomo=False)

    if not onlyfiles:
        return False

    if root and all_items :
        root.setExpanded(True)
        # Show first image
        helper.set_current_image_path(controller=controller, current_image_path=path.join(controller.model.image_folder_path, str(root.child(0).text(0))))
        controller.view.current_tree_item = root.child(0)
        im = helper.read_image(file_path=controller.model.current_image_path,use_mmap=False)

        if len(im.shape) != 2:
            controller.view.err_message( msg="Please open an image folder with micrographs")
            return False

        controller.model.set_rectangles( rectangles= [])

        controller.model.type_case = constants.Type_case.SPA.value
        controller.model.init_box_dictionary(onlyfiles=onlyfiles, tot_slices=None)
        controller.view.set_first_time_img( im=im)

        controller.view.setCurrentItem_viewTree(is_tomo_folder=False, number_tomo=0, z=0)
        controller.view.setWindowTitle_viewPlot(title=controller.get_current_filename(with_extension=True))
        controller.view.enable_button_apply_filter()
        controller.model.unsaved_changes = False
        return True

    return False

def _get_list_boxes_for_histograms(controller:boxmanager_controller)->Tuple[List[MySketch.MySketch],str]:
    """
    Return the correct list of list of boxes for 'show_confidence_histogram' and 'show_size_distribution'
    """
    current_filename = controller.get_current_filename(with_extension=False)
    add_in_title = " of " + current_filename if controller.model.type_case == constants.Type_case.TOMO_FOLDER.value else ""
    if controller.model.type_case == constants.Type_case.SPA.value:
        list_boxes = [*controller.model.box_dictionary.particle_dictionary.values()]
    else:
        bdict=controller.model.box_dictionary.particle_dictionary[current_filename]
        list_boxes = [*bdict.values()]

    return list_boxes,add_in_title

def show_size_distribution(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    list_boxes, add_in_title = _get_list_boxes_for_histograms(controller=controller)
    estimated_size = [box.get_est_size() for boxes in list_boxes for box in boxes]

    fig = plt.figure()

    width = max(10, int((np_max(estimated_size) - np_min(estimated_size)) / 10))
    plt.hist(estimated_size, bins=width)
    plt.title("Particle diameter distribution" + add_in_title)
    plt.xlabel("Partilce diameter [px] (Bin size: " + str(width) + "px )")
    plt.ylabel("Count")

    controller.view.plot_distribution( fig=fig)

def show_confidence_histogram(controller:boxmanager_controller)->None:
    """
    :param controller: Boxmanager_controller obj
    """
    list_boxes, add_in_title = _get_list_boxes_for_histograms(controller)
    confidence= [box.get_confidence() for boxes in list_boxes for box in boxes]

    fig = plt.figure()

    width = max(10, int((np_max(confidence) - np_min(confidence)) / 0.05))
    plt.hist(confidence, bins=width)
    plt.title("Confidence distribution" + add_in_title)
    bin_size_str = "{0:.2f}".format(((np_max(confidence) - np_min(confidence)) / width))
    plt.xlabel("Confidence (Bin size: " + bin_size_str + ")")
    plt.ylabel("Count")

    controller.view.plot_distribution( fig=fig)
