'''
独立的颜色处理 与target 无关
'''
import numpy as np
import cv2
import random


def random_brightness(img, delta):
    img += random.uniform(-delta, delta)
    return img


def random_contrast(img, alpha_low, alpha_up):
    img *= random.uniform(alpha_low, alpha_up)
    return img


def random_saturation(img, alpha_low, alpha_up):
    hsv_img = cv2.cvtColor(img.astype(np.float32) / 255, cv2.COLOR_BGR2HSV)
    hsv_img[..., 1] *= random.uniform(alpha_low, alpha_up)
    img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR) * 255
    # cv2.imshow('img', img/255)
    return img


def normalize(meta, mean, std):
    img = meta['img'].astype(np.float32)
    mean = np.array(mean, dtype=np.float64).reshape(1, -1)
    stdinv = 1 / np.array(std, dtype=np.float64).reshape(1, -1)
    cv2.subtract(img, mean, img)
    cv2.multiply(img, stdinv, img)
    meta['img'] = img
    return meta


def _normalize(img, mean, std):
    mean = np.array(mean, dtype=np.float32).reshape(1, 1, 3) / 255
    std = np.array(std, dtype=np.float32).reshape(1, 1, 3) / 255
    img = (img - mean) / std
    return img


def color_aug_and_norm(meta):
    img = meta['img'].astype(np.float32) / 255

    if random.randint(0, 1):
        # 0.2 亮度
        img = random_brightness(img, 0.2)

    if random.randint(0, 1):
        # [0.8, 1.2] 对比度
        img = random_contrast(img, 0.8, 1.2)

    if random.randint(0, 1):
        # [0.8, 1.2] 饱和度
        img = random_saturation(img, 0.8, 1.2)
    # cv2.imshow('trans', img)
    # cv2.waitKey(0)
    img = _normalize(img, [103.53, 116.28, 123.675], [57.375, 57.12, 58.395])
    return img
