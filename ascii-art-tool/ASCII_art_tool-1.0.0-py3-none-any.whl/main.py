from os import path
import PIL.Image

PIXEL_CHARS = ["@", "#", "$", "%", "?", "*", "+", ";", ":", ",", "."]

def get_grey(picture):
    return picture.convert("L")

def resize(picture, next_width: int = 100):
    width, height = picture.size
    new_height = int(next_width * height / width)
    return picture.resize((next_width, new_height))

def pixel_to_ascii(image: PIL.Image.Image) -> str:
    pixels = image.getdata()
    ascii_str = ""
    for pixel in pixels:
        ascii_str += PIXEL_CHARS[pixel//25]
    return ascii_str
    
class Generator:
    def __init__(self, input: str, output: str) -> None:
        self.input = input
        self.output = output

    def check_file(self) -> None:
        if path.exists(self.input):
            pass
        else:
            raise FileNotFoundError("The specified input file doesn't exist")

    def execute(self) -> None:
        self.check_file()
        try:
            image = PIL.Image.open(self.input)
        except:
            print(self.input, "Image not found ")
        image = resize(image)
        greyscale_image = get_grey(image)
        ascii_str = pixel_to_ascii(greyscale_image)
        img_width = greyscale_image.width
        ascii_str_len = len(ascii_str)
        ascii_img=""
        for i in range(0, ascii_str_len, img_width):
            ascii_img += ascii_str[i:i+img_width] + "\n"
        with open(self.output, "w") as f:
            f.write(ascii_img)
