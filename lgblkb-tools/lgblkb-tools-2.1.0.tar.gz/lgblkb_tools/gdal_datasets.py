from pathlib import Path
import logging
import os
import string
import uuid
from typing import Iterable, Union

import geojson
import matplotlib.pyplot as plt
import numpy as np
import shapely.geometry as shg
import shapely.wkt as shwkt
from box import Box
from osgeo import gdal, gdal_array, ogr, osr, gdalconst

from . import logger
from . import pathify
from .common.utils import run_cmd
from .pathify import get_name

gdal.UseExceptions()


def ds_to_array(ds, band_index=1):
    if isinstance(ds, str): ds = gdal.Open(ds)
    return ds.GetRasterBand(band_index).ReadAsArray(0, 0, ds.RasterXSize, ds.RasterYSize)


geom_from_ds = lambda ds: np.abs(np.array(ds.GetGeoTransform()).reshape(2, -1))
resol_from_ds = lambda ds: geom_from_ds(ds)[:, 1:].sum(axis=0)
ul_from_ds = lambda ds: geom_from_ds(ds)[:, 0]


# get_epsg_from = lambda ds: int(
#     gdal.Info(ds, format='json')['coordinateSystem']['wkt'].rsplit('"EPSG","', 1)[-1].split('"')[0])


def plot_ds(ds, show=False):
    array = ds_to_array(ds)
    plt.imshow(array)
    if show: plt.show()


code_lut = {v: k for k, v in gdal_array.codes.items()}


def array_to_ds(array, parent_info):
    try:
        arr_ds = gdal_array.OpenNumPyArray(array, True)
    except:
        arr_ds = gdal_array.OpenNumPyArray(array)
    if isinstance(parent_info, DataSet): parent_info = parent_info.ds
    if isinstance(parent_info, gdal.Dataset):
        transform = parent_info.GetGeoTransform()
        projection = parent_info.GetProjection()
    else:
        transform, projection = parent_info
    arr_ds.SetGeoTransform(transform)
    arr_ds.SetProjection(projection)
    return arr_ds


def get_datasource(driver_name, fpath, field_name, field_type):
    dest_datasource = ogr.GetDriverByName(driver_name).CreateDataSource(fpath)
    dest_layer = dest_datasource.CreateLayer('', srs=None)
    dest_layer.CreateField(ogr.FieldDefn(field_name, field_type))
    return dest_datasource, dest_layer


@logger.trace()
def polygonize(ds, driver_name, fpath, field_name='DN', field_type=ogr.OFTInteger):
    dest_datasource, dest_layer = get_datasource(driver_name, fpath, field_name, field_type)
    if field_type is ogr.OFTReal:
        polygonizer = gdal.FPolygonize
    else:
        polygonizer = gdal.Polygonize
    polygonizer(ds.GetRasterBand(1), None, dest_layer, 0, ['8connected=8'], callback=None)
    return dest_datasource, dest_layer


def contour_generate(ds, val_ranges, driver_name, fpath, field_name, field_type):
    contour_dsrc, contour_layer = get_datasource(driver_name, fpath, field_name, field_type)
    gdal.ContourGenerate(ds.GetRasterBand(1), 0, 0, val_ranges, 0, 0, contour_layer, 0, 0)
    return contour_dsrc, contour_layer


