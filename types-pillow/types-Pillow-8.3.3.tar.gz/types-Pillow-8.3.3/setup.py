from setuptools import setup

name = "types-Pillow"
description = "Typing stubs for Pillow"
long_description = '''
## Typing stubs for Pillow

This is a PEP 561 type stub package for the `Pillow` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `Pillow`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/Pillow. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `034a5f6aec1d544d681e7286c70db8f32ae6b876`.
'''.lstrip()

setup(name=name,
      version="8.3.3",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['PIL-stubs'],
      package_data={'PIL-stubs': ['ImageQt.pyi', 'ContainerIO.pyi', 'FtexImagePlugin.pyi', 'ExifTags.pyi', 'ImageMode.pyi', 'Hdf5StubImagePlugin.pyi', 'CurImagePlugin.pyi', 'SpiderImagePlugin.pyi', 'PyAccess.pyi', 'ImageMath.pyi', 'ImageWin.pyi', 'JpegImagePlugin.pyi', 'FitsStubImagePlugin.pyi', 'TiffImagePlugin.pyi', '__init__.pyi', 'GribStubImagePlugin.pyi', 'SunImagePlugin.pyi', 'GimpPaletteFile.pyi', 'XbmImagePlugin.pyi', 'DcxImagePlugin.pyi', 'WebPImagePlugin.pyi', 'McIdasImagePlugin.pyi', 'PngImagePlugin.pyi', 'MspImagePlugin.pyi', 'ImageFile.pyi', 'PsdImagePlugin.pyi', 'ImagePath.pyi', '_tkinter_finder.pyi', 'ImtImagePlugin.pyi', 'BdfFontFile.pyi', 'FontFile.pyi', 'GifImagePlugin.pyi', 'XVThumbImagePlugin.pyi', '_binary.pyi', 'ImageFilter.pyi', 'XpmImagePlugin.pyi', 'GbrImagePlugin.pyi', 'PalmImagePlugin.pyi', 'IcoImagePlugin.pyi', 'BlpImagePlugin.pyi', 'ImagePalette.pyi', 'ImageTransform.pyi', 'WalImageFile.pyi', 'features.pyi', 'ImageMorph.pyi', 'IptcImagePlugin.pyi', 'ImageGrab.pyi', 'ImImagePlugin.pyi', 'ImageOps.pyi', 'FliImagePlugin.pyi', 'BmpImagePlugin.pyi', 'MpoImagePlugin.pyi', 'ImageColor.pyi', 'ImageSequence.pyi', 'SgiImagePlugin.pyi', 'ImageDraw.pyi', 'Image.pyi', 'ImageDraw2.pyi', 'JpegPresets.pyi', 'TiffTags.pyi', 'ImageShow.pyi', 'ImageEnhance.pyi', 'Jpeg2KImagePlugin.pyi', 'ImageStat.pyi', 'EpsImagePlugin.pyi', 'MpegImagePlugin.pyi', 'IcnsImagePlugin.pyi', 'GdImageFile.pyi', 'PcfFontFile.pyi', 'PdfParser.pyi', 'ImageCms.pyi', 'ImageFont.pyi', 'TgaImagePlugin.pyi', '_util.pyi', 'WmfImagePlugin.pyi', '__main__.pyi', 'PixarImagePlugin.pyi', '_imaging.pyi', 'PpmImagePlugin.pyi', 'TarIO.pyi', 'ImageTk.pyi', 'PcdImagePlugin.pyi', '_version.pyi', 'ImageChops.pyi', 'GimpGradientFile.pyi', 'PaletteFile.pyi', 'FpxImagePlugin.pyi', 'PdfImagePlugin.pyi', 'BufrStubImagePlugin.pyi', 'DdsImagePlugin.pyi', 'PcxImagePlugin.pyi', 'PSDraw.pyi', 'MicImagePlugin.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
