import cv2
import glob
import os
import time

class Image2Video:
    def __init__(self, width, height, fps):
        self.width = width
        self.height = height
        self.fps = fps
        self.writer = cv2.VideoWriter()
        fourcc = cv2.VideoWriter.fourcc(*"H264")
        filename = "{}.avi".format(int(time.time()))
        self.writer.open(filename, fourcc, fps, (width, height))
        if not self.writer.isOpened():
            print("H264 does not support, switch to MJPG")
            fourcc = cv2.VideoWriter.fourcc(*"MJPG")
            self.writer.open(filename, fourcc, fps, (width, height))

    def record(self, img_dir):
        imgpaths = []
        for fmt in ["*.jpg", "*.png"]:
            paths = glob.glob(os.path.join(img_dir, fmt))
            imgpaths.extend(paths)

        i = 0
        while self.writer.isOpened():
            img_p = imgpaths[i]
            img = cv2.imread(img_p)
            img = cv2.resize(img, (self.width, self.height))
            self.writer.write(img)
            time.sleep(1 / self.fps)  # sleep by fps
            cv2.imshow("img", img)
            key = cv2.waitKey(1)
            if key == ord('q'):
                cv2.destroyAllWindows()
                self.writer.release()
                break
            i = (i + 1) % len(imgpaths)

    def record_img(self, img):
        self.writer.write(img)

if __name__ == '__main__':
    img2video = Image2Video(1280, 720, 0.5)
    img2video.record("/home/liam/deepblue/projects/edge_sweeper/YOLOV5_WTS_TRT通路/yolov5_tensorrt-master/yolov5_trainAndToTRT/yolov5_ToTRT_int8Fp16Fp32/images")
