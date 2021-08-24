#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'text_2_img'

import os
import re
from PIL import Image, ImageDraw, ImageFont
import cjkwrap
import hashlib
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# otf_loc = '~/Library/Fonts/SourceHanSerifSC-Light.otf' # 思源宋体
# fft_loc = 'SourceHanSerifCN-Light.ttf'

# otf_loc = '~/Library/Fonts/SourceHanSansCN-Normal.otf' # 思源黑体
otf_loc = '~/Library/Fonts/SourceHanSansCN-Light.otf' # 思源黑体
fft_loc = 'SourceHanSansCN-VF.ttf'

def getFilename(text, dirname = 'tmp'):
    text = re.sub(r'[-/\s]+', '', text)
    h = hashlib.sha224(text.encode('utf-8')).hexdigest()[:3]
    return text[:10] + '_' + h

def getLineItemText(item):
    try:
        return item[1][0]
    except:
        ...
    return item.words[0].text

def splitText(text, line_char_max, line_max, font, width, style):
    text = text.strip()
    lines = []
    total_lines = 0
    for line in text.split('\n'):
        new_lines = Paragraph(line, style).breakLinesCJK(width).lines
        new_lines = [getLineItemText(item) for item in new_lines] or ['']
        lines.append(new_lines)
        total_lines += len(new_lines)
    parts = int((total_lines + line_max - 1) / line_max)
    current_lines = []
    current_count = 0
    target = (total_lines / parts) * 1.2
    for long_line in lines:
        if current_count + len(long_line) > target:
            to_yield = '\n'.join(current_lines).strip()
            if to_yield:
                yield to_yield
                current_lines = []
                target += total_lines / parts
        current_count += len(long_line)
        current_lines += long_line
    last = '\n'.join(current_lines).strip()
    if last:
        yield last

def gen(text, dirname = 'tmp', font_loc=otf_loc, fft_loc = fft_loc, color=(0, 0, 0), 
        background=(252, 250, 222), img_size=(3600, 6400), margin=200,
        font_size=160, padding=20, line_char_max=39, line_max=27):
    pdfmetrics.registerFont(TTFont('myfont', fft_loc))  #注册字体
    style = ParagraphStyle(fontName='myfont', name='myfont', fontSize=font_size)
    os.system('mkdir %s > /dev/null 2>&1' % dirname)
    fn_base = dirname + '/' + getFilename(text)
    font = ImageFont.truetype(font_loc, font_size)
    result = []
    texts = list(splitText(text, line_char_max, line_max, font, img_size[0] - margin * 2.5, style))
    for index, subText in enumerate(texts):
        lines = subText.split('\n')
        height = margin
        text_height = font.getsize(lines[0])[1]
        img_size = (img_size[0], 
            int(len(lines) * (padding + text_height) + margin * 2.5))
        img = Image.new('RGB', img_size, color=background)
        for line in lines:
            ImageDraw.Draw(img).text((margin, height), line, font=font, fill=color)
            height += text_height + padding
        fn = '%s_%d.png' % (fn_base, index)
        img.save(fn)
        result.append(fn)
    return result

