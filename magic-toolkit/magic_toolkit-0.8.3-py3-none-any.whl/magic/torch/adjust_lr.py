import numpy as np
from torch.optim.lr_scheduler import LambdaLR

class CosineAnnealingWarm(LambdaLR):
    def __init__(self, optimizer, T_warm=10, T_max=100, eta_max=1, eta_min=0.001):
        """
        lr decay factor
        :param T_warm: num of epochs for warm start
        :param T_max: cycle of epoch
        :param eta_max: defaut 1
        :param eta_min: defaut 0.001
        """
        self.eta_min = eta_min
        self.eta_max = eta_max
        self.T_max = T_max
        self.T_warm = T_warm
        self.factor = 1.0
        super(CosineAnnealingWarm, self).__init__(optimizer, lr_lambda=self.lr_lambda)

    def lr_lambda(self, epoch):
        if epoch < self.T_warm:
            alpha = self.eta_min + (self.eta_max - self.eta_min) / self.T_warm * epoch  # epoch start from 0
        else:
            alpha = self.eta_min + 0.5 * (self.eta_max - self.eta_min) * \
                    (1 + np.cos((epoch - self.T_warm) / self.T_max * np.pi))
        return alpha

if __name__ == '__main__':
    from torch.utils.tensorboard import SummaryWriter
    import torch
    from torchvision.models import resnet18

    summary = SummaryWriter()
    model = resnet18()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9, weight_decay=0)
    scheduler = CosineAnnealingWarm(optimizer, 10, 100)
    for i in range(500):
        lr = optimizer.param_groups[0]['lr']
        summary.add_scalar("lr", lr, i)
        scheduler.step()
    summary.close()
