import numpy as np

#### activation functions
class activationRELu:
    def forward(self,x):
        return np.maximum(0,x)



class Layer_Dense:
    def __init__(self,n_input,n_neuron,activation=activationRELu(),biaseszeroes=False):
        self.weights = 0.10*np.random.randn(n_input,n_neuron)
        if biaseszeroes:
            self.biases = np.zeros(n_neuron)
        else:
            self.biases = 0.10*np.random.randn(n_neuron)
        self.activation = activation
    def forward(self,inputs):
        self.output = self.activation.forward(np.dot(inputs,self.weights) + self.biases)
        return self.output

if __name__ == '__main__':
    X =[[2.7,5],
        [4.8,1.2]]
    l = Layer_Dense(2,3)
    print(l.forward(X))
