'''
Author: ZHANG XIANRUI
Date: 2021-06-30 16:57:16
LastEditTime: 2021-08-17 12:24:53
LastEditors: ZHANG XIANRUI
Description: 
'''

from PIL import Image
import openslide
import math
import numpy as np
from openslide import ImageSlide, OpenSlide
from pathlib import Path


def open_slide(filename, image=False):
    """Open a whole-slide image filenmae, PIL filename/object.

    Return an OpenSlide or ImageSlide object."""
    if isinstance(filename, Path):
        filename = str(filename)
    if image:
        try:
            slide = ImageSlide(filename)
        except:
            slide = None
    else:
        try:
            slide = OpenSlide(filename)
        except:
            slide = None
    return slide


class ShallowZoomGenerator(object):
    """Generates Deep Zoom tiles and metadata
    Support for Deep Zoom images.This module provides functionality for 
    generating Deep Zoom images from OpenSlide objects.
    1. 根据参数limit bounds选定active region,一般设置为TRUE。
    2. 根据tilesize把选定的level下就行切分，tilezsize=128,切分时候最后一列，最后一行可能凑不够128，这是就边缘补0，凑够整数个tile。
    3. overlap可以理解为padding. e.g. padding = 64,以切分好的128*128的tile为中心，宽和高都向边缘扩展64个像素，扩展一圈，所以读取出的图像size=tile size + overlap *2.
    """

    BOUNDS_OFFSET_PROPS = (openslide.PROPERTY_NAME_BOUNDS_X,
                           openslide.PROPERTY_NAME_BOUNDS_Y)
    BOUNDS_SIZE_PROPS = (openslide.PROPERTY_NAME_BOUNDS_WIDTH,
                         openslide.PROPERTY_NAME_BOUNDS_HEIGHT)

    def __init__(self, osr, tile_size=256, overlap=128, limit_bounds=True):
        """Create a ShallowZoomGenerator.

        osr:          a slide object.
        tile_size:    the width and height of a single tile.
        overlap:      it is not overlap, it is stride of slide window.
        limit_bounds: True to render only the non-empty slide region.
        """

        self._osr = osr
        self._z_t_downsample = tile_size
        self._z_overlap = overlap
        self._limit_bounds = limit_bounds

        # Precompute dimensions
        # Slide level and offset
        if limit_bounds:
            # Level 0 coordinate offset  圆点 左上角
            self._l0_offset = tuple(
                int(osr.properties.get(prop, 0))
                for prop in self.BOUNDS_OFFSET_PROPS)
            # Slide level dimensions scale factor in each axis 激活区域比例
            size_scale = tuple(
                int(osr.properties.get(prop, l0_lim)) / l0_lim for prop, l0_lim
                in zip(self.BOUNDS_SIZE_PROPS, osr.dimensions))
            # Dimensions of active area  每个尺度下的激活区域维度
            self._l_dimensions = tuple(
                tuple(
                    int(math.ceil(l_lim * scale))
                    for l_lim, scale in zip(l_size, size_scale))
                for l_size in osr.level_dimensions)
        else:
            self._l_dimensions = osr.level_dimensions  # 每个尺度下的激活区域维度 全部都是激活区域
            self._l0_offset = (0, 0)  # 圆点 左上角
        self._l0_dimensions = self._l_dimensions[0]
        # Deep Zoom level
        z_size = self._l0_dimensions
        z_dimensions = [z_size]

        # 从最大维度开始除以2，直到小于2
        while z_size[0] > 1 or z_size[1] > 1:
            z_size = tuple(max(1, int(math.ceil(z / 2))) for z in z_size)
            z_dimensions.append(z_size)

        # 每个尺度的维度 从小往大排列
        self._z_dimensions = tuple(reversed(z_dimensions))

        # self._t_dimensions 排列成tile后的每个尺度的维度 原尺度缩小tile_size倍
        def tiles(z_lim):
            return int(math.ceil(z_lim / self._z_t_downsample))

        self._t_dimensions = tuple(
            (tiles(z_w), tiles(z_h)) for z_w, z_h in self._z_dimensions)

        # Deep Zoom level count 尺度的个数
        self._dz_levels = len(self._z_dimensions)

        # Total downsamples for each Deep Zoom level 采样率 ...32 16 8 4 2 1
        l0_z_downsamples = tuple(2**(self._dz_levels - dz_level - 1)
                                 for dz_level in range(self._dz_levels))

        # Preferred openslide levels for each Deep Zoom level
        # 每个采样率对应的level  对给定的下采样因子l0_z_downsamples 返回level
        self._slide_from_dz_level = tuple(
            self._osr.get_best_level_for_downsample(d)
            for d in l0_z_downsamples)

        # Piecewise downsamples
        self._l0_l_downsamples = self._osr.level_downsamples

        # 在dz的level下,计算opensldie的最佳level,在最佳level下读取后，
        # 是否还需要再次采样缩小，不需的话该值就是1
        # 因为openslide的level可能是 2 8 32 64  不一定是按照2的n次方
        self._l_z_downsamples = tuple(
            l0_z_downsamples[dz_level] /
            self._l0_l_downsamples[self._slide_from_dz_level[dz_level]]
            for dz_level in range(self._dz_levels))

        # Slide background color
        self._bg_color = '#' + self._osr.properties.get(
            openslide.PROPERTY_NAME_BACKGROUND_COLOR, 'ffffff')

    def __repr__(self):
        return '%s(%r, tile_size=%r, overlap=%r, limit_bounds=%r)' % (
            self.__class__.__name__, self._osr, self._z_t_downsample,
            self._z_overlap, self._limit_bounds)

    @property
    def level_count(self):
        """The number of Deep Zoom levels in the image."""
        return self._dz_levels

    @property
    def level_tiles(self):
        """A list of (tiles_x, tiles_y) tuples for each Deep Zoom level."""
        return self._t_dimensions

    @property
    def level_dimensions(self):
        """A list of (pixels_x, pixels_y) tuples for each Deep Zoom level."""
        return self._z_dimensions

    @property
    def tile_count(self):
        """The total number of Deep Zoom tiles in the image."""
        return sum(t_cols * t_rows for t_cols, t_rows in self._t_dimensions)

    def get_tile(self, level, address):
        """Return an RGB PIL.Image for a tile.

        level:     the Deep Zoom level.
        address:   the address of the tile within the level as a (col, row)
                   tuple."""

        # Read tile
        args, z_size = self._get_tile_info(level, address)
        tile = self._osr.read_region(*args)

        # Apply on solid background
        bg = Image.new('RGB', tile.size, self._bg_color)
        tile = Image.composite(tile, bg, tile)

        # Scale to the correct size
        if tile.size != z_size:
            tile.thumbnail(z_size, Image.ANTIALIAS)

        return tile

    def _get_tile_info(self, dz_level, t_location):
        # Check parameters
        if dz_level < 0 or dz_level >= self._dz_levels:
            raise ValueError("Invalid level")
        for t, t_lim in zip(t_location, self._t_dimensions[dz_level]):
            if t < 0 or t >= t_lim:
                raise ValueError("Invalid address")

        # Get preferred slide level
        slide_level = self._slide_from_dz_level[dz_level]

        z_size = tuple([self._z_t_downsample + self._z_overlap * 2]) * 2

        # Obtain the region coordinates
        z_location = [self._z_from_t(t) for t in t_location]
        l_location = [
            self._l_from_z(dz_level, z - self._z_overlap) for z in z_location
        ]
        # Round location down and size up, and add offset of active area
        l0_location = tuple(
            int(self._l0_from_l(slide_level, l) + l0_off)
            for l, l0_off in zip(l_location, self._l0_offset))
        l_size = tuple(
            math.ceil(self._l_from_z(dz_level, dz)) for dz in z_size)

        # Return read_region() parameters plus tile size for final scaling
        return ((l0_location, slide_level, l_size), z_size)

    def _l0_from_l(self, slide_level, l):
        return self._l0_l_downsamples[slide_level] * l

    def _l_from_z(self, dz_level, z):
        return self._l_z_downsamples[dz_level] * z

    def _z_from_t(self, t):
        return self._z_t_downsample * t

    def get_tile_coordinates(self, level, address):
        """Return the OpenSlide.read_region() arguments for the specified tile.

        Most users should call get_tile() rather than calling
        OpenSlide.read_region() directly.

        level:     the Deep Zoom level.
        address:   the address of the tile within the level as a (col, row)
                   tuple."""
        return self._get_tile_info(level, address)[0]

    def get_tile_dimensions(self, level, address):
        """Return a (pixels_x, pixels_y) tuple for the specified tile.

        level:     the Deep Zoom level.
        address:   the address of the tile within the level as a (col, row)
                   tuple."""
        return self._get_tile_info(level, address)[1]


