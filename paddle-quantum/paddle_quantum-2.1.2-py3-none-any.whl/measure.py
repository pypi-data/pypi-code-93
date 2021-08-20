# Copyright (c) 2021 Institute for Quantum Computing, Baidu Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


'''
the class for measure
'''

import math
import numpy as np
import paddle

from paddle.autograd import PyLayer
from paddle_quantum.utils import finite_difference_gradient, param_shift_gradient


class Measure(PyLayer):
    '''
    自定义测量算子，实现可训练的基于测量的采样
    '''
    @staticmethod
    def forward(ctx, state, which_qubits=None, shots=0, mode=None, grad_func=None, *args):
        '''前向计算的函数

        Args:
            ctx(PyLayerContext): 用于存储反向计算过程中需要知道的前向计算过程中的变量
            state(Tensor): 电路运行得到的量子态
            which_qubits(list): 要测量的量子比特。默认值为 `None`，表示全部测量
            shots(int): 测量的采样次数。默认为 0，表示计算解析解
            mode(str): 量子电路的运行模式，波函数向量模式或密度矩阵模式。默认为波函数向量模式

        Returns:
            Tensor: 测量得到的概率值
        '''
        def measure(state, which_qubits, shots, mode):
            '''测量的函数

            Args:
                state(Tensor): 电路运行得到的量子态
                which_qubits(list): 要测量的量子比特。默认值为 `None`，表示全部测量
                shots(int): 测量的采样次数。默认为 0，表示计算解析解
                mode(str): 量子电路的运行模式，波函数向量模式或密度矩阵模式。默认为波函数向量模式
            '''
            if mode is None:
                mode = 'state_vector'
            if mode != 'state_vector' and mode != 'density_matrix':
                raise ValueError("Can't recognize the mode of quantum state.")
            if mode == 'density_matrix':
                diag = np.diag(state.numpy())
                state = paddle.to_tensor(np.sqrt(diag))
            qubit_num = int(math.log2(state.size))
            prob_amplitude = paddle.abs(state).tolist()
            prob_amplitude = [item ** 2 for item in prob_amplitude]
            if which_qubits is None:
                measured_num = qubit_num
                prob_array = prob_amplitude
            else:
                which_qubits.sort()
                measured_num = len(which_qubits)
                prob_array = [0] * (2 ** measured_num)
                for i in range(2 ** qubit_num):
                    binary = bin(i)[2:]
                    binary = '0' * (qubit_num - len(binary)) + binary
                    target_qubits = str()
                    for qubit_idx in which_qubits:
                        target_qubits += binary[qubit_idx]
                    prob_array[int(target_qubits, base=2)] += prob_amplitude[i]
            if shots == 0:
                result = prob_array
            else:
                result = [0] * (2 ** measured_num)
                samples = np.random.choice(list(range(2 ** measured_num)), shots, prob_array)
                for item in samples:
                    result[item] += 1
                result = [item / shots for item in result]
            return paddle.to_tensor(result)

        ctx.measure_func = measure
        ctx.which_qubits = which_qubits
        ctx.shots = shots
        ctx.mode = mode
        ctx.args = args
        if grad_func is None:
            grad_func = 'finite_diff'
        assert grad_func in {'finite_diff', 'param_shift'}, "grad_func must be one of 'finite_diff' or 'param_shift'"
        if grad_func == "finite_diff":
            ctx.grad_func = finite_difference_gradient
        else:
            ctx.grad_func = param_shift_gradient
        return measure(state, which_qubits, shots, mode)

    @staticmethod
    def backward(ctx, dy):
        '''反向函数

        Args:
            ctx(PyLayerContext): 用于存储反向计算过程中需要知道的前向计算过程中的变量
            dy (Tensor): expecval的梯度

        Returns:
            Tensor: theta的梯度
        '''
        grad_func = ctx.grad_func
        which_qubits = ctx.which_qubits
        shots = ctx.shots
        mode = ctx.mode
        args = ctx.args
        grad = dy * grad_func(ctx.measure_func, which_qubits, shots, mode, *args)
        return grad
