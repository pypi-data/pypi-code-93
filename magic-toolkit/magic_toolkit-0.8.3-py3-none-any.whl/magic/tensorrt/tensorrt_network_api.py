"""
Creating A Network Definition From Scratch Using The Python API.
The network definition reference is used to add various layers to the network.
"""
import tensorrt as trt
import numpy as np

class AddTensorRTLayer():
    def __init__(self, network, weights=None):
        self.network = network
        self.weights = weights

    def get_trt_plugin(self, plugin_name: str, parameters: list):
        PLUGIN_CREATORS = trt.get_plugin_registry().plugin_creator_list
        plugin_name_list = [plugin_creator.name for plugin_creator in PLUGIN_CREATORS]
        print("pluginNameList:", plugin_name_list)

        field_collection = trt.PluginFieldCollection()
        for param in parameters:
            field_collection.append(trt.PluginField(param['name'], param['data'], param['type']))
        for plugin_creator in PLUGIN_CREATORS:
            if plugin_creator.name == plugin_name:
                plugin = plugin_creator.create_plugin(name=plugin_name, field_collection=field_collection)
                print('{} creation completed'.format(plugin_name))
                return plugin
        raise RuntimeError('{} not exist!'.format(plugin_name))

    def input(self, name, shape, dtype=trt.DataType.FLOAT):
        input = trt.INetworkDefinition.add_input(self.network, name=name, shape=shape, dtype=dtype)
        return input

    def constant(self, numpyArr: np.array):
        shape = trt.Dims(numpyArr.shape)
        layer = self.network.add_constant(shape, np.array(numpyArr, dtype=np.float32).copy())
        return layer.get_output(0)

    def reshape(self, input, shape):
        shuffle = trt.INetworkDefinition.add_shuffle(self.network, input)
        shuffle.reshape_dims = shape
        return shuffle.get_output(0)

    def concatenate(self, inputs: list, axis=0):
        concatenate = trt.INetworkDefinition.add_concatenation(self.network, inputs)
        concatenate.axis = axis
        return concatenate.get_output(0)

    def Conv2d(self, input, out_channels, kernel_size, stride=(1, 1), padding=(0, 0), layerName='', dilation=(1, 1)):
        kernel = self.weights[layerName + '.weight'].astype(np.float32)
        bias = self.weights[layerName + '.bias'].astype(np.float32)
        layer = trt.INetworkDefinition.add_convolution(self.network, input, out_channels, kernel_size, kernel, bias)
        layer.stride = stride
        layer.padding = padding
        layer.dilation = dilation
        return layer.get_output(0)

    def MaxPool2d(self, input, kernel_size=(2, 2), stride=(2, 2)):
        layer = trt.INetworkDefinition.add_pooling(self.network, input, type=trt.PoolingType.MAX,
                                                   window_size=kernel_size)
        layer.stride = stride
        return layer.get_output(0)

    def BatchNorm2d(self, input, layerName):
        gamma = self.weights[layerName + '.weight'].astype(np.float32)
        beta = self.weights[layerName + '.bias'].astype(np.float32)
        mean = self.weights[layerName + '.running_mean'].astype(np.float32)
        var = self.weights[layerName + '.running_var'].astype(np.float32)
        scale = gamma / np.sqrt(var + 1e-05)
        shift = beta - mean * scale
        layer = trt.INetworkDefinition.add_scale(self.network, input, mode=trt.ScaleMode.CHANNEL, shift=shift,
                                                 scale=scale)
        return layer.get_output(0)

    def activation_fn(self, input, type=trt.ActivationType.SIGMOID):
        activation = trt.INetworkDefinition.add_activation(self.network, input, type)
        return activation.get_output(0)

    def Linear(self, input, num_outputs, layerName):
        shuffle = trt.INetworkDefinition.add_shuffle(self.network, input)
        shuffle.reshape_dims = (-1, 1, 1)

        kernel = self.weights[layerName + '.weight'].astype(np.float32)
        bias = self.weights[layerName + '.bias'].astype(np.float32)
        fc = trt.INetworkDefinition.add_fully_connected(self.network, shuffle.get_output(0), num_outputs, kernel, bias)
        shuffle2 = trt.INetworkDefinition.add_shuffle(self.network, fc.get_output(0))
        shuffle2.reshape_dims = (num_outputs,)
        return shuffle2.get_output(0)

    def matrix_multiply(self, input0, input1, MatrixOperation='vector*matrix'):
        """ MatrixOperation
        matrix * matrix -> matrix
        matrix * vector -> vector
        vector * matrix -> vector
        vector * vector -> scalar
        """
        OperationDict = {'matrix*matrix': (trt.MatrixOperation.NONE, trt.MatrixOperation.NONE),
                         'matrix*vector': (trt.MatrixOperation.NONE, trt.MatrixOperation.VECTOR),
                         'vector*matrix': (trt.MatrixOperation.VECTOR, trt.MatrixOperation.NONE),
                         'vector*vector': (trt.MatrixOperation.VECTOR, trt.MatrixOperation.VECTOR)}
        op0, op1 = OperationDict[MatrixOperation]
        layer = trt.INetworkDefinition.add_matrix_multiply(self.network, input0, op0, input1, op1)
        return layer.get_output(0)

    def AdaptiveMaxPool2d(self, input, output_size: tuple):
        """output_size --> height, width """
        parameters = [
            {'name': 'H_output', 'data': np.array(output_size[0], dtype=np.int32), 'type': trt.PluginFieldType.INT32},
            {'name': 'W_output', 'data': np.array(output_size[1], dtype=np.int32), 'type': trt.PluginFieldType.INT32}
        ]
        layer = trt.INetworkDefinition.add_plugin_v2(self.network, [input],
                                                     plugin=self.get_trt_plugin('adaptive_MaxPool2d', parameters))
        return layer.get_output(0)

    def ROIMaxPool(self, input, rois, output_size: tuple):
        """output_size --> height, width """
        parameters = [
            {'name': 'H_output', 'data': np.array(output_size[0], dtype=np.int32), 'type': trt.PluginFieldType.INT32},
            {'name': 'W_output', 'data': np.array(output_size[1], dtype=np.int32), 'type': trt.PluginFieldType.INT32}
        ]
        layer = trt.INetworkDefinition.add_plugin_v2(self.network, [input, rois],
                                                     plugin=self.get_trt_plugin('ROIMaxPool', parameters))
        return layer.get_output(0)

    def argmax(self, input, topk=1, reduceAxis=1):
        """ return max and index
        axes value for NCHW,  {C: 1, H: 2, W: 4}
        """
        layer = trt.INetworkDefinition.addNone_topk(self.network, input, trt.TopKOperation.MAX, k=topk, axes=reduceAxis)
        return layer.get_output(1)

    def ElementWise(self, input1, input2, op=trt.ElementWiseOperation.SUM):
        layer = self.network.add_elementwise(input1, input2, op)
        return layer.get_output(0)

    def Unary(self, input, op=trt.UnaryOperation.EXP):
        layer = self.network.add_unary(input, op)
        return layer.get_output(0)

    def Slice(self, input, start, shape, stride):
        layer = self.network.add_slice(input, start, shape, stride)
        return layer.get_output(0)

