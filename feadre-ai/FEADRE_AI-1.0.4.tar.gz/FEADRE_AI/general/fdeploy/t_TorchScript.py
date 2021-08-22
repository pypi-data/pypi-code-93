import torch  # This is all you need to use both PyTorch and TorchScript!
from torchvision import models

from ftools.f_general import fshow_time

print(torch.__version__)


class MyCell(torch.nn.Module):
    def __init__(self):
        super(MyCell, self).__init__()
        self.linear = torch.nn.Linear(4, 4)

    def forward(self, x, h):
        # for i in range(x.size(0)):  # 这种动态的 用trace要报错
        for i in range(7):
            new_h = torch.tanh(self.linear(x) + h)
        return new_h, new_h


class MyDecisionGate(torch.nn.Module):
    def forward(self, x):
        if x.sum() > 0:
            return x
        else:
            return -x


class MyCell2(torch.nn.Module):
    def __init__(self, dg):
        super(MyCell2, self).__init__()
        self.dg = dg
        self.linear = torch.nn.Linear(4, 4)

    def forward(self, x, h):
        new_h = torch.tanh(self.dg(self.linear(x)) + h)
        return new_h, new_h


class MyRNNLoop(torch.nn.Module):
    def __init__(self):
        super(MyRNNLoop, self).__init__()
        self.cell = torch.jit.script(MyCell2(MyDecisionGate()), (x, h))  # 复杂的在属性里进行处理
        self.cell = torch.nn.Linear(4, 4)

    def forward(self, xs):
        h, y = torch.zeros(3, 4), torch.zeros(3, 4)
        for i in range(xs.size(0)):
            y, h = self.cell(xs[i], h)
        return y, h


if __name__ == '__main__':
    x = torch.rand(3, 4)
    h = torch.rand(3, 4)

    # my_cell = MyCell()
    # print(my_cell(x, h))

    # traced_cell = torch.jit.trace(my_cell, (x, h))
    # print(traced_cell)
    # print(traced_cell.graph)
    # print(traced_cell.code)
    # print(traced_cell(x, h))

    # my_cell = MyCell2(MyDecisionGate())
    # print(my_cell(x, h))
    # scripted_cell = torch.jit.script(my_cell)
    # # scripted_cell = torch.jit.trace(my_cell, (x, h))  # 警告提示
    # print(scripted_cell.code)
    # print(scripted_cell(x, h))

    # rnn_loop = torch.jit.trace(MyRNNLoop(),(x))
    # print(rnn_loop.code)

    # traced_cell.save('wrapped_rnn.pt')
    # loaded = torch.jit.load('wrapped_rnn.pt')