class MaskZoomGenerator():
    def __init__(self, sz, tile_size, overlap, mask_img):
        self.sz = sz
        self.tile_size = tile_size
        self.overlap = overlap
        self.mask_img = mask_img

    def get_tile(self, level, address):
        target_slide_dim = tuple(i * self.tile_size
                                 for i in self.sz.level_tiles[level])
        origin_slide_dim = self.sz.level_dimensions[level]
        scale = math.gcd(self.tile_size, self.overlap)
        while scale > 8:
            scale = scale / 2  # 防止缩放得太小
        mask_tile_size = int(self.tile_size / scale)
        mask_overlap_size = int(self.overlap / scale)
        origin_mask_size = tuple(
            math.ceil(i / scale) for i in origin_slide_dim)
        target_mask_size = tuple(
            math.ceil(i / scale) for i in target_slide_dim)

        mask_img = self.mask_img.resize(origin_mask_size, Image.NEAREST)
        mask_array = np.asarray(mask_img).astype('uint8')

        w, h = target_mask_size
        target_mask = np.zeros((h, w)).astype('uint8')
        w, h = origin_mask_size
        target_mask[:h, :w] = mask_array
        target_mask_padded = np.pad(target_mask, (mask_overlap_size, ),
                                    constant_values=0)

        w, h = address
        x_top = h * mask_tile_size
        x_bottom = x_top + mask_tile_size + 2 * mask_overlap_size

        y_left = w * mask_tile_size
        y_right = y_left + mask_tile_size + 2 * mask_overlap_size
        roi = target_mask_padded[x_top:x_bottom, y_left:y_right]
        return Image.fromarray(roi)
