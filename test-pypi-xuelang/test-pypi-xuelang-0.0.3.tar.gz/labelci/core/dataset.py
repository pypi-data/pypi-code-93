# encoding: utf-8
# @Time: 2021/8/16 5:31 下午
# @Author: Zuo
# @File: dataset.py
# @Desc:
from typing import Optional
from labelci.core.client.client import DataHubClient
from labelci.core.index import Index
from labelci.core.tensor import Tensor
from labelci.common.utils import project_exists, get_filename, dir_exists
from labelci.common.exception.labelci_sdk_exception import PropertyDoesNotExistError


class Dataset:
    def __init__(self,
                 url: str,
                 token: str,
                 index: Optional[Index] = None,
                 ):
        self.token = token
        self.url = url
        self.client = DataHubClient(self.url, self.token)
        self.index = index or Index()
        self.tensors: dict = {}

    @property
    def num_samples(self) -> int:
        """Returns the length of the smallest tensor.
        Ignores any applied indexing and returns the total length.
        """
        return min(map(len, self.tensors.values()), default=0)

    def __len__(self):
        """Returns the length of the smallest tensor"""
        tensor_lengths = [len(tensor.data) for tensor in self.tensors.values()]

        return min(tensor_lengths, default=0)

    def __getattr__(self, key):
        data_dic = self.tensors
        if key in data_dic:
            return data_dic[key]

        return self.__dict__[key]

    def list(self):
        datasets = self.client.get_project_list()

        return datasets

    def load(self, project_id):
        """
        Return data by project_id
        """
        self.client.check_project_id(project_id)
        data = self.client.get_project_tasks(project_id)

        self._load_meta(data)

        return self

    def export(self, project_id, export_type, export_path, all_data: bool = False):
        """
        Export annotated tasks as a file in a specific format.
        """
        self.client.check_project_id(project_id)
        data = self.client.export_project(project_id, export_type, all_data)

        filename = get_filename(project_id)
        dir_exists(export_path)
        file_path = export_path+"/"+filename+"."+export_type
        with open(file_path, "w", encoding="utf8") as f:
            f.write(data.decode(encoding="utf8"))

        return file_path

    def _load_meta(self, data):
        """Load data into tensors.
        """
        images = []
        labels = []
        for item in data:
            images.append(item["data"].get("image"))
            labels.append(item["annotations"])
        self.tensors["images"] = Tensor("images", images, self.client)
        self.tensors["labels"] = Tensor("labels", labels, self.client)
