# -*-coding: utf-8 -*-
"""
    @Author : panjq
    @E-mail : pan_jinquan@163.com
    @Date   : 2021-07-28 09:09:32
"""
import torch.nn as nn
from torch.utils.data.dataset import Dataset
from torch.utils.data.dataloader import DataLoader
from ..utils import torch_data, torch_tools
from ..engine import engine
from ..engine import comm


class EngineTrainer(engine.Engine):
    def __init__(self, cfg):
        super(EngineTrainer, self).__init__(cfg)
        torch_tools.set_env_random_seed()
        self.model = None
        self.optimizer = None
        self.criterion = None
        self.train_loader = None
        self.test_loader = None
        self.num_epochs = cfg.num_epochs
        self.num_steps = 0  # 每个epoch的迭代次数
        self.num_samples = 0  # 训练的样本数目
        self.criterion = None  # 损失函数
        self.progress = cfg.progress  # 是否显示进度条
        self.is_main_process = comm.is_main_process()
        self.world_size = comm.get_world_size()
        self.local_rank = comm.get_local_rank()
        self.device = comm.get_device(cfg.gpu_id)

    def build(self, cfg, **kwargs):
        self.train_loader = self.build_train_loader(cfg, **kwargs)
        self.test_loader = self.build_test_loader(cfg, **kwargs)
        self.num_steps = len(self.train_loader)
        self.num_samples = len(self.train_loader.sampler)
        self.model = self.build_model(cfg, **kwargs)
        self.optimizer = self.build_optimizer(cfg, **kwargs)
        self.criterion = self.build_criterion(cfg, **kwargs)
        self.callbacks = self.build_callbacks(cfg, **kwargs)

    def build_train_loader(self, cfg, **kwargs):
        """定义训练数据"""
        raise NotImplementedError("build_train_loader not implemented!")

    def build_test_loader(self, cfg, **kwargs):
        """定义测试数据"""
        raise NotImplementedError("build_test_loader not implemented!")

    def build_model(self, cfg, **kwargs):
        """定于训练模型"""
        raise NotImplementedError("build_model not implemented!")

    def build_optimizer(self, cfg, **kwargs):
        """定义优化器"""
        raise NotImplementedError("build_optimizer not implemented!")

    def build_criterion(self, cfg, **kwargs):
        """定义损失函数"""
        raise NotImplementedError("build_criterion not implemented!")

    def build_callbacks(self, cfg, **kwargs):
        """定义回调函数"""
        raise NotImplementedError("build_callbacks not implemented!")

    @classmethod
    def build_dataloader(cls, dataset: Dataset, batch_size: int, num_workers: int,
                         shuffle: bool = True, phase: str = "train", **kwargs) -> DataLoader:
        return torch_data.build_dataloader(dataset,
                                           batch_size,
                                           num_workers,
                                           shuffle=shuffle,
                                           phase=phase,
                                           **kwargs)

    @classmethod
    def build_model_parallel(cls, model: nn.Module, device_ids=None, **kwargs) -> nn.Module:
        return torch_data.build_model_parallel(model, device_ids, **kwargs)
