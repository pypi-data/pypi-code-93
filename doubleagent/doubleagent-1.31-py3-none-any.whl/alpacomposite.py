from PIL import Image, ImageDraw, ImageFont
import numpy as np


def alpacomposite(bigone, smallone, locate):

    tagetx, targety = locate

    onex, oney = bigone.size
    background = Image.new('RGBA', (onex, oney), (255, 255, 255, 0))

    background.paste(smallone, (tagetx, targety))
    final = Image.alpha_composite(bigone, background)
    return final
