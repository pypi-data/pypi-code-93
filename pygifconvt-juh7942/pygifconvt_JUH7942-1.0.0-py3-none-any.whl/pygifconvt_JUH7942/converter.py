import glob
from PIL import Image

class GIFConverter():
    def __init__(self, path_in=None, path_out=None, resize=(320, 240)):
        """
        path_in : Source Multiple Image Paths
        path_out : Result Image Path
        resize : Resizing Size
        """
        self.path_in = path_in or './*.png'
        self.path_out = path_out or './output.gif'
        self.resize = resize

    def convert_gif(self):
        """
        Perform GIF Image Conversion
        """
        print(self.path_in, self.path_out, self.resize)

        img, *images = \
        [Image.open(f).resize((self.resize), Image.ANTIALIAS) for f in sorted(glob.glob(self.path_in))]

        try:
            img.save(
                fp=self.path_out,
                format='GIF',
                append_images=images,
                save_all=True,
                duration=500,
                loop=False
            )
        except IOError:
            print('Cannot convert!', img)

if __name__ == '__main__':
    # 클래스
    c = GIFConverter('./project/images/*.png', './project/image_out/result.gif', (320, 240))

    # 변환
    c.convert_gif()
