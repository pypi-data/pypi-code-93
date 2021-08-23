import pandas as pd
import json
import numpy as np
import os
import cv2
import torch
import torch.utils.data
from torchvision import transforms
from PIL import Image


class TrojClassificationDataLoader:
    def __init__(
        self,
        dataframe,
        root_folder,
        transforms=[None],
        channel_first=True,
        return_idx=True,
    ):
        """
        :param dataframe: A troj dataframe.
        :param root_folder: The root folder containing the images.
        :param transforms: A (list of) function(s) to be applied to the images during loading.
        :param channel_first: Whether or not to put the channels first. Set to false if this is handled by transforms.
        """
        if type(transforms) is not list:
            transforms = [transforms]

        self.dataset_meta = {
            "root_folder": root_folder,
            "transforms": list(map(self._get_transforms, transforms)),
        }
        self.dataframe = dataframe
        self.transforms = transforms
        self.root_folder = root_folder
        self.index_list = self.dataframe.index.tolist()
        self.channel_first = channel_first
        self.return_idx = return_idx

    def _get_transforms(self, n):
        return n.__name__

    def __len__(self):
        return len(set(self.dataframe["file_name"]))

    def __getitem__(self, index):
        """

        :param index: Index to retrieve item from.
        :return: image and corresponding label, along with the dataframe index if self.return_idx = True
        """
        # print(self.dataframe.loc[index]["file_name"].compute())
        index = self.index_list[index]
        example_row = self.dataframe.loc[index]
        file_name = example_row["file_name"]
        annotation = example_row["label"]
        class_folder = example_row["class_name"]
        stage_folder = example_row["stage"]
        relative_path = (
            self.root_folder + "/" + stage_folder + "/" + class_folder + "/" + file_name
        )

        img = cv2.imread(relative_path)
        if self.transforms != None:
            for transform in self.transforms:
                img = transform(img)
        # find way to make work with troj-transforms?
        if self.channel_first is True:
            img = np.moveaxis(img, -1, 0)
        if self.return_idx:
            return img, annotation, index
        else:
            return img, annotation


class TrojClassificationDataset:
    def __init__(self):
        """
        We initialize the dataframe as None so that if the client does not wish to use our methods they can
        create their own dataframe and pass it to this class. We just specify that the dataframe
        must have the expected basic columns for our methods to function properly.
        """
        self.dataframe = None
        # saves the main folder to look in to recreate the relative links to the images for loading
        self.root_folder = None
        # saves whether or not the data is in coco format or imagenet folders
        self.data_structure = None

    def CreateDF(self, folder_path):
        """
        :param folder_path: A folder path which contains subfolders with the structure
        folder_path/stage_folder/class_folder/img.format
        :return: creates dataframe
        """

        try:
            # if no annotations are included, the annotation information is embedded in the folder structure
            # load it in to dataframe
            accumulator = 0
            out_dict = dict()
            class_list = list()
            for root, d_names, f_names in sorted(
                os.walk(os.path.normpath(folder_path))
            ):
                if f_names != []:
                    # replace the double slash with forward slash for consistency
                    # root = os.path.join(root).replace("\\", "/")
                    # split out each part of the root
                    root = os.path.realpath(root)
                    class_name = root.split(os.path.sep)[-1]
                    stage = root.split(os.path.sep)[-2]
                    base = root.split(os.path.sep)[-3]
                    if class_name not in class_list:
                        class_list.append(class_name)
                    for i, f_name in enumerate(f_names):
                        i = i + accumulator
                        out_dict[i] = {
                            "stage": stage,
                            "class_name": class_name,
                            "file_name": f_name,
                            "label": class_list.index(class_name),
                        }
                        # the accumulator tracks the index of the dictionary across folder loops
                    accumulator = i + 1
            df = pd.DataFrame(out_dict).transpose()
            self.data_structure = "imagenet"
        except Exception as ex:
            print(ex)
            print("Creating dataframe from imagefolders failed!")

        self.dataframe = df
        self.root_folder = folder_path

    def SaveDF(self, path, **kwargs):
        """
        :param path: the save path. This can be a globstring.
        :param kwargs: args for to_csv
        :return:
        """
        self.dataframe.to_csv(path, **kwargs)


def convert_coco_to_cartesian(bbox):
    """
    Converts coco style bounding box coordinates to cartesian coordinates.
    :param bbox:
    :return:
    """
    new_bbox = [bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]]
    return new_bbox


def convert_coco_json_to_dict(filename, stage, convert_bbox=True):
    """
    Converts a coco-style JSON to a dicionary.
    :param filename: JSON file
    :param stage: a name for the stage such as train, test, validation, etc.
    :param convert_bbox: Whether or not to convert from coco format to cartestian bounding boxes.
    :return: A dictionary with the image id as the key where the value is a dictionary containing the annotation information.
    """
    s = json.load(open(filename, "r"))
    annots = s["annotations"]
    ims = s["images"]
    data_dict = {}
    for im in ims:
        im_dict = im
        file_name = im_dict["file_name"]
        im_id = im_dict["id"]
        temp_dict = {}
        temp_dict["stage"] = stage
        temp_dict["file_name"] = file_name
        temp_dict["boxes"] = []
        temp_dict["labels"] = []

        data_dict[im_id] = temp_dict

    for annotations in annots:
        im_id = annotations["image_id"]
        cur_subdict = data_dict[im_id]
        coco_box = [annotations["bbox"][i] for i in range(len(annotations["bbox"]))]
        if convert_bbox:
            coco_box = convert_coco_to_cartesian(coco_box)
        cur_subdict["boxes"].append(coco_box)
        cur_subdict["labels"].append(annotations["category_id"])
        data_dict[im_id] = cur_subdict

    return data_dict


