import os

import numpy as np
import torch
import time
from .loss import LossCounter


class ModelTrainer:
    """
    Class to train object detection models
    """

    def __init__(self, model,
                 optimizer,
                 scheduler,
                 base_dir,
                 device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
                 num_epochs=100,
                 model_file=None,
                 log_path=None,
                 verbose=True,
                 verbose_step=100,
                 keep_models=3):
        """

        :param model: Model to train.
        :param device: Device to train the model on. CPU or CUDA.
        :param optimizer: Model optimizer.
        :param scheduler: Learning rate scheduler for training.
        :param base_dir: Default directory for saving output.
        :param num_epochs: Number of epochs to train. Defaults to 100
        :param model_file: File for loading partially trained models.
        :param log_path: Optional value for specifying log file location
        :param verbose: Boolean for printing output. Defaults to True
        :param verbose_step: Interval on which to print status. Defaults to 100.
        :param keep_models: Maximum number of models to save. Defaults to 3
        """
        self.model = model
        self.device = device
        self.model.to(self.device)
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.num_epochs = num_epochs
        self.base_dir = base_dir
        self.verbose = verbose
        self.verbose_step = verbose_step
        self.keep_models = keep_models
        self.zfill = np.ceil(np.log10(self.verbose_step)).astype(int)
        if model_file:
            self.load(model_file)
        else:
            self.start_epoch = 0
            self.best_summary_loss = []
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

        self.log_path = log_path if log_path else f"{self.base_dir}/log.csv"
        print(f'Fitter prepared. Device is {self.device}')

    def _csv_header(self):
        """
        Writes log file header.
        """
        self.log("Epoch, Stage, Summary Loss, Class Loss, Box Loss", print_line=False)

    @staticmethod
    def _csv_line(summary_loss, epoch, stage):
        """
        Builds the string for one line of logging to csv file.

        :param summary_loss: Total current loss
        :param epoch: Current epoch
        :param stage: Training or Validation
        :return: String to write to log file.
        """
        return f"{epoch}, {stage}, {summary_loss.avg:.5f}," + \
               f"{summary_loss.class_avg:.5f}," + \
               f"{summary_loss.box_avg:.5f}"

    @staticmethod
    def _output_dict(output):
        return {"loss": output["loss"].detach().item(),
                "class_loss": output["class_loss"].detach().item(),
                "box_loss": output["box_loss"].detach().item()}

    @staticmethod
    def _print_line(summary_loss, step, total_steps, stage, t):
        """
        Prints a line of output showing the current status of training.

        :param summary_loss: Total current loss.
        :param step: Current step in epoch.
        :param total_steps: Total number of steps in epoch.
        :param stage: Training or Validation.
        :param t: Start time of training or validation epoch.
        """
        print(
            f"{stage} Step {step}/{total_steps}, " +
            f"summary_loss: {summary_loss.avg:.5f}, " +
            f"class_loss: {summary_loss.class_avg:.5f}, " +
            f"box_loss: {summary_loss.box_avg:.5f}, " +
            f"time: {(time.time() - t):.5f}\n")

    def fit(self, train_loader, validation_loader):
        """
        Trains the model. Saves best models after each epoch and updates learning rate.

        :param train_loader: Data Loader for training data.
        :param validation_loader: Data Loader for validation data.
        """
        if self.start_epoch == 0:
            self._csv_header()
        for epoch in range(self.start_epoch, self.num_epochs):
            # Train one epoch
            summary_loss = self.train(train_loader)

            self.log(self._csv_line(summary_loss, epoch, "Train"))
            self.save(f'{self.base_dir}/last-checkpoint.bin', epoch)

            # Evaluate on validation data.
            summary_loss = self.validate(validation_loader)

            self.log(self._csv_line(summary_loss, epoch, "Val"))

            # Update list of saved models
            if len(self.best_summary_loss) < self.keep_models:
                self.best_summary_loss.append((summary_loss.avg, epoch))
                self.save(f'{self.base_dir}/best-checkpoint-{str(epoch).zfill(self.zfill)}epoch.bin', epoch)
                self.best_summary_loss.sort()
            elif summary_loss.avg < self.best_summary_loss[-1][0]:
                _, old_epoch = self.best_summary_loss.pop()
                self.best_summary_loss.append((summary_loss.avg, epoch))
                self.save(f'{self.base_dir}/best-checkpoint-{str(epoch).zfill(self.zfill)}epoch.bin', epoch)
                os.remove(f'{self.base_dir}/best-checkpoint-{str(old_epoch).zfill(self.zfill)}epoch.bin')
                self.best_summary_loss.sort()

            # Update learning rate.
            if self.scheduler:
                self.scheduler.step()

    def load(self, path):
        """
        Loads saved model, including optimizer, scheduler history, and previous best models.

        :param path: Path of model to load.
        """
        checkpoint = torch.load(path)
        self.model.model.load_state_dict(checkpoint["state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        self.best_summary_loss = checkpoint["best_summary_loss"]
        self.start_epoch = checkpoint["epoch"] + 1

    def log(self, message, print_line=True):
        """
        Write data to log.
        :param message: Message to write.
        :param print_line: Boolean, print message to stdout. Default True.
        """
        if self.verbose and print_line:
            print(message)
        with open(self.log_path, 'a+') as logger:
            logger.write(f'{message}\n')

    def save(self, path, epoch):
        """
        Saves model after training epoch.

        :param path: Path of file for saved model
        :param epoch: Epoch number.
        """
        self.model.eval()
        torch.save({
            "state_dict": self.model.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "best_summary_loss": self.best_summary_loss,
            "epoch": epoch,
        }, path)

    def train(self, train_loader):
        """
        Trains model for one epoch.
        :param train_loader: Data Loader for training data
        :type train_loader: torch.utils.data.DataLoader
        :return: Total Loss on training data for epoch.
        """
        self.model.train()
        summary_loss = LossCounter()
        t = time.time()
        for step, (images, targets) in enumerate(train_loader):
            if self.verbose and step and step % self.verbose_step == 0:
                self._print_line(summary_loss, step, len(train_loader), "Train", t)

            images = torch.stack(images)
            images = images.to(self.device).float()
            batch_size = images.shape[0]
            boxes = [target['bboxes'].to(self.device).float() for target in targets]
            labels = [target['labels'].to(self.device).float() for target in targets]

            self.optimizer.zero_grad()

            output = self.model(images, {'bbox': boxes, 'cls': labels})

            output['loss'].backward()

            summary_loss.update_avg(self._output_dict(output), batch_size)

            self.optimizer.step()

        return summary_loss

    def validate(self, val_loader):
        """
        Evaluates model on validation data after one epoch of training.

        :param val_loader: Data Loader for validation data.
        :type val_loader: torch.utils.data.DataLoader
        :return Total Loss on validation data.
        """
        self.model.eval()
        summary_loss = LossCounter()
        t = time.time()
        for step, (images, targets) in enumerate(val_loader):
            if self.verbose and step and step % self.verbose_step == 0:
                self._print_line(summary_loss, step, len(val_loader), "Val", t)
            with torch.no_grad():
                images = torch.stack(images)
                batch_size = images.shape[0]
                images = images.to(self.device).float()
                boxes = [target['bboxes'].to(self.device).float() for target in targets]
                labels = [target['labels'].to(self.device).float() for target in targets]

                output = self.model(images, {'bbox': boxes, 'cls': labels,
                                             "img_scale": None,
                                             "img_size": None})
                summary_loss.update_avg(self._output_dict(output), batch_size)

        return summary_loss