class DataSet:

    def __init__(self, ds, array=None, name=''):
        self.path = None
        if isinstance(ds, str):
            name = name or '_'.join(pathify.get_splitted(os.path.splitext(ds)[0])[-2:])
            self.path = ds
            ds = gdal.Open(ds)
        self.ds = ds
        geom = geom_from_ds(self.ds)
        self.resol = geom[:, 1:].sum(axis=0)
        self.ul = geom[:, 0]
        self.__array = array
        self.projection = self.ds.GetProjection()
        self.transform = self.ds.GetGeoTransform()
        self.name = name

    # @logger.trace(skimpy=True)
    def get_array(self, band_index=1):
        return ds_to_array(self.ds, band_index=band_index)

    @property
    def array(self):
        if self.__array is None:
            self.__array = self.get_array()
        return self.__array

    @property
    def epsg(self):
        return osr.SpatialReference(wkt=self.projection).GetAttrValue('AUTHORITY', 1)

    def plot(self, show=False):
        plot_ds(self.ds, show=show)
        return self

    @logger.trace()
    def reproject(self, to_epsg):
        """
        A sample function to reproject and resample a GDAL dataset from within
        Python. The idea here is to reproject from one system to another, as well
        as to change the pixel size. The procedure is slightly long-winded, but
        goes like this:

        1. Set up the two Spatial Reference systems.
        2. Open the original dataset, and get the geotransform
        3. Calculate bounds of new geotransform by projecting the UL corners
        4. Calculate the number of pixels with the new projection & spacing
        5. Create an in-memory raster dataset
        6. Perform the projection
        """
        # Define the UK OSNG, see <http://spatialreference.org/ref/epsg/27700/>
        osng = osr.SpatialReference()
        osng.ImportFromEPSG(to_epsg)
        wgs84 = osr.SpatialReference()
        wgs84.ImportFromEPSG(self.epsg)
        tx = osr.CoordinateTransformation(wgs84, osng)
        # Up to here, all  the projection have been defined, as well as a
        # transformation from the from to the  to :)
        # We now open the dataset
        # Get the Geotransform vector
        geo_t = self.ds.GetGeoTransform()
        x_size, y_size = self.raster_sizes
        # Work out the boundaries of the new dataset in the target projection
        (ulx, uly, ulz) = tx.TransformPoint(geo_t[0], geo_t[3])
        (lrx, lry, lrz) = tx.TransformPoint(geo_t[0] + geo_t[1] * x_size, geo_t[3] + geo_t[5] * y_size)
        # See how using 27700 and WGS84 introduces a z-value!
        # Now, we create an in-memory raster
        mem_drv = gdal.GetDriverByName('MEM')
        # The size of the raster is given the new projection and pixel spacing
        # Using the values we calculated above. Also, setting it to store one band
        # and to use Float32 data type.
        # dest=mem_drv.Create('',int((lrx-ulx)/x_size),int((uly-lry)/y_size),1,gdal.GDT_Float32)
        dtype = np.typeDict[str(self.array.dtype)]
        dest = mem_drv.Create('', x_size, y_size, 1, code_lut[dtype])
        # dest=mem_drv.Create('',pixel_x_size,pixel_y_size,1,gdal.GDT_Float32)
        # Calculate the new geotransform
        resol = self.resol
        new_geo = (ulx, resol[0], geo_t[2], uly, geo_t[4], -resol[1])
        # Perform the projection/resampling
        # Set the geotransform
        dest.SetGeoTransform(new_geo)
        dest.SetProjection(osng.ExportToWkt())
        gdal.ReprojectImage(self.ds, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Bilinear)
        # gdal.ReprojectImage(self.ds,dest,wgs84.ExportToWkt(),osng.ExportToWkt())
        return DataSet(dest)

    # @logger.trace(skimpy=True)
    def do_warp(self, cutline_feature=None, destroy_after=True, out_epsg=None, out_path='', return_as_ds=True,
                lazy=False, ignore_error=False, **kwargs):
        """options=None, format=None,
         outputBounds=None,
         outputBoundsSRS=None,
         xRes=None, yRes=None, targetAlignedPixels = False,
         width = 0, height = 0,
         srcSRS=None, dstSRS=None,
         srcAlpha = False, dstAlpha = False,
         warpOptions=None, errorThreshold=None,
         warpMemoryLimit=None, creationOptions=None, outputType = gdalconst.GDT_Unknown,
         workingType = gdalconst.GDT_Unknown, resampleAlg=None,
         srcNodata=None, dstNodata=None, multithread = False,
         tps = False, rpc = False, geoloc = False, polynomialOrder=None,
         transformerOptions=None, cutlineDSName=None,
         cutlineLayer=None, cutlineWhere=None, cutlineSQL=None, cutlineBlend=None, cropToCutline = False,
         copyMetadata = True, metadataConflictValue=None,
         setColorInterpretation = False,
         callback=None, callback_data=None"""
        if lazy and out_path and (not return_as_ds) and os.path.exists(out_path): return out_path
        out_path = out_path or f"/vsimem/{uuid.uuid4()}"
        if not cutline_feature is None:
            if isinstance(cutline_feature, str):
                cutline_feature = geojson.Feature(geometry=shwkt.loads(cutline_feature))
            elif isinstance(cutline_feature, (shg.MultiPolygon, shg.Polygon)):
                cutline_feature = geojson.Feature(geometry=cutline_feature)
            elif isinstance(cutline_feature, DataSet):
                cutline_feature = geojson.Feature(geometry=cutline_feature.geom)
        try:
            gdal.Warp(out_path, self.ds, srcSRS=f'EPSG:{self.epsg}', dstSRS=f'EPSG:{out_epsg or self.epsg}',
                      cutlineDSName=cutline_feature, **dict(dict(cropToCutline=not cutline_feature is None), **kwargs))
        except RuntimeError as exc:
            if return_as_ds or not ignore_error: raise exc
            logger.warning(str(exc))
            return
        if return_as_ds:
            out = DataSet(out_path)
        else:
            out = out_path
        if destroy_after: self.ds = None
        return out

    @property
    def geo_info(self):
        return self.transform, self.projection

    @property
    def raster_count(self):
        return self.ds.RasterCount

    @property
    def raster_sizes(self):
        return self.ds.RasterXSize, self.ds.RasterYSize

    @property
    def file_meta(self):
        return Box(self.ds.GetMetadata())

    def get_band_metas(self):
        band_metas = list()
        for i in range(self.raster_count):
            band_metas.append(Box(self.ds.GetRasterBand(i + 1).GetMetadata()))
        return band_metas

    @classmethod
    def from_array(cls, array, geo_info):
        if isinstance(geo_info, str): geo_info = DataSet(geo_info)
        return DataSet(array_to_ds(array, geo_info), array)

    @logger.trace()
    def polygonize(self, driver_name, fpath, destroy_after=True, **kwargs):
        datasource, ds_layer = polygonize(self.ds, driver_name, fpath, **kwargs)
        if not 'mem' in driver_name.lower():
            ds_layer = None
            datasource = None
        if destroy_after: self.ds = None
        return datasource, ds_layer

    @logger.trace()
    def generate_contours(self, val_ranges, driver_name, fpath, field_name='DN',
                          field_type=ogr.OFTReal, destroy_after=True):
        datasource, ds_layer = contour_generate(ds=self.ds, val_ranges=val_ranges,
                                                driver_name=driver_name, fpath=fpath,
                                                field_name=field_name, field_type=field_type)
        if not 'mem' in driver_name.lower():
            ds_layer = None
            datasource = None
        if destroy_after: self.ds = None
        return datasource, ds_layer

    @logger.trace(skimpy=True)
    def to_geotiff(self, filepath, no_data_value=-9999, dtype=gdal.GDT_Float32, lazy=False):
        if lazy and os.path.exists(filepath): return filepath
        band = self.ds.GetRasterBand(1)
        arr = band.ReadAsArray()
        [cols, rows] = arr.shape
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(filepath, rows, cols, 1, dtype)
        outdata.SetGeoTransform(self.transform)  ##sets same geotransform as input
        outdata.SetProjection(self.projection)  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(np.where(np.isnan(arr), no_data_value, arr))
        if no_data_value is not False:
            outdata.GetRasterBand(1).SetNoDataValue(no_data_value)  ##if you want these values transparent
        outdata.FlushCache()  ##saves to disk!!
        outdata = None
        band = None
        ds = None
        return filepath

    @logger.trace(skimpy=True)
    def to_file(self, filepath, driver_name, no_data_value=-9999, dtype=gdal.GDT_Float32,
                file_meta: dict = None, band_metas: list = None):
        driver = gdal.GetDriverByName(driver_name)
        cols, rows = self.ds.GetRasterBand(1).ReadAsArray().shape
        outdata = driver.Create(filepath, rows, cols, self.raster_count, dtype)
        outdata.SetGeoTransform(self.transform)  ##sets same geotransform as input
        outdata.SetProjection(self.projection)  ##sets same projection as input
        if file_meta:
            outdata.SetMetadata({str(k): str(v) for k, v in file_meta.items()})

        for band_i in range(self.ds.RasterCount):
            band_num = band_i + 1
            arr = self.ds.GetRasterBand(band_num).ReadAsArray()
            if no_data_value is False:
                the_array = arr
            else:
                the_array = np.where(np.isnan(arr), no_data_value, arr)
            band = outdata.GetRasterBand(band_num)
            band.WriteArray(the_array)
            if band_metas:
                band.SetMetadata({str(k): str(v) for k, v in band_metas[band_i].items()})
            if no_data_value is not False:
                band.SetNoDataValue(no_data_value)  ##if you want these values transparent
        outdata.FlushCache()  ##saves to disk!!
        outdata = None
        band = None
        return filepath

    @logger.trace(skimpy=True)
    def to_file_old(self, filepath, driver_name, no_data_value=-9999, dtype=gdal.GDT_Float32):
        band = self.ds.GetRasterBand(1)
        arr = band.ReadAsArray()
        [cols, rows] = arr.shape
        driver = gdal.GetDriverByName(driver_name)
        outdata = driver.Create(filepath, rows, cols, 1, dtype)
        outdata.SetGeoTransform(self.transform)  ##sets same geotransform as input
        outdata.SetProjection(self.projection)  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(np.where(np.isnan(arr), no_data_value, arr))
        if no_data_value is not False:
            outdata.GetRasterBand(1).SetNoDataValue(no_data_value)  ##if you want these values transparent
        outdata.FlushCache()  ##saves to disk!!
        outdata = None
        band = None
        ds = None
        return filepath

    def scale_array(self, scaler):
        scaled = scaler.fit_transform(self.array.reshape(-1, 1))
        scaled_band = scaled.reshape(self.array.shape)
        out = self.from_array(scaled_band, self.geo_info)
        self.ds = None
        return out

    def get_info(self, **kwargs):
        kwargs = dict(dict(format='json'), **kwargs)
        return gdal.Info(self.ds, options=gdal.InfoOptions(**kwargs))

    @logger.trace(skimpy=True)
    def translate(self, options=None, format=None,
                  outputType=gdalconst.GDT_Unknown, bandList=None, maskBand=None,
                  width=0, height=0, widthPct=0.0, heightPct=0.0,
                  xRes=0.0, yRes=0.0,
                  creationOptions=None, srcWin=None, projWin=None, projWinSRS=None, strict=False,
                  unscale=False, scaleParams=None, exponents=None,
                  outputBounds=None, metadataOptions=None,
                  outputSRS=None, GCPs=None,
                  noData=None, rgbExpand=None,
                  stats=False, rat=True, resampleAlg=None,
                  callback=None, callback_data=None, destroy_after=True, out_path='', return_as_ds=True):
        out_path = out_path or f"/vsimem/{uuid.uuid4()}"
        gdal.Translate(out_path, self.ds, options=gdal.TranslateOptions(
            options=options, format=format, outputType=outputType, bandList=bandList, maskBand=maskBand, width=width,
            height=height,
            widthPct=widthPct, heightPct=heightPct, xRes=xRes, yRes=yRes, creationOptions=creationOptions,
            srcWin=srcWin, projWin=projWin,
            projWinSRS=projWinSRS, strict=strict, unscale=unscale, scaleParams=scaleParams, exponents=exponents,
            outputBounds=outputBounds,
            metadataOptions=metadataOptions, outputSRS=outputSRS, GCPs=GCPs, noData=noData, rgbExpand=rgbExpand,
            stats=stats, rat=rat,
            resampleAlg=resampleAlg, callback=callback, callback_data=callback_data,
        ))
        if return_as_ds:
            out = DataSet(out_path, name='translated')
        else:
            out = out_path
        if destroy_after: self.ds = None
        return out

    @property
    def wkt(self):
        return self.geom.wkt

    @property
    def geom(self):
        return shg.shape(self.get_info()['wgs84Extent'])