if __name__ == '__main__':

    TRT_LOGGER = trt.Logger(trt.Logger.VERBOSE)
    with trt.Builder(TRT_LOGGER) as builder, builder.create_network() as network:
        builder.max_workspace_size = 1 << 30  # 1GB
        builder.max_batch_size = 1  # frist dimension for input

        nn = AddTensorRTLayer(network, None)
        input1 = nn.input("input1", (13, 13, 3, 8))
        input2 = nn.input("input2", (13, 13, 3, 1))
        net = nn.ElementWise(input1, input2, trt.ElementWiseOperation.SUM)
        net = nn.Unary(net)
        net = nn.activation_fn(net, trt.ActivationType.SIGMOID)
        const = nn.constant(np.random.randn(13, 13, 3, 8))
        net = nn.ElementWise(net, const, trt.ElementWiseOperation.PROD)
        pred_xy = nn.Slice(net, [0, 0, 0, 0], [13, 13, 3, 2], [1,1,1,1])
        pred_wh = nn.Slice(net, [0, 0, 0, 2], [13, 13, 3, 2], [1,1,1,1])
        pred_conf = nn.Slice(net, [0, 0, 0, 4], [13, 13, 3, 1], [1,1,1,1])
        pred_cls = nn.Slice(net, [0, 0, 0, 5], [13, 13, 3, 3], [1,1,1,1])
        output = nn.concatenate([pred_xy, pred_wh, pred_conf, pred_cls], axis=3)

        network.mark_output(output)

############################################################################################
        for i in range(network.num_layers):
            layer = network.get_layer(i)
            print(layer.name, '-- ', layer.get_output(0).shape)

        print('display network output ', '#'*50)
        for i in range(network.num_outputs):
            ret = network.get_output(i)
            print(ret.name, '---', ret.shape)

        engine = builder.build_cuda_engine(network)

