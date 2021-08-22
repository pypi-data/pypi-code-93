import cv2
import torch
from PIL import Image
from torchvision import transforms
from torchvision.transforms import functional as F
import numpy as np
import matplotlib.pyplot as plt

'''
PIL九种模型为1，L，P，RGB，RGBA，CMYK，YCbCr，I，F
    “1”为二值图像
    “L”为灰色图像
    “P”为8位彩色图像
    “RGBA”为32位彩色图像 红色、绿色和蓝色 透明
    “CMYK”为32位彩色图像 
        C：Cyan = 青色
        M：Magenta = 品红色
        Y：Yellow = 黄色
        K：Key Plate(blacK) = 定位套版色（黑色）
    “YCbCr”为24位彩色图像
        YCbCr其中Y是指亮度分量
        Cb指蓝色色度分量
        而Cr指红色色度分量
    “I”为32位整型灰色图像
    “F”为32位浮点灰色图像
    
'''


def f转换(file_img):
    # img_np = cv2.imread(file_img) # 这个打开是hwc bgr
    # img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

    # -------- tensor2 PIL --------- 两种方式等价
    # plt 支持.convert('RGB') 转换通道
    img_pil = Image.open(file_img)  # 这个打开的就是RGB wh 500*335
    img_tensor = F.to_tensor(img_pil)  # 转换后进行归一化 c,h,w
    transform2tensor = transforms.ToTensor()
    img_tensor = transform2tensor(img_pil)
    img_pil = F.to_pil_image(img_tensor)
    transform2pic = transforms.ToPILImage(mode="RGB")
    img_pil = transform2pic(img_tensor)

    # -------- ts np 正常转--------
    # 直接转需还原归一化 c,h,w -> h,w,c
    img_np_rgb = np.transpose(np.uint8((img_tensor * 255).numpy()), (1, 2, 0))
    img_np_bgr = cv2.cvtColor(img_np_rgb, cv2.COLOR_RGB2BGR)
    img_np_rgb = cv2.cvtColor(img_np_bgr, cv2.COLOR_BGR2RGB)
    # cv2.imshow("img", img_np_bgr)  # 显示
    # key = cv2.waitKey(0)
    # if key == 27:  # 按esc键时，关闭所有窗口
    #     print(key)
    #     cv2.destroyAllWindows()

    # ---------np plt---------
    img_np_rgb = np.array(img_pil)
    img_pil = Image.fromarray(img_np_rgb, mode="RGB")  # 不支持BGR
    img_pil = Image.fromarray(img_np_rgb.astype('uint8')).convert('RGB')
    # img_pil.show()


if __name__ == '__main__':
    '''
    t开头为测试文件
    '''
    file_img = r'D:\tb\tb\ai_code\DL\_test_pic\2007_000042.jpg'  # 500 335
    f转换(file_img)

    pass