@logger.trace(level=logging.DEBUG)
def translate_tiff(input_tiff, output_tiff, translate_opts: gdal.TranslateOptions) -> str:
    ds = gdal.Open(input_tiff)
    ds = gdal.Translate(output_tiff, ds, options=translate_opts)
    ds = None
    return output_tiff


@logger.trace(level=logging.DEBUG)
def rgb_to_geotiff(tiff_path, *band_paths, no_data_value=-9999, dtype=gdal.GDT_Float32, **warp_opts):
    # logsup.logger.info('no_data_value: %s',no_data_value)
    band_dss = [DataSet(path).do_warp(**warp_opts) for path in band_paths]
    band_arrays = [band_ds.array for band_ds in band_dss]
    # for path in band_paths:
    # 	step1=DataSet(path).do_warp(out_epsg=3857,srcNodata=-2000)  #
    # 	step3=step1.scale_array(RobustScaler()).scale_array(MinMaxScaler((0,255))).array
    # 	band_arrays.append(step3)
    # band_arrays=[_get_image_prepared_array(path,warp_opts=dict(out_epsg=3857),scaler=MinMaxScaler((0,255))) for path in band_paths]
    # band_arrays=gsup.ParallelTasker(_get_image_prepared_array,scaler=MinMaxScaler((0,255))).set_run_params(ds=band_paths).run(sleep_time=1e-1)
    # band_arrays=gsup.ParallelTasker(ds_to_array).set_run_params(ds=band_paths).run(sleep_time=1e-1)
    [cols, rows] = band_arrays[0].shape
    driver = gdal.GetDriverByName("GTiff")
    if len(band_paths) == 3:
        options = ['PHOTOMETRIC=RGB', 'PROFILE=GeoTIFF', ]
    else:
        options = None
    # elif len(band_paths)==4:
    # 	options=['PHOTOMETRIC=RGBA','PROFILE=GeoTIFF',]
    # else:
    # 	raise NotImplementedError(f'Invalid number of input files - {len(band_paths)}.',dict(count=len(band_paths)))

    outdata = driver.Create(tiff_path, rows, cols, len(band_paths), dtype, options=options)
    outdata.SetGeoTransform(band_dss[0].transform)  ##sets same geotransform as input
    outdata.SetProjection(band_dss[0].projection)  ##sets same projection as input
    for i, (array, band_interpretation) in \
            enumerate(zip(band_arrays, [gdal.GCI_RedBand, gdal.GCI_GreenBand, gdal.GCI_BlueBand])):
        raster_band = outdata.GetRasterBand(i + 1)
        raster_band.SetColorInterpretation(band_interpretation)
        raster_band.WriteArray(np.where(array == 0, no_data_value, array))
        if no_data_value is not False:
            raster_band.SetNoDataValue(no_data_value)  ##if you want these values transparent

    outdata.FlushCache()  ##saves to disk!!
    outdata = None
    band = None
    ds = None
    return tiff_path


