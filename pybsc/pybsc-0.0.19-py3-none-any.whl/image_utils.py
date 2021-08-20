import base64

import cv2
import numpy as np
from turbojpeg import TurboJPEG


jpeg = TurboJPEG()


def decode_image_cv2(b64encoded):
    bin = b64encoded.split(",")[-1]
    bin = base64.b64decode(bin)
    bin = np.frombuffer(bin, np.uint8)
    img = cv2.imdecode(bin, cv2.IMREAD_COLOR)
    return img


def decode_image_turbojpeg(b64encoded):
    bin = b64encoded.split(",")[-1]
    bin = base64.b64decode(bin)
    img = jpeg.decode(bin)
    return img


def decode_image(b64encoded):
    try:
        img = decode_image_turbojpeg(b64encoded)
    except Exception:
        img = decode_image_cv2(b64encoded)
    return img


def encode_image_turbojpeg(img):
    bin = jpeg.encode(img)
    b64encoded = base64.b64encode(bin).decode('ascii')
    return b64encoded


def encode_image_cv2(img, quality=90):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, encimg = cv2.imencode('.jpg', img, encode_param)
    b64encoded = base64.b64encode(encimg).decode('ascii')
    return b64encoded


def encode_image(img):
    try:
        img = encode_image_turbojpeg(img)
    except Exception:
        img = encode_image_cv2(img)
    return img
