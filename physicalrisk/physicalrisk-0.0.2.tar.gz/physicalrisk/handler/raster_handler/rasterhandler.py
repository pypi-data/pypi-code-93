
import numpy as np
from osgeo import gdal, osr
from typing import Tuple

gdal.UseExceptions()
gdal_driver = gdal.GetDriverByName('GTiff')
invalid = np.array(np.nan)

class RasterHandler():

    def __init__(self):
        pass
    # array of picel:
    # long and lat to pixel: [0,0] at the center
    # conver long and lat to index of pixel in raster.
    @staticmethod
    def read_crop_geotif(infilename: str, bounds: list, outfilename: str=None) -> Tuple[np.array, list, list]:
        dataset = gdal.Open(infilename)
        transform = dataset.GetGeoTransform()
        xOrigin = transform[0]
        yOrigin = transform[3]
        pixelWidth = transform[1]
        pixelHeight = transform[5]
        xMin = bounds[0][0]
        xMax = bounds[1][0]
        yMin = bounds[0][1]
        yMax = bounds[1][1]

        i1 = int(round((xMin - xOrigin) / pixelWidth))
        j1 = int(round((yMax - yOrigin) / pixelHeight))
        i2 = int(round((xMax - xOrigin) / pixelWidth))
        j2 = int(round((yMin - yOrigin) / pixelHeight))
        # converting the lat and long to raster index
        # lat and long to the raster format.
        #

        new_cols = i2 - i1 + 1
        new_rows = j2 - j1 + 1
        data = dataset.ReadAsArray(i1, j1, new_cols, new_rows)
        lons = [xOrigin + i * pixelWidth for i in range(i1, i2 + 1)]
        lats = [yOrigin + j * pixelHeight for j in range(j1, j2 + 1)]
        # setting extension of output raster
        # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
        new_transform = (xMin, transform[1], transform[2], yMax, transform[4], transform[5])
        if outfilename:
            # Create gtif file
            dataset_croped = gdal_driver.Create(outfilename, new_cols, new_rows, 1, gdal.GDT_Float32)
            # writting output raster
            if len(data.shape) == 3:
                for i in range(data.shape[0]):
                    dataset_croped.GetRasterBand(1).WriteArray(data[i])
            else:
                dataset_croped.GetRasterBand(1).WriteArray(data)
            dataset_croped.SetGeoTransform(new_transform)
            wkt = dataset.GetProjection()
            # setting spatial reference of output raster
            srs = osr.SpatialReference()
            srs.ImportFromWkt(wkt)
            dataset_croped.SetProjection(srs.ExportToWkt())
        # Close output raster dataset
        dataset = None
        dataset_croped = None
        return data, lons, lats