def get_mean_std_scale_params(stack: np.array, std_num=2):
    mean = np.nanmean(stack)
    std = np.nanstd(stack)
    return [max(0, mean - std_num * std), mean + std_num * std]


def GetExtent(gt, cols, rows):
    ''' Return list of corner coordinates from a geotransform

        @type gt:   C{tuple/list}
        @param gt: geotransform
        @type cols:   C{int}
        @param cols: number of columns in the dataset
        @type rows:   C{int}
        @param rows: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner
    '''
    ext = []
    xarr = [0, cols]
    yarr = [0, rows]

    for px in xarr:
        for py in yarr:
            x = gt[0] + (px * gt[1]) + (py * gt[2])
            y = gt[3] + (px * gt[4]) + (py * gt[5])
            ext.append([x, y])
        # print(x,y)

        yarr.reverse()
    return ext


def ReprojectCoords(coords, src_srs, tgt_srs):
    ''' Reproject a list of x,y coordinates.

        @type geom:     C{tuple/list}
        @param geom:    List of [[x,y],...[x,y]] coordinates
        @type src_srs:  C{osr.SpatialReference}
        @param src_srs: OSR SpatialReference object
        @type tgt_srs:  C{osr.SpatialReference}
        @param tgt_srs: OSR SpatialReference object
        @rtype:         C{tuple/list}
        @return:        List of transformed [[x,y],...[x,y]] coordinates
    '''
    trans_coords = []
    transform = osr.CoordinateTransformation(src_srs, tgt_srs)
    for x, y in coords:
        x, y, z = transform.TransformPoint(x, y)
        trans_coords.append([x, y])
    return trans_coords


