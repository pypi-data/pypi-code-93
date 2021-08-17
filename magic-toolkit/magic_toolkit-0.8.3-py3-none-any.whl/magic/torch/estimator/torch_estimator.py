import os
import time
from .estimator import Estimator
from magic.dataloader import DataLoader
from magic.dataset import ConcatDataset
from magic import log
import torch
from torch.utils.tensorboard import SummaryWriter

class TorchEstimator(Estimator):

    def __init__(self, model, pre_trained, inputs_size,
                 train_batch=32, total_epoch=100, epoch_interval=5, num_workers=8,
                 loss_avg_step=10, cudnn_benchmark=True):
        """
        :param model:  torch.nn.Module
        :param pre_trained: path for saving and loading
        :param inputs_size: list of size, [[C, H, W], [C, H, W], ...]
        :param train_batch:
        :param epoch_range: [start, stop, step]
        :param num_workers:
        :param loss_avg_step:
        """
        super(TorchEstimator, self).__init__(model, pre_trained, inputs_size)

        # pre-defined
        self.train_batch = train_batch
        self.num_workers = num_workers
        self.total_epoch = total_epoch
        self.epoch_interval = epoch_interval
        self.loss_avg_step = loss_avg_step
        self.epoch_start = 0
        self.current_epoch = 0
        self.summary_writer = None
        self.epoch_loss_mean = [float('inf'), 0]  # mean of loss respected to last epoch and current epoch
        self.model_backup_list = []

        # do something when class was initialized
        if cudnn_benchmark:
            torch.backends.cudnn.enabled = True
            torch.backends.cudnn.benchmark = True

    def backward_optim(self, train_dataset=None, loss_fn=None, optimizer=None, scheduler=None):
        """
        train process
        :param train_dataset: dataset or a list of dataset
        :param loss_fn: loss_fn(model, data)
        :param optimizer: SGD ...
        :param scheduler:
        :return:
        """
        self.set_train_mode()

        assert train_dataset, "need train dataset"
        assert loss_fn, "need loss function"
        assert optimizer, "need optimizer to update parameters"

        # Releases all unoccupied cached memory currently held by the caching allocator
        # so that those can be used in other GPU application and visible in nvidia-smi.
        torch.cuda.empty_cache()

        if torch.cuda.device_count() > 1:
            self.model = torch.nn.DataParallel(self.model)

        # concatenate datasets
        train_dataset = ConcatDataset(train_dataset) if isinstance(train_dataset, list) else train_dataset
        n_samples_train = len(train_dataset)
        steps_per_epoch = (n_samples_train + self.train_batch - 1) // self.train_batch
        log.info("n_samples_train: {}".format(n_samples_train))
        train_loader = DataLoader(dataset=train_dataset,
                                  batch_size=self.train_batch,
                                  num_workers=self.num_workers,
                                  shuffle=True,
                                  drop_last=False)

        # resume last training if optimizer_state_dist is not empty
        if self.resume_last_training:
            log.info("resume last training")
            self.epoch_start = self.checkpoint["epoch"]
            optimizer.load_state_dict(self.checkpoint["optimizer"])
            self.summary_writer = SummaryWriter(log_dir=self.checkpoint["logdir"])
            self.epoch_loss_mean[0] = self.checkpoint["epoch_loss_mean"]
        else:
            self.summary_writer = SummaryWriter()  # tensorboard

        log.info("training ...")

        for epoch in range(self.epoch_start, self.total_epoch):
            self.current_epoch = epoch
            self.run_steps(epoch, steps_per_epoch, train_loader, optimizer, loss_fn)

            if epoch % self.epoch_interval == self.epoch_interval - 1:
                self.execute_epoch_interval()

            # adjust learning rate every epoch
            if scheduler is not None:
                scheduler.step()

        # exit from training
        self.summary_writer.close()

    def run_steps(self, epoch, steps_per_epoch, train_loader, optimizer, loss_fn):
        # print learning rate
        lr = optimizer.state_dict()["param_groups"][0]["lr"]
        self.summary_writer.add_scalar("train/learning rate", lr, epoch)

        running_loss = dict()
        time_stamp0 = time.time()
        for i, sample in enumerate(train_loader, 0):
            # zero the parameter gradients
            optimizer.zero_grad()
            # forward + backward + optimize
            loss_dict = loss_fn(self.model, sample)
            assert isinstance(loss_dict, dict)  # loss = {"loss_bp": loss, "conf": conf}
            loss = loss_dict["loss_bp"]
            loss.backward()
            optimizer.step()
            # mean loss of current epoch
            self.epoch_loss_mean[1] = (loss.item() + self.epoch_loss_mean[1] * i) / (i + 1)

            # accumulate loss by specific steps
            for key, value in loss_dict.items():
                if isinstance(value, torch.Tensor):
                    running_loss[key] = running_loss.get(key, 0) + value.item()
                else:
                    running_loss[key] = running_loss.get(key, 0) + value
            # print something by steps
            if i % self.loss_avg_step == self.loss_avg_step - 1:
                step = i + 1
                global_step = epoch * steps_per_epoch + step
                # calculate time consume
                time_stamp1 = time.time()
                time_consume_per_step = (time_stamp1 - time_stamp0) / self.loss_avg_step
                time_stamp0 = time_stamp1
                remain = (steps_per_epoch - step) * time_consume_per_step
                # average loss
                loss_msg = []
                for key, value in running_loss.items():
                    running_loss_avg = value / self.loss_avg_step
                    self.summary_writer.add_scalar('train/' + key, running_loss_avg, global_step)
                    loss_msg.append("{}:{:.6f}".format(key, running_loss_avg))

                log.info("epoch:{} step:{}/{} remain:{:.0f}s {} lr:{:.8f}".format(
                    epoch, step, steps_per_epoch, remain, " ".join(loss_msg), lr))

                for key in running_loss:
                    running_loss[key] = 0

                self.summary_writer.flush()
        # update checkpoint to save
        self.checkpoint["epoch"] = epoch + 1
        self.checkpoint["optimizer"] = optimizer.state_dict()
        self.checkpoint["logdir"] = self.summary_writer.get_logdir()
        self.checkpoint["epoch_loss_mean"] = self.epoch_loss_mean[0]
        self.save(self.pre_trained.split(".")[0] + ".pth" + "_bak")

        # save model when loss reaches current minimum of mean
        log.info("epoch_loss_mean:", self.epoch_loss_mean)
        if self.epoch_loss_mean[1] < self.epoch_loss_mean[0]:
            self.epoch_loss_mean[0] = self.epoch_loss_mean[1]
            pth = self.pre_trained.split(".")[0] + ".pth" + "_epoch{}".format(epoch)
            # update checkpoint to save
            self.checkpoint["epoch_loss_mean"] = self.epoch_loss_mean[0]
            self.save(pth)
            self.model_backup_list.append(pth)
            if len(self.model_backup_list) > 1:
                try:
                    os.remove(self.model_backup_list.pop(0))
                except Exception as err:
                    print(err)

    def execute_epoch_interval(self):
        # visualize model weights histogram
        # for name, params in self.model.named_parameters():
        #     self.summary_writer.add_histogram(name, params, epoch + 1)
        # self.summary_writer.flush()

        # 执行模型评估
        self.set_eval_mode()
        self.validate()
        self.set_train_mode()

    def validate(self):
        raise NotImplementedError
