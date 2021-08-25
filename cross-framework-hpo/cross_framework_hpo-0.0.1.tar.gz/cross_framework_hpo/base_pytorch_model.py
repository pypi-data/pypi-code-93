from torch import nn
import pytorch_lightning as pl
import torchvision
import torch
import statistics


class BasePytorchModel(pl.LightningModule):
    def __init__(self, config):
        super().__init__()
        self.model = None
        # this is meant to operate on logits
        self.criterion = nn.CrossEntropyLoss()
        self.config = config
        self.test_loss = None
        self.test_accuracy = None
        self.accuracy = pl.metrics.Accuracy()
        self.training_loss_history = []
        self.avg_training_loss_history = []
        self.latest_training_loss_history = []
        self.training_loss_history = []

    def train_dataloader(self):
        return torch.utils.data.DataLoader(torchvision.datasets.CIFAR10("/tmp", train=True,
                                                                      transform=torchvision.transforms.ToTensor(),
                                                                      target_transform=None, download=True),
                                           batch_size=int(self.config['batch_size']), num_workers=0, shuffle=False)

    def test_dataloader(self):
        return torch.utils.data.DataLoader(torchvision.datasets.CIFAR10("/tmp", train=False,
                                                                      transform=torchvision.transforms.ToTensor(),
                                                                      target_transform=None, download=True),
                                           batch_size=int(self.config['batch_size']), num_workers=0, shuffle=False)

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.config['learning_rate'],
                                     eps=self.config['adam_epsilon'])
        return optimizer

    def forward(self, x):
        return self.model(x)

    def training_step(self, train_batch, batch_idx):
        x, y = train_batch
        return {'forward': self.forward(x), 'expected': y}

    def training_step_end(self, outputs):
        loss = self.criterion(outputs['forward'], outputs['expected'])
        logs = {'train_loss': loss}
        # pdb.set_trace()
        return {'loss': loss, 'logs': logs}

    def training_epoch_end(self, outputs):
        # pdb.set_trace()
        loss = []
        for x in outputs:
            loss.append(float(x['loss']))
        avg_loss = statistics.mean(loss)
        # tensorboard_logs = {'train_loss': avg_loss}
        self.avg_training_loss_history.append(avg_loss)
        self.latest_training_loss_history.append(loss[-1])
        # return {'avg_train_loss': avg_loss, 'log': tensorboard_logs}

    def test_step(self, test_batch, batch_idx):
        x, y = test_batch
        return {'forward': self.forward(x), 'expected': y}

    def test_step_end(self, outputs):
        loss = self.criterion(outputs['forward'], outputs['expected'])
        accuracy = self.accuracy(outputs['forward'], outputs['expected'])
        logs = {'test_loss': loss, 'test_accuracy': accuracy}
        return {'test_loss': loss, 'logs': logs, 'test_accuracy': accuracy}

    def test_epoch_end(self, outputs):
        loss = []
        for x in outputs:
            loss.append(float(x['test_loss']))
        avg_loss = statistics.mean(loss)
        # tensorboard_logs = {'test_loss': avg_loss}
        self.test_loss = avg_loss
        accuracy = []
        for x in outputs:
            accuracy.append(float(x['test_accuracy']))
        avg_accuracy = statistics.mean(accuracy)
        self.test_accuracy = avg_accuracy

def base_pytorch_function(config, supplied_model):
    torch.manual_seed(0)
    model_class = BasePytorchModel(config)
    model_class.model = supplied_model
    model_class.model.train()
    try:
        trainer = pl.Trainer(max_epochs=config['epochs'], gpus=[0])
    except:
        print("WARNING: training on CPU only, GPU[0] not found.")
        trainer = pl.Trainer(max_epochs=config['epochs'])
    trainer.fit(model_class)
    trainer.test(model_class)
    return (model_class.test_accuracy, model_class.model, model_class.avg_training_loss_history,
            model_class.latest_training_loss_history)