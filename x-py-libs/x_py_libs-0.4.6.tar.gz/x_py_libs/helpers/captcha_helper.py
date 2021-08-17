# -*- coding=utf-8 -*-

# https://cloud.tencent.com/developer/article/1067121

from captcha.image import ImageCaptcha, random_color
from random import randint
import gvcode
import base64
from io import BytesIO


CHAR_LIST = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        #'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 
        #'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        #'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 
        #'J', 'K', 'L', 'M', 'N', 'O', 
        #'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
        ]

class CaptchaHelper(object):

    @staticmethod
    def generate(length=4, width=160, height=60, fonts=None, font_sizes=None, char_list=CHAR_LIST, create_noise_dots=True, create_noise_curve=True):
        
        chars = ''.join([(char_list[randint(0, len(char_list) - 1)])for i in range(length)])
        
        # image = ImageCaptcha(width=width, height=height, fonts=fonts, font_sizes=font_sizes).generate_image(chars)

        # generate_image的实现方法，可以通过重写此方法来实现自定义验证码样式。
        # create_captcha_image(chars, color, background) 
 
        # 生成验证码干扰点。
        # create_noise_dots(image, color, width=3, number=30) 
        
        # 生成验证码干扰曲线。
        # create_noise_curve(image, color) 

        background = random_color(238, 255)
        color = random_color(10, 200, randint(220, 255))

        ic = ImageCaptcha(width=width, height=height, fonts=fonts, font_sizes=font_sizes)
        image = ic.create_captcha_image(chars, color, background) 

        if create_noise_dots:
            ic.create_noise_dots(image, color, width=3, number=30) 
        if create_noise_dots:
            ic.create_noise_curve(image, color) 

        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        # print(chars ,type(image),img_str)
        return chars, img_str
        # image.show()

# CaptchaHelper.generate()

# s, v = gvcode.generate() #序列解包
# s.show() #显示生成的验证码图片
# print(v) #打印验证码字符串
 
# image.show()
 
        # self.write(simplejson.dumps({'code': 0, 'img': stream.getvalue().encode('base64')}))
    #这里是将stream的值进行了一次base64的编码