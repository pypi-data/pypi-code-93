# -*- coding:utf-8 -* 
#
# 验证码
#

import os
from io import BytesIO

from django.http import HttpResponse

from framework.route import Route
from framework.views import notauth


@Route('^get_verify_code_image/')
@notauth
def get_verify_code_image(request):
    """验证码
    @background #随机背景颜色
    @line_color #随机干扰线颜色
    @img_width = #画布宽度
    @img_height = #画布高度
    @font_color = #验证码字体颜色
    @font_size = #验证码字体尺寸
    @font = I#验证码字体
    """

    from PIL import Image, ImageDraw, ImageFont
    import random
    path = os.path.dirname(__file__)
    background = (random.randrange(230, 255), random.randrange(230, 255), random.randrange(230, 255))
    line_color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
    img_width = 80
    img_height = 30
    font_color = ['black', 'darkblue', 'darkred']
    font_size = 20
    font = ImageFont.truetype(os.path.join(path, 'BRITANIC.TTF'), font_size)
    # request.session['verify'] = ''
    im = Image.new('RGB', (img_width, img_height), background)
    draw = ImageDraw.Draw(im)
    A_Z = ''.join(map(chr, list(range(65, 91)) + list(range(97, 123))))
    # string = A_Z + '#@^%&*!'
    string = '1234567890'
    code = random.sample(string, 5)
    # code = md5str[:4]
    # 新建画笔
    draw = ImageDraw.Draw(im)

    for i in range(random.randrange(3, 5)):
        xy = (random.randrange(0, img_width), random.randrange(0, img_height),
              random.randrange(0, img_width), random.randrange(0, img_height))
        draw.line(xy, fill=line_color, width=1)

    x = 2
    for i in code:
        y = random.randrange(0, 10)
        draw.text((x, y), i, font=font, fill=random.choice(font_color))
        x += 14
    request.session['verify'] = ''.join(code)
    del x
    del draw
    buf = BytesIO()
    im.save(buf, 'gif')
    buf.seek(0)
    return HttpResponse(buf.getvalue(), 'image/gif')
