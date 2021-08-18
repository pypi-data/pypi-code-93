import requests
import json
import picsellia.pxl_exceptions as exceptions
import os
from uuid import uuid4 
from multiprocessing import Process, Manager
import tqdm
import datetime
from picsellia.pxl_multithreading import chunks
import xml.etree.ElementTree as ET
import numpy as np
import collections
class COCOParser:
    def __init__(self, path: str=None, ):
        self.annpath = path
        if not os.path.isfile(self.annpath):
            raise exceptions.ResourceNotFoundError("Please provide a valid path.")
        with open(self.annpath, 'rb') as f:
            self.data = json.load(f)

    def _find_matching_annotations(self, imgid):
        return [ann for ann in self.data["annotations"] if ann["image_id"] == imgid]

    def _find_category_name(self, catid):
        for cate in self.data["categories"]:
            if cate['id'] == catid:
                return cate['name']
        return False

    def find_dataset_type(self,):
        if self.data['annotations'][0]['bbox'] != [] and self.data['annotations'][0]['segmentation'] == []:
            self.dataset_type = 'detection'
        elif self.data['annotations'][0]['bbox'] != [] and self.data['annotations'][0]['segmentation'] != []:
            self.dataset_type = 'segmentation'
        else:
            self.dataset_type = 'classification'
        return self.dataset_type

    @property
    def images(self,):
        return self.data["images"]

    @property
    def categories(self,):
        return self.data["categories"]

    def generate_images_and_annotations(self, tags=None):
        if tags is None:
            tags = [str(datetime.date.today())]
        print("Parsing {} ...".format(self.annpath))
        self.find_dataset_type()
        final = []
        for image in tqdm.tqdm(self.data["images"]):
            img_infos = {
                'internal_key': os.path.join(str(uuid4()), image['file_name']),
                'external_url': image['file_name'],
                'height': image["height"],
                'width': image["width"],
                'tags': tags,
                'source': 'sdk'
            }
            ann_list = self._find_matching_annotations(image["id"])
            if self.dataset_type == "detection":
                ann_infos = self._to_picsellia_format_bbox(image["file_name"], ann_list)
            elif self.dataset_type == "segmentation":
                ann_infos = self._to_picsellia_format_poly(image["file_name"], ann_list)
            final.append((
                img_infos,
                ann_infos
            ))
        return final, tags

    def generate_annotations(self, tags=None, rectangle: bool=False):
        if tags is None:
            tags = [str(datetime.date.today())]
        print("Parsing {} ...".format(self.annpath))
        self.find_dataset_type()
        final = []
        repartition = {}
        nb_annotations = 0
        nb_objects = 0 
        c = collections.Counter()

        for image in tqdm.tqdm(self.data["images"]):
            ann_list = self._find_matching_annotations(image["id"])
            if self.dataset_type == "detection":
                ann_infos = self._to_picsellia_format_bbox(image["file_name"], ann_list)
                final.append(
                    ann_infos
                )
                nb_annotations += 1
                nb_objects += len(ann_infos[1]['data'])
                clss = [e['label'] for e in ann_infos[1]['data']]
                c.update(clss)

            elif self.dataset_type == "segmentation":
                if rectangle and self.data['annotations'][0]['bbox'] != []:
                    ann_infos = self._to_picsellia_format_bbox(image["file_name"], ann_list)
                    final.append(
                        ann_infos
                    )
                else:
                    ann_infos = self._to_picsellia_format_poly(image["file_name"], ann_list)
                    final.append(
                        ann_infos
                    )
                nb_annotations += 1
                nb_objects += len(ann_infos[1]['data'])
                clss = [e['label'] for e in ann_infos[1]['data']]
                c.update(clss)

        return final, dict(c), nb_annotations, nb_objects
           
    def _to_picsellia_format_bbox(self, imgid, ann_list: list):
        picsellia_list = []
        for ann in ann_list:
            class_name = self._find_category_name(ann['category_id'])
            if not class_name:
                continue
            picsellia_list.append({
                        "qa": [],
                        "type": "rectangle",
                        "label": class_name,
                        "rectangle": {
                            "top":    ann['bbox'][1],
                            "left":   ann['bbox'][0],
                            "width":  ann['bbox'][2],
                            "height": ann['bbox'][3] 
                        }
                    
                })
    
        return [imgid, {'data': picsellia_list}]

    def _to_picsellia_format_poly(self, imgid, ann_list: list):
        """
        TODO -> Create the RLE cases for COCO polygon push.
        """
        picsellia_list = []
        for ann in ann_list:
            class_name = self._find_category_name(ann['category_id'])
            if not class_name:
                continue
            if not self._is_rle(ann):
                tmp = {
                            "qa": [],
                            "type": "polygon",
                            "label": class_name,
                            "polygon": {
                                "geometry": []
                            }
                }
                if not len(ann['segmentation'][0]) % 2 == 0:
                    continue

                indexes = [0]
                if isinstance(ann['segmentation'][0], list):
                    indexes += [(i+2) for i in range(len(ann['segmentation'][0])//2)]
                else:
                    indexes += [(i+2) for i in range(len(ann['segmentation'])//2)]
                for coords in chunks(ann["segmentation"][0], 2):
                    coord = {
                        'x' : coords[0],
                        'y' : coords[1]
                    }
                    tmp['polygon']['geometry'].append(coord)
                picsellia_list.append(tmp)

        return [imgid, {'data': picsellia_list}]

    def _is_rle(self, annotations):
        return isinstance(annotations['segmentation'], dict)



class PVOCParser:
    def __init__(self, path: str=None):
        self.annpath = path 
        if not os.path.isdir(self.annpath):
            raise exceptions.ResourceNotFoundError("Please provide a valid path to your .xml file directory.")
        self.xmlpaths = [os.path.join(self.annpath, e) for e in os.listdir(self.annpath)]


    def _find_dataset_type(self,):
        tree = ET.parse(self.xmlpaths[0])
        root = tree.getroot()
        obj = root.find('object')
        polygon = obj.find('polygon')
        self.dataset_type = "detection" if polygon is None else "segmentation"
        return self.dataset_type


    def _get_class_name(self, obj):
        name = obj.find('name').text.strip().lower()
        return name

    def _get_img_infos(self, root, tags):
        w, h = self._get_width_height(root)
        filename = self._get_file_name(root)
        return {
                'internal_key': os.path.join(str(uuid4()), filename),
                'external_url': filename,
                'height': h,
                'width': w,
                'tags': tags,
                'source': 'sdk'
            }

    def _get_width_height(self, root):
        size=root.find('size')
        width = int(size.find('width').text)
        height = int(size.find('height').text)
        return width, height

    def _get_bbox_coord(self, obj):
        xml_box = obj.find('bndbox')
        xmin = (float(xml_box.find('xmin').text) - 1)
        ymin = (float(xml_box.find('ymin').text) - 1)
        xmax = (float(xml_box.find('xmax').text) - 1)
        ymax = (float(xml_box.find('ymax').text) - 1)

        return {
            'top': ymin,
            'left': xmin,
            'width': xmax-xmin,
            'height': ymax-ymin,
        }  

    def _get_file_name(self, root):
        name = root.find('filename').text
        return name

    def _generate_data_bbox(self, tags, root, classes):
        data = []
        for obj in root.iter('object'):
            label = self._get_class_name(obj)
            if len(classes) < 1:
                classes.append((
                    label, 'rectangle'
                ))
            elif (label, 'rectangle') not in classes:
                classes.append((
                    label, 'rectangle'
                ))
            data.append({
                "qa": [],
                "type": "rectangle",
                "label": label,
                "rectangle": self._get_bbox_coord(obj)
            })
        image_infos = self._get_img_infos(root, tags)
        return classes, image_infos, (image_infos['external_url'], {'data': data})

    def _generate_data_poly(self, tags, root, classes):
        data = []
        for obj in root.iter('object'):
            label = self._get_class_name(obj)
            if len(classes) < 1:
                classes.append((
                    label, 'rectangle'
                ))
            elif (label, 'rectangle') not in classes:
                classes.append((
                    label, 'rectangle'
                ))
            data.append({
                "qa": [],
                "type": "polygon",
                "label": label,
                "rectangle": [],
                "polygon": {
                    "geometry": self._get_polygon_coord(obj)
                }
            })
        image_infos = self._get_img_infos(root, tags)
        return classes, image_infos, (image_infos['external_url'], {'data': data})

    def _get_polygon_coord(obj):
        i = 1
        ann = []
        polygon = obj.find('polygon')
        while True:
            x = 'x' + str(i)
            y = 'y' + str(i)
            x1 = polygon.find(x)
            y1 = polygon.find(y)

            if x1 is None or y1 is None:
                break 

            x1 = int(x1.text)
            y1 = int(y1.text)
            i += 1
            ann.append({
                'x': x1,
                'y': y1
            })
        return ann

    def _generate_images_labels_annotations(self, tags):

        dataset_type = self._find_dataset_type()
        classes, image_infos, ann_datas = [], [], []
        
        c = collections.Counter()
        nb_annotations, nb_objects = 0, 0

        dataset_type = self._find_dataset_type()

        for path in self.xmlpaths:
            tree = ET.parse(path)
            root = tree.getroot()

            if dataset_type == "detection":
                classes, image_info, ann_data = self._generate_data_bbox(
                    tags=tags, root=root, classes=classes
                )
            else:
                classes, image_info, ann_data = self._generate_data_poly(
                    tags=tags, root=root, classes=classes
                )
            image_infos.append(image_info)
            ann_datas.append(ann_data)
            nb_annotations += 1
            nb_objects += len(ann_data[1]['data'])
            cc = [e['label'] for e in ann_data[1]['data']]
            c.update(cc)
        return classes, image_infos, ann_datas, dict(c), nb_annotations, nb_objects