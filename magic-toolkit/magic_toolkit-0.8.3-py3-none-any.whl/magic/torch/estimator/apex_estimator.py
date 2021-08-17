import os
import time
from .estimator import Estimator
from magic.dataloader import DataLoader
from magic import log
import torch
from torch.utils.tensorboard import SummaryWriter

try:
    from apex import amp
except:
    pass

class ApexEstimator(Estimator):
    def __init__(self, model, pre_trained, inputs_size, train_batch, epoch_range, num_workers=8, loss_avg_step=10):
        """
        :param model:  torch.nn.Module
        :param pre_trained: path for saving and loading
        :param inputs_size: list of size, [[C, H, W], [C, H, W], ...]
        :param train_batch:
        :param epoch_range: [start, stop, step]
        :param num_workers:
        :param loss_avg_step:
        """
        super(ApexEstimator, self).__init__(model, pre_trained, inputs_size)
        self.train_batch = train_batch
        self.num_workers = num_workers
        self.epoch_range = epoch_range
        self.loss_avg_step = loss_avg_step
        # pre-defined
        self.current_epoch = 0

    def backward_optim(self, train_dataset=None, loss_fn=None, optimizer=None, scheduler=None, evaluate_fn=None):
        """
        train process
        :param train_dataset: train dataset
        :param loss_fn: loss_fn(model, data)
        :param optimizer: SGD ...
        :param scheduler:
        :param evaluate_fn: eval()
        :return:
        """
        assert train_dataset, "need train dataset"
        assert loss_fn, "need loss function"
        assert optimizer, "need optimizer to update parameters"

        # Releases all unoccupied cached memory currently held by the caching allocator
        # so that those can be used in other GPU application and visible in nvidia-smi.
        torch.cuda.empty_cache()
        self.set_train_mode()

        self.summary_writer = SummaryWriter()  # tensorboard
        self.summary()

        self.model, optimizer = amp.initialize(self.model, optimizer, opt_level="O1")

        if not hasattr(self.model, "module"):
            self.model = torch.nn.DataParallel(self.model)

        n_samples_train = len(train_dataset)
        steps_per_epoch = (n_samples_train + self.train_batch - 1) // self.train_batch
        log.info("n_samples_train: {}".format(n_samples_train))

        train_loader = DataLoader(dataset=train_dataset,
                                  batch_size=self.train_batch,
                                  num_workers=self.num_workers,
                                  shuffle=True,
                                  drop_last=False)

        log.info("training ...")
        epoch_loss_mean = [float('inf'), 0]  # mean of loss respected to last epoch and current epoch
        model_backup_list = []
        for epoch in range(*self.epoch_range[:2]):
            self.current_epoch = epoch

            # print learning rate every epoch
            lr = optimizer.state_dict()["param_groups"][0]["lr"]
            self.summary_writer.add_scalar("train/learning rate", lr, epoch + 1)
            self.summary_writer.flush()

            running_loss = dict()
            time_stamp0 = time.time()
            for i, sample in enumerate(train_loader, 0):
                # zero the parameter gradients
                optimizer.zero_grad()
                # forward + backward + optimize
                loss_dict = loss_fn(self.model, sample)
                assert isinstance(loss_dict, dict)  # loss = {"loss_bp": loss, "conf": conf}
                loss = loss_dict["loss_bp"]
                with amp.scale_loss(loss, optimizer) as scaled_loss:
                    scaled_loss.backward()
                optimizer.step()
                # mean loss of current epoch
                epoch_loss_mean[1] = (loss.item() + epoch_loss_mean[1] * i) / (i + 1)

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
                        epoch + 1, step, steps_per_epoch, remain, " ".join(loss_msg), lr))

                    # flush data to tensorboard
                    self.summary_writer.flush()
                    for key in running_loss:
                        running_loss[key] = 0

            # do something by epoch frequency
            if epoch % self.epoch_range[2] == self.epoch_range[2] - 1:
                # visualize model weights histogram
                # for name, params in self.model.named_parameters():
                #     self.summary_writer.add_histogram(name, params, epoch + 1)
                # self.summary_writer.flush()

                # 执行模型评估
                if evaluate_fn:
                    self.set_eval_mode()
                    evaluate_fn()
                    self.set_train_mode()

            # adjust learning rate every epoch
            if scheduler is not None:
                scheduler.step()

            # save model when loss reaches current minimum of mean
            log.info("epoch_loss_mean:", epoch_loss_mean)
            if epoch_loss_mean[1] < epoch_loss_mean[0]:
                epoch_loss_mean[0] = epoch_loss_mean[1]
                pth = self.pre_trained.split(".")[0] + ".pth" + "_epoch{}".format(epoch + 1)
                self.save(pth)
                model_backup_list.append(pth)
                if len(model_backup_list) > 1:
                    try:
                        os.remove(model_backup_list.pop(0))
                    except Exception as err:
                        print(err)
            self.save(self.pre_trained.split(".")[0] + ".pth" + "_bak")
        # exit from training
        self.summary_writer.close()
