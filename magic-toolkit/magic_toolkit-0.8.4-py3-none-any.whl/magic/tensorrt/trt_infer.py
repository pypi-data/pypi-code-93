import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit


class HostDeviceMem(object):
    def __init__(self, host_mem, device_mem):
        self.host = host_mem
        self.device = device_mem

    def __str__(self):
        return "Host:\n" + str(self.host) + "\nDevice:\n" + str(self.device)

    def __repr__(self):
        return self.__str__()


class TrtSession(object):
    def __init__(self):
        print("tensorrt version:", trt.__version__)
        print("cuda version:", cuda.get_version())
        self.TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

    def load_engine(self, engine_path):
        with open(engine_path, "rb") as f:
            print("Reading:", engine_path)
            data = f.read()
        # Note that we have to provide the plugin factory when deserializing an engine built with an IPlugin or IPluginExt.
        runtime = trt.Runtime(self.TRT_LOGGER)
        self.engine = runtime.deserialize_cuda_engine(serialized_engine=data, plugin_factory=None)
        
        self.max_batch_size = self.engine.max_batch_size
        print("engine.max_batch_size={}".format(self.max_batch_size))
        for i in range(self.engine.num_bindings):
            binding_type = "input_node:" if self.engine.binding_is_input(i) else "output_node:"
            binding_name = self.engine.get_binding_name(i)
            binding_shape = self.engine.get_binding_shape(i)
            print(binding_type, binding_name, binding_shape)


        self.context = self.engine.create_execution_context()
        self._allocate_buffers()

    def _allocate_buffers(self):
        """# Allocates all buffers required for an engine, i.e. host/device inputs/outputs."""
        self.inputs = []
        self.outputs = []
        self.bindings = []
        self.stream = cuda.Stream()
        for binding in self.engine:  # binding relative with input and output
            size = trt.volume(self.engine.get_binding_shape(binding))
            dtype = trt.nptype(self.engine.get_binding_dtype(binding))
            # Allocate host and device buffers
            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)
            # Append the device buffer to device bindings.
            self.bindings.append(int(device_mem))
            # Append to the appropriate list.
            if self.engine.binding_is_input(binding):
                self.inputs.append(HostDeviceMem(host_mem, device_mem))
            else:
                self.outputs.append(HostDeviceMem(host_mem, device_mem))

    def do_inference(self, *inputs):
        """This function is generalized for multiple inputs/outputs.
        inputs and outputs are expected to be lists of HostDeviceMem objects."""

        for i, data in enumerate(inputs):
            self.inputs[i].host = np.array(data, dtype=np.float32, order='C').ravel()

        # Transfer input data to the GPU.
        [cuda.memcpy_htod_async(inp.device, inp.host, self.stream) for inp in self.inputs]
        # Run inference.
        # self.context.execute_async(batch_size=self.max_batch_size, bindings=self.bindings, stream_handle=self.stream.handle)
        self.context.execute_async_v2(bindings=self.bindings, stream_handle=self.stream.handle)
        # Transfer predictions back from the GPU.
        [cuda.memcpy_dtoh_async(out.host, out.device, self.stream) for out in self.outputs]
        # Synchronize the stream
        self.stream.synchronize()
        # Return only the host outputs.
        return [out.host for out in self.outputs]

if __name__ == '__main__':

    """ example"""

    sess = TrtSession()
    sess.load_engine("engine.trt")

    frame = cv2.imread("00001.jpg")
    frame = preprocess(frame)
    trt_outputs = sess.do_inference([frame], max_batch_size=sess.engine.max_batch_size)

    output0 = trt_outputs[0]


