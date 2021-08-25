import argparse
import numpy as np
from math import isnan
from os import listdir,path
from mrcfile import mmap as mrcfile_mmap        #it is not in the setup.py because it is already installed by cryolo

from cryoloBM import MySketch, constants, helper_GUI
from cryolo import  utils,imagereader

from cryoloBM import boxmanager_controller # for type hinting purpose
from typing import Union,List,Dict,Tuple

def create_parser():
    """
    Create the parser
    """
    parser = argparse.ArgumentParser(
        description="Train and validate crYOLO on any dataset",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-i", "--image_dir", help="Path to image directory.")
    parser.add_argument("-b", "--box_dir", help="Path to box directory.")
    parser.add_argument("--wildcard",
                           help="Wildcard for selecting spcific images (e.g *_new_*.mrc)")
    parser.add_argument("-t", "--is_tomo", action="store_true",
                           help="Flag for specifying that the directory or the path  contains tomogram(s).")
    return parser

def set_current_image_path(controller:boxmanager_controller, current_image_path:str)->None:
    """
    Set the current image path for the model and view
    :param controller: Boxmanager_model obj
    :param current_image_path: the current image path
    """
    controller.model.current_image_path = current_image_path
    controller.view.current_image_path = current_image_path

def is_cbox_untraced(b:utils.BoundBox)->bool:
    """
    :param b: loaded box of a cbox file
    return False True if the file is cobx_untraced
    """

    # micrograph case has always b.depth == None and crYOLO will never spawn a untraced file for micrograph case
    if b.depth is not None and isnan(b.depth) is False:
        return int(b.depth) == 1
    return False


def get_corresponding_box(x:int, y:int, rectangles:List[MySketch.MySketch], current_conf_thresh:int, box_size:int, get_low:bool=False)->Union[MySketch.MySketch,None]:
    a = np.array([x, y])

    for box in rectangles:
        b = np.array(box.get_xy())
        dist = np.linalg.norm(a - b)
        if get_low:
            if dist < box_size / 2 and box.get_confidence() < current_conf_thresh:
                return box
        else:
            if dist < box_size / 2 and box.get_confidence() > current_conf_thresh:
                return box
    return None


def read_image(file_path:str, use_mmap:bool=False)->np.ndarray:
    im_type = constants.Filetype_name[path.splitext(file_path)[1].replace(".","").upper()].value

    img = imagereader.image_read(file_path, use_mmap=use_mmap)
    img = normalize_and_flip(img, im_type)
    return img


def normalize_and_flip(img:np.ndarray, file_type:int)->np.ndarray:
    if file_type == 0:
        # JPG
        img = np.flip(img, 0)
    if file_type == 1 or file_type == 2:
        # tif /mrc
        if not np.issubdtype(img.dtype, np.float32):
            img = img.astype(np.float32)
        if len(img.shape) == 3:
            img = np.flip(img, 1)
        else:
            img = np.flip(img, 0)
        mean = np.mean(img)
        sd = np.std(img)
        img = (img - mean) / sd
        img[img > 3] = 3
        img[img < -3] = -3
    return img

def convert_list_bbox_to_sketch(boxes_list:List[utils.BoundBox], out_dict:bool=True, col:str ='r',fil_id=None)->Union[Dict[int,MySketch.MySketch],List[MySketch.MySketch]]:
    """
    Convert the list of Bbox (see 'cryolo.grouping3d.do_tracing' for the syntax), in a dict of sketches
    :param boxes_list: list of BoundingBox instances
    :param out_dict: If True convert in dict otherwise in list
    :param col: color of the edge
    :param fil_id: id filament, used for saving on file purpose and some conversion visualization
    :return dict of sketches (k = frame number, v = list of sketches)
    """
    out = dict() if out_dict else list()

    num_boxes = 1
    for b in boxes_list:
        if 'num_boxes' in b.meta:
            num_boxes = b.meta["num_boxes"]

        sketch = MySketch.MySketch(xy=(b.x,b.y), width=b.w, height=b.h,
                                   is_tomo=True, angle=0.0, est_size=b.w,
                                   confidence=b.c, only_3D_visualization=False,
                                   num_boxes=num_boxes, meta=None, z=None, id=fil_id,
                                   linewidth=1, edgecolor=col, facecolor="none")
        if out_dict is False:
            out.append(sketch)
        elif b.z in out:
            out[int(b.z)].append(sketch)
        else:
            out[int(b.z)] = [sketch]
    return out


class Params:
    """
    Used only in tomo folder case
    We storage the 'thresholding' and 'tracing' params in order to keep the state for each tomo
    """
    def __init__(self, tomo_name:str, filter_freq:float, box_size:int, upper_size_thresh:float, lower_size_thresh:float, conf_thresh:float, num_boxes_thresh:int,
                 min_edge_weight:int, search_range:int, memory:int, min_length:int, win_size:int)->None:
        self.tomo_name = tomo_name
        self.filter_freq = filter_freq
        self.box_size = box_size
        self.upper_size_thresh = upper_size_thresh
        self.lower_size_thresh = lower_size_thresh
        self.conf_thresh = conf_thresh
        self.num_boxes_thresh = num_boxes_thresh
        self.min_edge_weight = min_edge_weight
        self.search_range = search_range
        self.memory=  memory
        self.min_length = min_length
        self.win_size =win_size

    def reset_to_default_values(self)->None:
        """
        Reset to default value. Win_size default value is the box_size
        """
        self.filter_freq = constants.Default_settings_value.DEFAULT_FILTER_FREQ.value
        self.upper_size_thresh = constants.Default_settings_value.DEFAULT_UPPER_SIZE_THRESH.value
        self.lower_size_thresh = constants.Default_settings_value.DEFAULT_LOWER_SIZE_THRESH.value
        self.conf_thresh = constants.Default_settings_value.DEFAULT_CURRENT_CONF_THRESH.value
        self.num_boxes_thresh = constants.Default_settings_value.DEFAULT_CURRENT_NUM_BOXES_THRESH.value
        self.min_edge_weight = constants.Default_settings_value.DEFAULT_MIN_EDGE_WEIGHT.value
        self.search_range = constants.Default_settings_value.DEFAULT_SEARCH_RANGE.value
        self.memory = constants.Default_settings_value.DEFAULT_MEMORY.value
        self.min_length = constants.Default_settings_value.DEFAULT_MIN_LENGTH.value
        self.win_size = constants.Default_settings_value.DEFAULT_BOX_SIZE.value

    def has_same_tracing_params(self,param, has_filament:bool = False)->bool:
        """
        :param param: a Params obj
        :param has_filament: True if we analyze filament
        Return True if param has the same tracing parameters
        """
        min_cond = self.min_length == param.min_length and self.memory == param.memory and self.search_range  == param.search_range
        if has_filament:
            return min_cond and self.min_edge_weight == param.min_edge_weight and self.win_size == param.win_size
        return self.min_length == param.min_length and self.memory == param.memory and self.search_range  == param.search_range


def get_only_files(dir_path:str,wildcard:str,is_list_tomo:bool)->List[str]:
    """
    generate list of files in 'dir_path' path
    :param dir_path: path to the folder
    :param wildcard: using wildcard
    :param is_list_tomo: True if folder of 3D tomo
    :return: list of valid files in 'dir_path'
    """
    onlyfiles = [
        f
        for f in sorted(listdir(dir_path))
        if path.isfile(path.join(dir_path, f))
    ]

    if wildcard:
        import fnmatch
        onlyfiles = [
            f
            for f in sorted(listdir(dir_path))
            if fnmatch.fnmatch(f, wildcard)
        ]

    if is_list_tomo is False:
        onlyfiles = [
            i
            for i in onlyfiles
            if not i.startswith(".")
               and i.endswith((".jpg", ".jpeg", ".png", ".mrc", ".mrcs", ".tif", ".tiff", ".rec"))]
    else:
        onlyfiles_all = [i for i in onlyfiles if not i.startswith(".") and i.endswith((".mrc", ".mrcs",".rec"))]
        onlyfiles.clear()
        for f in onlyfiles_all:
            with mrcfile_mmap(path.join(dir_path, f), permissive=True, mode="r") as mrc:
                if len(mrc.data.shape) == 3:
                    onlyfiles.append(f)
                mrc.close()

    return onlyfiles

def list_files_in_folder(controller:boxmanager_controller,is_list_tomo:bool=False)->Union[Tuple[helper_GUI.QtG.QTreeWidgetItem, List[str], List[helper_GUI.QtG.QTreeWidgetItem]],Tuple[bool,bool,bool]]:
    """
    :param controller: Boxmanager_controller obj
    :param is_list_tomo: True if folder of 3D tomo
    :return root: the QTreeWidgetItem
    :return onlyfiles: list of valid files
    :return all_items: items of the root (one for each valid file)
    """
    if controller.model.image_folder_path != "" and controller.model.image_folder_path is not None:
        title = path.join(str(controller.model.image_folder_path), controller.model.wildcard) if controller.model.wildcard else str(controller.model.image_folder_path)
        root = controller.view.create_tree_widget_item( title=title)
        controller.view.check_item_checkbox(item=root, check=False)

        controller.view.reset_tree(root, title)
        controller.model.set_rectangles(rectangles=[])

        onlyfiles = get_only_files(controller.model.image_folder_path,controller.model.wildcard,is_list_tomo)
        all_items = [controller.view.create_tree_widget_item( title=file) for file in onlyfiles]

        if len(all_items) > 0:
            pd = controller.view.create_progress_dialog(title="Load images")
            pd.show()
            for item_index, item in enumerate(all_items):
                #controller.view.run_in_same_thread()       # sometimes it crashes
                pd.setValue(int((item_index+1)*100/len(all_items)))
                controller.view.check_item_checkbox(item=item, check=False)
                root.addChild(item)
            pd.close()
        return root,onlyfiles,all_items
    return False,False,False


def get_all_loaded_filesnames(root:helper_GUI.QtG.QTreeWidgetItem)->List[str]:
    """
    get the list of the loaded file
    :param root: QtG.QTreeWidget obj
    :return: list of filenames
    """
    return [path.splitext(root.child(i).text(0))[0] for i in range(root.childCount())]

def check_if_should_be_visible( box:MySketch.MySketch, current_conf_thresh:float, upper_size_thresh:float, lower_size_thresh:float, num_boxes_thresh:int = 0, is_filament:bool = True)->bool:
    # Cryolo returns estimated value = NaN for the filament mode. hence in these case we filter only in according with its num_boxes and confidence thresholding
    est_size = upper_size_thresh if is_filament else box.get_est_size()
    if isnan(est_size) :
        return True
    cond = [box.get_confidence() > current_conf_thresh or isnan(box.get_confidence()),
            upper_size_thresh >= est_size >= lower_size_thresh ,
            box.num_boxes > num_boxes_thresh]
    return all(cond)

def create_sketch(sketch:MySketch.MySketch, delta:int, size:int, is_start_end_filament:bool)->MySketch.MySketch:
    """
    Create a new 'smaller' sketch of the given 'sketch' for creating the 3D visualization
    """
    est_size = sketch.get_est_size(False)
    if not est_size:
        est_size = sketch.get_width()
    xy = sketch.get_xy(circle = False)
    width = sketch.get_width() if is_start_end_filament else size
    return MySketch.MySketch(xy=(xy[0] + delta, xy[1] + delta), width=width, height=size, is_tomo=sketch.get_is_tomo(),
                             angle=sketch.get_angle(), est_size=est_size, confidence=sketch.get_confidence(),
                             only_3D_visualization=True, num_boxes=sketch.num_boxes, meta=None, z=None, id=sketch.id,
                             linewidth=1, edgecolor=sketch.getSketch().get_edgecolor(), facecolor="none")

def load_tomo_params(controller:boxmanager_controller,pure_filename:str)->None:
    """
    reset the param f the given tomo, it is basically used in '_event_image_changed'
    :param controller
    :param pure_filename: name of the tomo
    """
    #self.is_loading_max_min_sizes = True
    controller.view.is_updating_params = True
    controller.model.upper_size_thresh = controller.model.params[pure_filename].upper_size_thresh
    controller.view.line_setText(line=controller.view.upper_size_thresh_line, value=str(controller.model.upper_size_thresh))
    controller.model.lower_size_thresh = controller.model.params[pure_filename].lower_size_thresh
    controller.view.line_setText(line=controller.view.lower_size_thresh_line,value=str(controller.model.lower_size_thresh))
    controller.model.current_conf_thresh = controller.model.params[pure_filename].conf_thresh
    controller.view.line_setText(line=controller.view.conf_thresh_line,value=str(controller.model.current_conf_thresh))
    controller.model.current_num_boxes_thresh =controller.model.params[pure_filename].num_boxes_thresh
    controller.view.line_setText(line=controller.view.num_boxes_thresh_line,value=str(controller.model.current_num_boxes_thresh))
    if controller.model.is_cbox_untraced:
        controller.model.memory = controller.model.params[pure_filename].memory
        controller.view.line_setText(line=controller.view.memory_line,value=str(controller.model.memory))
        controller.model.search_range = controller.model.params[pure_filename].search_range
        controller.view.line_setText(line=controller.view.search_range_line,value=str(controller.model.search_range))
        controller.model.min_length = controller.model.params[pure_filename].min_length
        controller.view.line_setText(line=controller.view.min_length_line, value=str(controller.model.min_length))
        if controller.model.has_filament:
            controller.model.win_size = controller.model.params[pure_filename].win_size
            controller.view.line_setText(line=controller.view.win_size_line,value=str(controller.model.win_size))
            controller.model.min_edge_weight = controller.model.params[pure_filename].min_edge_weight
            controller.view.line_setText(line=controller.view.min_edge_weight_line,value=str(controller.model.min_edge_weight))
    controller.view.is_updating_params = False