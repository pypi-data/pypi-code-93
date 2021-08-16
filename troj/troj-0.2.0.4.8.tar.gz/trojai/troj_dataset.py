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
        transforms=None,
        channel_first=True,
    ):
        '''

        :param dataframe:
        :param root_folder:
        :param transforms:
        :param channel_first:
        '''
        self.dataset_meta = {}
        self.dataframe = dataframe
        self.transforms = transforms
        self.root_folder = root_folder
        self.index_list = self.dataframe.index.tolist()
        self.channel_first = channel_first

    def __len__(self):
        return len(set(self.dataframe["file_name"]))

    def __getitem__(self, index):
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
            img = self.transforms(img)
        if self.channel_first is True:
            img = np.moveaxis(img, -1, 0)

        return img, annotation, index


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
        '''

        :param folder_path:
        :return:
        '''

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
    '''

    :param bbox:
    :return:
    '''
    new_bbox = [bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]]
    return new_bbox


def convert_coco_json_to_dict(filename, stage, convert_bbox=True):
    '''

    :param filename:
    :param stage:
    :param convert_bbox:
    :return:
    '''
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
    def __init__(self, dataframe, root_folder, transforms=None, box_transforms=None):
        '''

        :param dataframe:
        :param root_folder:
        :param transforms:
        :param box_transforms:
        '''
        self.dataframe = dataframe
        self.transforms = transforms
        self.root_folder = root_folder
        self.index_list = self.dataframe.index.tolist()

    def __len__(self):
        return len(set(self.dataframe["file_name"]))

    def __getitem__(self, index):
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
    '''

    :param dataloader:
    :param batch_size:
    :param shuffle:
    :param device:
    :param kwargs:
    :return:
    '''
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



def BuildClassificationBatchIterator(dataloader, batch_size, shuffle=True, **kwargs):
    '''

    :param dataloader:
    :param batch_size:
    :param shuffle:
    :param kwargs:
    :return:
    '''
    def collate_wrapper(batch):
        transposed_data = list(zip(*batch))
        inp = np.ascontiguousarray(np.stack(transposed_data[0], 0).astype(np.float32))
        tgt = np.stack(transposed_data[1], 0).astype(np.int64)
        idx = np.stack(transposed_data[2], 0)
        return (inp, tgt, idx)

    loader = torch.utils.data.DataLoader(
        dataloader,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=collate_wrapper,
        **kwargs
    )
    return loader
