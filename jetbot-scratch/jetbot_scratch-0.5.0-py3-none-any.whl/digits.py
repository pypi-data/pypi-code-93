import cv2
import numpy as np
import torch
from torchvision import transforms
from torch2trt import TRTModule
import os


def imgs2tensor(imgs):
    """
    imgs: list of images, each image has shape (28,28)
    """
    mean = (0.1307, )
    std = (0.3081, )
    tensors = []

    for img in imgs:
        img = np.expand_dims(img, axis=-1)
        img = transforms.functional.to_tensor(img)
        img = transforms.functional.normalize(img, mean, std)
        tensors.append(img)
    return torch.stack(tensors)


def run_inference(model, imgs):
    """
    imgs: list of images, each image has shape (28,28)
    """
    imgs = imgs2tensor(imgs).cuda().half()
    with torch.no_grad():
        output = model(imgs)
        scores, predict_num = torch.max(output, 1)
    return scores, predict_num


def threshold_img(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 将图像转为灰度图像
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # 应用高斯模糊去噪声
    _, th = cv2.threshold(gray, 90, 255,
                          cv2.THRESH_BINARY_INV)  # 将亮度低于90的像素值设为255，其它设为0
    return th


def find_contours(th_im):
    cnts, _ = cv2.findContours(th_im, cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
    # 将面积小于133的轮廓忽略掉，该数值可酌情修改
    cnts = [cnt for cnt in cnts if cv2.contourArea(cnt) > 133]
    return cnts


def white_black_ratio(roi):
    """
    计算白色像素与黑色像素之比
    """
    hist = cv2.calcHist([roi], [0], None, [2], [0, 256])
    extent = float(hist[1]) / hist[0]
    return extent


def get_digit_rect(cnts, th_im):
    rects = [cv2.boundingRect(cnt) for cnt in cnts]
    rects = [
        rect for rect in rects
        if white_black_ratio(th_im[rect[1]:rect[1] + rect[3],
                                   rect[0]:rect[0] + rect[2]]) < 1
    ]
    return rects


def get_digit_imgs(th, rects):
    roi = [
        th[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
        for rect in rects
    ]
    resize = []
    for i in roi:
        h, w = i.shape
        # 缩放矩形区域，使其最大边长为18个像素
        scale = 18 / h if h > w else 18 / w
        i = cv2.resize(i, (0, 0), fx=scale, fy=scale)
        resize.append(i)

    # 将含有数字像素的图像复制到28x28的黑色背景中
    mnist_digits = []
    for d in resize:
        black = np.zeros((28, 28), dtype=np.uint8)
        h, w = d.shape
        black[int(14 - h / 2):int(14 + h / 2),
              int(14 - w / 2):int(14 + w / 2)] = d
        mnist_digits.append(black)
    return mnist_digits


def draw_predict_num(frame, scores, predict_num, rects):
    font = cv2.FONT_HERSHEY_SIMPLEX
    for score, num, rect in zip(scores, predict_num, rects):
        # 成绩小于0.8的当无效
        if score > 0.8:
            cv2.putText(frame, '%d: %.1f%%' % (num, score * 100),
                        (rect[0], rect[1]), font, 1, (255, 255, 0), 3,
                        cv2.LINE_AA)
            cv2.rectangle(frame, (rect[0], rect[1]),
                          (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0),
                          3)


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

cur_dir = os.path.split(os.path.realpath(__file__))[0]


class DigitDetector():
    def __init__(self) -> None:
        self.model = TRTModule()
        self.model.load_state_dict(
            torch.load(os.path.join(cur_dir, 'mnist_trt_b9.pth')))
        self.model = self.model.to(device)
        self.model.eval()
        x = torch.ones(1, 1, 28, 28).cuda().half()
        self.model(x)

    def detect(self, frame):
        th = threshold_img(frame)
        height, width = th.shape
        cnts = find_contours(th)
        rects = get_digit_rect(cnts, th)
        rects = [
            r for r in rects if r[2] > 40 and r[3] > 40 and r[2] < height /
            2 and r[3] < height / 2
        ]
        digits = get_digit_imgs(th, rects)
        if len(digits):
            # 最多送入 9 张图片，因为 mnist_trt_b9.pth 设置了最大 batchSize 为 9
            scores, predict_num = run_inference(self.model, digits[:9])
            # 将结果显示在frame中
            draw_predict_num(frame, scores, predict_num, rects)
