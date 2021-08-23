from pywkmisc import FileUtils


class ImageUtils(FileUtils):

    def __init__(self, file_path):
        """
        :param file_path:   磁盘图片文件路径
        """
        super(ImageUtils, self).__init__(file_path)
        try:
            from PIL import Image
            self._img: Image = Image.open(self._file_path)
        except ImportError:
            print('ImageHash 未安装 ，pip install ImageHash')

    @property
    def width(self):
        return self._img.width

    @property
    def height(self):
        return self._img.height

    @property
    def size(self):
        return self._img.size

    def dhash(self):
        try:
            import imagehash
            return str(imagehash.dhash(self._img))
        except ImportError:
            print('ImageHash 未安装 ，pip install ImageHash')

    def getexif(self):
        return self._img.getexif()

    def thumbnail(self, size, resample=None, reducing_gap=None):
        """同比缩放"""
        return self._img.thumbnail(size, resample, reducing_gap)

    def resize(self, size, resample=None, box=None, reducing_gap=None):
        """缩放图片"""
        return self._img.resize(size, resample, box, reducing_gap)

    @staticmethod
    def getimagedhash(filepath):
        """
        获取图片的dhash值，计算图片相识度
            dhash = ImageUtils.getimagedhash('./../qiao.jpg')\n
            print(dhash)\n
            =========\n
            4b6b694766791946
        :param filepath:        文件路径
        :return:                图片dhash数据
        """
        return ImageUtils(filepath).dhash()

    def del_file(self):
        try:
            if self._img is not None:
                self._img.close()
        except Exception as e:
            pass
        super(ImageUtils, self).del_file()

    def __del__(self):
        try:
            if self._img is not None:
                self._img.close()
        except Exception as e:
            pass


if __name__ == '__main__':
    pass
