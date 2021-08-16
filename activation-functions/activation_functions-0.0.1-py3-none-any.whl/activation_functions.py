import matplotlib.pyplot as plt
import numpy as np


def binaryStep(x):
    ''' It returns '0' if the input is less then zero otherwise it returns one '''
    return np.heaviside(x, 1)


def linear(x):
    ''' y = f(x) It returns the input as it is'''
    return x


def sigmoid(x):
    ''' It returns 1/(1+exp(-x)). where the values lies between zero and one '''
    return 1/(1+np.exp(-x))


def tanh(x):
    ''' It returns the value (1-exp(-2x))/(1+exp(-2x)) and the value returned will be lies in between -1 to 1.'''
    return np.tanh(x)


def RELU(x):
    ''' It returns zero if the input is less than zero otherwise it returns the given input. '''
    return np.maximum(0, x)


def LeakyReLu(x):
    ''' It returns zero if the input is less than zero otherwise it returns the given input multiplied by 0.001. Negative inputs stay negative. '''
    if x > 0:
        return x
    else:
        return 0.001*x


def softmax(x):
    ''' Compute softmax values for each sets of scores in x. '''
    return np.exp(x) / np.sum(np.exp(x), axis=0)