def get_geo_extent(ds):
    gt = ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    ext = GetExtent(gt, cols, rows)

    src_srs = osr.SpatialReference()
    src_srs.ImportFromWkt(ds.GetProjection())
    # tgt_srs=osr.SpatialReference()
    # tgt_srs.ImportFromEPSG(4326)
    tgt_srs = src_srs.CloneGeogCS()

    geo_ext = ReprojectCoords(ext, src_srs, tgt_srs)
    return geo_ext


class GdalMan(object):
    def __init__(self, debug=False, lazy=False, **kwargs):
        self.out_filepath = None
        self.kwargs = kwargs
        self.debug = debug
        self.lazy = lazy
        self.data = dict()

    def _get_laziness(self, lazy, out_filepath):
        # if Path(out_filepath).suffix.lower() == '.vrt' and lazy:
        #     logger.warning('Lazy is set to True, but provided out_filepath is virtual.',
        #                    dict(provided_vrt_path=out_filepath))
        #     lazy = False
        return self.lazy if lazy is None else lazy

    @property
    def path(self):
        return self.out_filepath

    @property
    def ds(self):
        return DataSet(self.out_filepath)

    def _run_gdal_cmd(self, gdal_func, *args, is_gdal_calc=False, **input_params):
        params = list()
        if is_gdal_calc:
            default_kwargs = self.kwargs.copy()
            if 'q' in self.kwargs:
                q = default_kwargs.pop('q')
                default_kwargs['--quiet'] = q
            options = dict(default_kwargs, **input_params)
        else:
            options = dict(self.kwargs, **input_params)
        for k, v in options.items():
            if v is True:
                if k.startswith('-'):
                    params.append(k)
                else:
                    params.append(f'-{k}')
            elif not v:
                continue
            else:
                if k.startswith('--'):
                    params.append(f"{k}={v}")
                elif k.startswith('-'):
                    params.append(f"{k} {v}")
                else:
                    params.append(f"-{k} {v}")
        run_cmd(f" ".join(map(str, [gdal_func, *args, *params])), debug=self.debug)

    def _finalize_result(self, out_filepath, label_as, debug=None):
        self.out_filepath = self.data[label_as or 'path'] = out_filepath
        debug = debug or self.debug
        if debug:
            if isinstance(debug, str):
                log_level = debug.lower()
            else:
                log_level = 'debug'
            getattr(logger.a(), log_level)("%s: %s", label_as or get_name(self.out_filepath), self.out_filepath).s()
        if not Path(self.out_filepath).exists():
            raise FileNotFoundError(self.out_filepath)
        return self

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def gdalwarp(self, *srcfiles, out_filepath, lazy=None, label_as=None, debug=None, **kwargs):
        lazy = self._get_laziness(lazy, out_filepath)
        if not (lazy and os.path.exists(out_filepath)):
            # if not Path(out_filepath).exists(): os.remove(out_filepath)
            self._run_gdal_cmd('gdalwarp', *srcfiles, out_filepath, **dict(dict(overwrite=True), **kwargs))
        return self._finalize_result(out_filepath, label_as, debug)

    def gdalbuildvrt(self, *gdalfiles, out_filepath, label_as=None, debug=None, **kwargs):
        self._run_gdal_cmd('gdalbuildvrt', out_filepath, *gdalfiles, **dict(dict(overwrite=True), **kwargs))
        return self._finalize_result(out_filepath, label_as, debug)

    def gdal_translate(self, src_dataset, out_filepath, lazy=None, label_as=None, debug=None, **kwargs):
        lazy = self._get_laziness(lazy, out_filepath)
        if not (lazy and os.path.exists(out_filepath)):
            self._run_gdal_cmd('gdal_translate', src_dataset, out_filepath, **kwargs)
        return self._finalize_result(out_filepath, label_as, debug)

    def gdal_merge(self, *input_files, out_filepath, lazy=None, label_as=None, debug=None, **kwargs):
        lazy = self._get_laziness(lazy, out_filepath)
        if not (lazy and os.path.exists(out_filepath)):
            self._run_gdal_cmd('gdal_merge.py', *input_files, **dict(o=out_filepath, **kwargs))
        return self._finalize_result(out_filepath, label_as, debug)

    def gdaldem(self, mode, input_dem, out_filepath, color_text_file=None,
                lazy=None, label_as=None, debug=None, **kwargs):
        if mode == 'color-relief': assert color_text_file is not None
        lazy = self._get_laziness(lazy, out_filepath)
        if not (lazy and os.path.exists(out_filepath)):
            if color_text_file:
                self._run_gdal_cmd('gdaldem', mode, input_dem, color_text_file, out_filepath, **kwargs)
            else:
                self._run_gdal_cmd('gdaldem', mode, input_dem, out_filepath, **kwargs)
        return self._finalize_result(out_filepath, label_as, debug)

    def gdal_calc(self, untagged_expression, out_filepath, equation_info,
                  lazy=None, label_as=None, debug=None, **kwargs):
        lazy = self._get_laziness(lazy, out_filepath)
        if not (lazy and os.path.exists(out_filepath)):
            tags = list(string.ascii_uppercase[:len(equation_info)])
            kwargs = {k.lstrip('-'): v for k, v in kwargs.items()}
            additional_eqn_info = {k: v for k, v in kwargs.items() if k[0].isupper()}

            calc_info = {item_name: dict(tag=tag, path=path) for (item_name, path), tag in
                         zip(dict(equation_info, **additional_eqn_info).items(), tags)}

            tagged_expression = untagged_expression.format(
                **{band_name: v['tag'] for band_name, v in calc_info.items()})
            options = {v['tag']: v['path'] for v in calc_info.values()}

            undashed_options = {'outfile': out_filepath, 'calc': f'"{tagged_expression}"', 'overwrite': True}

            undashed_options.update(kwargs)
            if 'q' in undashed_options:
                q = undashed_options.pop('q')
                undashed_options['quiet'] = q
            for k, v in undashed_options.items():
                options["--" + k] = v
            self._run_gdal_cmd('gdal_calc.py', is_gdal_calc=True, **options)
        return self._finalize_result(out_filepath, label_as, debug)

    def ogr2ogr(self, input_datasource, out_filepath, lazy=None, label_as=None, debug=None, **kwargs):
        lazy = self._get_laziness(lazy, out_filepath)
        if not (lazy and os.path.exists(out_filepath)):
            self._run_gdal_cmd('ogr2ogr', out_filepath, input_datasource, **dict(dict(overwrite=True), **kwargs))
        return self._finalize_result(out_filepath, label_as, debug)

    def gdal_contour(self, src_filename, out_filepath, lazy=None, label_as=None, debug=None, **kwargs):
        lazy = self._get_laziness(lazy, out_filepath)
        if not (lazy and os.path.exists(out_filepath)):
            self._run_gdal_cmd('gdal_contour', src_filename, out_filepath, **kwargs)
        return self._finalize_result(out_filepath, label_as, debug)

    def gdal_polygonize(self, raster_file, out_filepath, layer='polygons',
                        connectedness=4, nomask=False, mask=None, band=None, ogr_format=None, fieldname='DN',
                        lazy=None, label_as=None, debug=None, q=None):
        """
        gdal_polygonize.py [-8] [-nomask] [-mask filename] <raster_file> [-b band]
                   [-q] [-f ogr_format] <out_file> [layer] [fieldname]
        :return: self
        """
        args_1 = list()
        if connectedness != 4: args_1.append(f"-{connectedness}")
        if nomask: args_1.append(f"-nomask")
        if mask is not None: args_1.append(f"-mask {mask}")
        args_2 = list()
        if band is not None: args_2.append(f"-b {band}")
        if q is not None: args_2.append("-q")
        if ogr_format is not None: args_2.append(f"-f {ogr_format}")
        args_3 = list()
        if layer: args_3.append(layer)
        if fieldname: args_3.append(fieldname)

        lazy = self._get_laziness(lazy, out_filepath)
        if not (lazy and os.path.exists(out_filepath)):
            self._run_gdal_cmd('gdal_polygonize.py', *args_2, raster_file, *args_2, out_filepath, *args_3)
        return self._finalize_result(out_filepath, label_as, debug)

    def gdal_rasterize(self, src_filename, out_filepath, lazy=None, label_as=None, debug=None, **kwargs):
        """
        gdal_rasterize [-b band]* [-i] [-at]
    {[-burn value]* | [-a attribute_name] | [-3d]} [-add]
    [-l layername]* [-where expression] [-sql select_statement]
    [-dialect dialect] [-of format] [-a_srs srs_def] [-to NAME=VALUE]*
    [-co "NAME=VALUE"]* [-a_nodata value] [-init value]*
    [-te xmin ymin xmax ymax] [-tr xres yres] [-tap] [-ts width height]
    [-ot {Byte/Int16/UInt16/UInt32/Int32/Float32/Float64/
            CInt16/CInt32/CFloat32/CFloat64}]
    [-optim {[AUTO]/VECTOR/RASTER}] [-q]
    <src_datasource> <dst_filename>
        """
        lazy = self._get_laziness(lazy, out_filepath)
        if not (lazy and os.path.exists(out_filepath)):
            self._run_gdal_cmd('gdal_rasterize', src_filename, out_filepath, **kwargs)
        return self._finalize_result(out_filepath, label_as, debug)


def get_geo_info(upper_left_xy: Union[list, tuple, np.ndarray],
                 resol_xy: Union[list, tuple, np.ndarray],
                 epsg: int) -> tuple:
    """
    Generates custom geo_info.
    :param upper_left_xy: X and Y coordinates of upper left corner.
    :param resol_xy: Resolution of image in X and Y directions.
    :param epsg: EPSG
    :return: transform and projection (i.e. geo_info).
    """
    transform = np.zeros(6)
    transform[0] = upper_left_xy[0] - resol_xy[0] / 2
    transform[1:3] = resol_xy[0], 0
    transform[3] = upper_left_xy[1] + resol_xy[1] / 2
    transform[4:] = 0, -resol_xy[1]

    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(epsg)
    projection = spatial_ref.ExportToWkt()
    geo_info = (transform, projection)
    return geo_info
