import base64
from io import BytesIO
from PIL import Image

def image_to_base64(img, fmt='png'):
    buffered = BytesIO()
    img.save(buffered, format=fmt)
    img_str = base64.b64encode(buffered.getvalue())
    return img_str

def base64_to_image(img_str):
    img = base64.b64decode(img_str)
    img = BytesIO(img)
    img = Image.open(img)
    return img
