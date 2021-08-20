# -*- coding: utf-8 -*-
# @Author        : Antonio-hi
# @Email         : 9428.al@gmail.com
# @Create Date   : 2021-08-09 19:08:49
# @Last Modified : 2021-08-10 10:11:06
# @Description   : 

# import the necessary packages
import numpy as np
import base64
import json
import sys
import cv2
import os

def base64_encode_image(a):
    # return a JSON-encoded list of the base64 encoded image, image data type, and image shape
    # return json.dumps([base64_encode_array(a), str(a.dtype), a.shape])
    return json.dumps([base64_encode_array(a).decode("utf-8"), str(a.dtype),
        a.shape])

def base64_decode_image(a):
    # grab the array, data type, and shape from the JSON-decoded object
    (a, dtype, shape) = json.loads(a)

    # set the correct data type and reshape the matrix into an image
    a = base64_decode_array(a, dtype).reshape(shape)

    # return the loaded image
    return a

def base64_encode_array(a):
    # return the base64 encoded array
    return base64.b64encode(a)

def base64_decode_array(a, dtype):
    # decode and return the array
    return np.frombuffer(base64.b64decode(a), dtype=dtype)

def base64_encode_file(image_path):
    filename = os.path.basename(image_path)
    # encode image file to base64 string
    with open(image_path, 'rb') as f:
        buffer = f.read()
        # convert bytes buffer string then encode to base64 string
        img64_bytes = base64.b64encode(buffer)
        img64_str = img64_bytes.decode('utf-8')          # bytes to str
    return json.dumps({"filename" : filename, "img64": img64_str})

def base64_to_image(img64):
    image_buffer = base64_decode_array(img64, dtype=np.uint8)
    # In the case of color images, the decoded images will have the channels stored in B G R order.
    image = cv2.imdecode(image_buffer, cv2.IMREAD_COLOR)
    return image


if __name__ == '__main__':

    image_path = '/home/lk/Repository/Project/turnsole/demos/images/sunflower.jpg'

    # 1）将图片文件转换成 base64 base64编码的字符串(理论上支持任意文件)
    json_str = base64_encode_file(image_path)

    img64_dict = json.loads(json_str)

    suffix = os.path.splitext(img64_dict['filename'])[-1].lower()
    if suffix not in ['.jpg', '.jpeg', '.png', '.bmp']:
        print(f'[INFO] 暂不支持格式为 {suffix} 的文件!')

    # 2）将 base64 编码的字符串转成图片
    image = base64_to_image(img64_dict['img64'])

    inputs = image/255.

    # 3）自创的, 将 array 转 base64 编码再转回array, 中间不经历图片操作, 还能保持 array 的数据类型
    base64_encode_json_string = base64_encode_image(inputs)
    
    inputs = base64_decode_image(base64_encode_json_string)

    print(inputs)

    # 3、字符串前加 b
    # 例: response = b'<h1>Hello World!</h1>'     # b' ' 表示这是一个 bytes 对象

    # 作用：

    # b" "前缀表示：后面字符串是bytes 类型。

    # 用处：

    # 网络编程中，服务器和浏览器只认bytes 类型数据。

    # 如：send 函数的参数和 recv 函数的返回值都是 bytes 类型

    # 附：

    # 在 Python3 中，bytes 和 str 的互相转换方式是
    # str.encode('utf-8')
    # bytes.decode('utf-8')