class TrojODDataset:
    def __init__(self):
        self.dataframe = None

    def CreateODDF(self, image_folder, annotations_dict, convert_coords=True):
        """
        Creates a dataframe for object detection datasets.

        :param: image_folder: folder containing split subfolders
        :param: annotations_dict: a dictionary where the keys are the names of subfolders, and the values are file locations for the
        annotations. If a folder has no annotations, set value to None in dict.
        :param: convert_coords: whether or not to convert coco-style coordinates to cartesian coordinates
        """
        data_list = []

        for im_dir in os.listdir(image_folder):
            if im_dir not in list(annotations_dict.keys()):
                pass
            else:
                im_dir_path = os.path.join(image_folder, im_dir)
                if annotations_dict[im_dir] == None:
                    pass
                else:
                    temp_data = convert_coco_json_to_dict(
                        annotations_dict[im_dir], im_dir, convert_coords
                    )
                    data_list.append(temp_data)

        dall = {}
        for d in data_list:
            dall.update(d)
        df = pd.DataFrame(list(dall.values()))

        self.dataframe = df


class ODTrojDataLoader:
    def __init__(self, dataframe, root_folder, transforms=None):
        """
        Dataloader for object detection data.

        :param dataframe: Troj object detection dataframe.
        :param root_folder: The root image folder.
        :param transforms: Any transforms to apply to the images (corresponding box transformations not yet implemented).
        """
        self.dataframe = dataframe
        self.transforms = transforms
        self.root_folder = root_folder
        self.index_list = self.dataframe.index.tolist()
        self.dataset_meta = {
            "root_folder": str(root_folder),
        }

    def __len__(self):
        return len(set(self.dataframe["file_name"]))

    def __getitem__(self, index):
        """

        :param index: Item index
        :return: transformed images, bounding boxes, labels, and the dataframe index
        """
        index = self.index_list[index]
        example_row = self.dataframe.loc[index]
        file_name = example_row["file_name"]
        labels = example_row["labels"]
        boxes = example_row["boxes"]
        stage_folder = example_row["stage"]
        relative_path = self.root_folder + "/" + stage_folder + "/" + file_name

        img = Image.open(relative_path)
        boxes = torch.tensor(boxes)
        labels = torch.tensor(labels)
        if self.transforms == None:
            self.transforms = transforms.ToTensor()
            # apply transforms
        return self.transforms(img), boxes, labels, index


def BuildODBatchIterator(dataloader, batch_size, shuffle=True, device="cuda", **kwargs):
    """
    The Troj function for iterating over OD data given a dataloader.

    :param dataloader: Troj OD Dataloader instance
    :param batch_size: the size of batches to be returned
    :param shuffle: Whether or not to shuffle the data or keep it in the original order
    :param device: device to put the data on
    :param kwargs:
    :return: A batch iterator
    """

    def ODcollate_wrapper(batch, device=device):
        transposed_data = list(zip(*batch))
        inp = []
        dict_list = []
        for idx in range(len(transposed_data[1])):
            # inp.append(transposed_data[0][idx])
            inp.append(transposed_data[0][idx].to(device))
            temp_dict = {}
            temp_dict["labels"] = transposed_data[2][idx].to(device)
            temp_dict["boxes"] = transposed_data[1][idx].to(device)
            dict_list.append(temp_dict)

        idx = np.stack(transposed_data[3], 0)
        return (inp, dict_list, idx)

    loader = torch.utils.data.DataLoader(
        dataloader,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=ODcollate_wrapper,
        **kwargs
    )
    return loader


def BuildClassificationBatchIterator(
    dataloader, batch_size, shuffle=True, as_torch_tensor=False, **kwargs
):
    """
    :param dataloader: Troj Classification dataloader.
    :param batch_size: size of batches.
    :param shuffle: Whether or not to shuffle the data.
    :param kwargs:
    :return:
    """

    def collate_wrapper(batch):
        transposed_data = list(zip(*batch))
        inp = np.ascontiguousarray(np.stack(transposed_data[0], 0).astype(np.float32))
        tgt = np.stack(transposed_data[1], 0).astype(np.int64)
        if as_torch_tensor:
            inp = torch.from_numpy(inp)
            tgt = torch.from_numpy(tgt)
        if len(transposed_data) == 3:
            idx = np.stack(transposed_data[2], 0)
            return (inp, tgt, idx)
        else:
            return (inp, tgt)

    loader = torch.utils.data.DataLoader(
        dataloader,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=collate_wrapper,
        **kwargs
    )
    return loader
