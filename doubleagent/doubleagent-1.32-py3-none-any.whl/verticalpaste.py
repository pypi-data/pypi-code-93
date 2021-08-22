from PIL import Image, ImageDraw, ImageFont
import numpy as np


def verticalpaste(left, right):
    lx, ly = left.size
    rx, ry = right.size
    roundback = Image.new(
        'RGB', ((lx+rx), (ly)), (255, 255, 255))
    roundback.paste(left, (0, 0))
    roundback.paste(right, (lx, 0))
    return roundback
