import cv2
import jetson.inference
import numpy as np


class ObjectDetector():
    def __init__(self) -> None:
        self.net = jetson.inference.detectNet('ssd-mobilenet-v2')
        x = np.ones((224, 224, 3))
        cuda_mem = jetson.utils.cudaFromNumpy(x)
        self.net.Detect(cuda_mem)
        del cuda_mem

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cuda_mem = jetson.utils.cudaFromNumpy(rgb)
        detections = self.net.Detect(cuda_mem)
        res = jetson.utils.cudaAllocMapped(width=cuda_mem.width,
                                           height=cuda_mem.height,
                                           format='bgr8')
        jetson.utils.cudaConvertColor(cuda_mem, res)
        jetson.utils.cudaDeviceSynchronize()
        frame[:] = jetson.utils.cudaToNumpy(res)[:]
        return detections
