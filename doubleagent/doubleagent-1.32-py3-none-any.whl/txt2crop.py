from PIL import Image, ImageDraw, ImageFont
import numpy as np


def txt2crop(string, font, color):

    ascent, descent = font.getmetrics()

    ox = font.getmask(string).getbbox()[2]
    oy = font.getmask(string).getbbox()[3] + descent
    im = Image.new('RGBA', (ox, oy), (255, 255, 255, 0))
    xt, yt = im.size
    draw = ImageDraw.Draw(im)
    draw.text((0, 0),
              string, color, font=font)
    nomal = np.array(im)

    nomal90 = im.transpose(Image.ROTATE_270)

    nomal90 = np.array(nomal90)
    nomal180 = im.transpose(Image.ROTATE_180)

    nomal180 = np.array(nomal180)
    nomal270 = im.transpose(Image.ROTATE_90)
    nomal270 = np.array(nomal270)
    count = 0
    #  momal numpy vertical
    nomal = nomal.tolist()
    for y, li1 in enumerate(nomal):

        if count == 1:
            break
        for x, li2 in enumerate(li1):
            if count == 1:
                break

            if not li2 == [255, 255, 255, 255]:
                y1 = y

                count = 1

    count = 0
    nomal90 = nomal90.tolist()
    for y, li1 in enumerate(nomal90):

        if count == 1:
            break
        for x, li2 in enumerate(li1):
            if count == 1:
                break

            if not li2 == [255, 255, 255, 255]:
                x1 = y
                count = 1

    count = 0
    nomal180 = nomal180.tolist()
    for y, li1 in enumerate(nomal180):

        if count == 1:
            break
        for x, li2 in enumerate(li1):
            if count == 1:
                break

            if not li2 == [255, 255, 255, 255]:
                y2 = oy-y
                count = 1

    count = 0
    nomal270 = nomal270.tolist()
    for y, li1 in enumerate(nomal270):

        if count == 1:
            break
        for x, li2 in enumerate(li1):
            if count == 1:
                break

            if not li2 == [255, 255, 255, 255]:
                x2 = ox-y
                count = 1

    im = im.crop((x1, y1, x2, y2))
    return im
