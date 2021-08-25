import tempfile

import cv2
import geojson
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely.affinity as shaff
from box import Box
from osgeo import gdal
from scipy import ndimage

from . import gdal_datasets as gds, Folder
from . import logger
from .common.utils import run_cmd
from .pathify import get_name


class Vectorizer(object):
    def __init__(self, ds, array=None, no_data_value=-9999, **history):
        self.ds = gds.DataSet(ds, array=array)
        self.history = Box(history, default_box=True)
        self.no_data_value = no_data_value
        self._data = np.where(self.ds.array == no_data_value, np.nan, self.ds.array)
        logger.debug('_data.shape: %s', self._data.shape)
        # self.history.original_data=self._data
        single_pixel_area = abs(self.ds.transform[1] * self.ds.transform[-1]) / 1e4
        self.area = np.count_nonzero(~np.isnan(self._data)) * single_pixel_area
        logger.debug('area (Ha):%s', self.area)
        self.__geo_info = self.ds.geo_info
        self._geometry = None
        self.history.original.geo_info = self.ds.geo_info
    
    @property
    def geometry(self):
        if self._geometry is None:
            self._geometry = Vectorizer(self.ds.path,
                                        no_data_value=self.no_data_value) \
                .vectorize(1) \
                .simplify() \
                .history.vectors.geometry.cascaded_union
        return self._geometry
    
    @property
    def data(self) -> np.ndarray:
        return self._data
    
    @property
    def geo_info(self):
        return self.__geo_info
    
    @property
    def raster_area(self):
        single_pixel_area = abs(self.ds.transform[1] * self.ds.transform[-1]) / 1e4
        return np.count_nonzero(~np.isnan(self._data)) * single_pixel_area
    
    @staticmethod
    def get_resized_array(array, scale_factor):
        resized_data = cv2.resize(array, tuple(np.round(np.array(array.shape) * scale_factor).astype(int))[::-1],
                                  interpolation=cv2.INTER_CUBIC)
        return resized_data
    
    @logger.trace()
    def resize(self, scale_factor):
        # Plotter(self.data)
        self.history.scale_factor = scale_factor
        resized_data = self.get_resized_array(self.data, scale_factor=scale_factor)
        logger.debug('resized_data.shape: %s', resized_data.shape)
        # self.history.resized_data=resized_data
        self._data = resized_data
        transform, projection = self.geo_info
        transform = list(transform)
        transform[1] /= scale_factor
        transform[-1] /= scale_factor
        self.__geo_info = transform, projection
        logger.debug('new_geo_info: %s', self.__geo_info)
        
        return self
    
    @logger.trace()
    def smooth(self, sigma=1):
        logger.debug('self.data.shape: %s', self.data.shape)
        self._data = ndimage.gaussian_filter(self.data, sigma=sigma)
        # Plotter().add_images(self.data,res).plot()
        
        return self
    
    @staticmethod
    def get_digitized(array, bins):
        if isinstance(bins, (int, np.integer)):
            bin_edges = np.histogram_bin_edges(array[~np.isnan(array)], bins)
        else:
            bin_edges = bins
        logger.debug('bin_edges: %s', bin_edges)
        digitized_data = np.digitize(array, bin_edges)
        return digitized_data, bin_edges
    
    @staticmethod
    def get_georeferenced_vectors(vectors: gpd.GeoDataFrame, transform, raster_shape):
        vectors.geometry = vectors.geometry.map(
            lambda g: shaff.scale(g, xfact=transform[1], yfact=abs(transform[5]), origin=(0, 0))
        )
        vectors.geometry = vectors.geometry.map(
            lambda g: shaff.translate(g, transform[0], transform[3] + transform[5] * raster_shape[0]))
        return vectors
    
    @staticmethod
    def get_vectorized(array, bins, geo_info, **kwargs):
        # old_array=array
        # if isinstance(bins,(int,np.integer)) and bins<0:
        
        array, bin_edges = Vectorizer.get_digitized(array, bins)
        # Plotter(old_array,array)
        vectors = list()
        unique_values = np.unique(array)
        potrace_folder = Folder(tempfile.mkdtemp())
        for unique_value_i, unique_value in enumerate(unique_values):
            # logger.debug('unique_value: %s',unique_value)
            tmp_folder = potrace_folder[f'unique_value_{unique_value}']
            if unique_value == len(bin_edges):
                # logger.info('Continuing')
                continue
            value_mask = np.where(array == unique_value, 0, 255)
            mask_ds = gds.DataSet.from_array(value_mask, geo_info)
            bmp_filepath = mask_ds.to_file(filepath=tmp_folder[f'mask_{unique_value}.bmp'],
                                           driver_name='BMP', no_data_value=0, dtype=gdal.GDT_Byte)
            vector_path = tmp_folder[f"out_{unique_value}.geojson"]
            cmd_kwargs = " ".join([f'--{k} {v}' for k, v in kwargs.items()])
            run_cmd(f'potrace -o {vector_path} -b geojson {bmp_filepath} ' + cmd_kwargs)
            df: gpd.GeoDataFrame = gpd.GeoDataFrame.from_file(vector_path)
            df['DN'] = np.mean(bin_edges[unique_value_i:unique_value_i + 2])
            # logger.debug('df:\n%s',df)
            vectors.append(df)
        potrace_folder.delete()
        
        combined_vectors = Vectorizer.get_georeferenced_vectors(
            vectors=gpd.GeoDataFrame(pd.concat(vectors, ignore_index=True), crs=3857),
            transform=geo_info[0],
            raster_shape=array.shape)
        return combined_vectors
    
    @logger.trace()
    def vectorize(self, bins, **kwargs):
        # Plotter().add_images(self.data).plot()
        vectors: gpd.GeoDataFrame = self.get_vectorized(self.data,
                                                        bins=bins,
                                                        geo_info=self.geo_info,
                                                        **kwargs)
        self.history.vectors = vectors
        return self
    
    # @staticmethod
    # def _simplify_polygon(s: gpd.GeoSeries,decimals=3,area_threshold=0):
    # 	simplifier=lambda linering:ThePoly(simplify_coords(np.round(ThePoly(linering)
    # 	                                                            .xy,decimals=decimals)
    # 	                                                   .copy(order='C'),1)).geometry
    #
    # 	g: shg.Polygon=s.geometry
    #
    # 	g_exterior=simplifier(g.exterior).exterior.coords
    # 	g_interiors=list()
    # 	# has_interior=False
    # 	for interior in g.interiors:
    # 		interior_geom=simplifier(interior)
    # 		if interior_geom.area<area_threshold:
    # 			logger.debug('interior_geom.area: %s',interior_geom.area)
    # 			continue
    # 		# self.history.interiors_lookup_data.append(dict(
    # 		# 	parent_index=s.name,geometry=interior_geom
    # 		# ))
    # 		# has_interior=True
    # 		g_interiors.append(interior_geom.exterior.coords)
    # 	out_g=shg.Polygon(g_exterior,g_interiors)
    #
    # 	# if has_interior:
    # 	# 	out_g_no_holes=shg.Polygon(g_exterior)
    # 	# 	logger.debug('out_g_no_holes: %s',out_g_no_holes)
    # 	# 	out_g_with_holes=shg.Polygon(g_exterior,g_interiors)
    # 	# 	logger.debug('out_g_with_holes: %s',out_g_with_holes)
    # 	#
    # 	# 	ThePoly(g).plot('input_geometry',c='green')
    # 	# 	ThePoly(out_g).plot('output_geometry',c='red')
    # 	# 	plt.show()
    # 	# g=ThePoly(simplify_coords(ThePoly(g).xy.copy(order='C'))).geometry
    # 	return out_g
    
    # @staticmethod
    # def _make_difference(g1,g2,max_tries=100):
    # 	try_count=0
    # 	while try_count<max_tries:
    # 		try_count+=1
    # 		try:
    # 			res=g1.difference(g2)
    # 			# logger.debug('res: %s',res)
    # 			return res.iloc[0]
    # 		except shapely.errors.TopologicalError:
    # 			if not isinstance(g2,shg.MultiPolygon): raise ValueError
    # 			g2: shg.MultiPolygon=g2
    # 			out_polys=list()
    # 			for poly in g2:
    # 				poly: shg.Polygon=poly
    # 				out_poly=ThePoly(ThePoly(poly).xy+np.random.rand()*1e-6).geometry
    # 				for interior in poly.interiors:
    # 					logger.debug('interior: %s',interior)
    # 					out_poly=out_poly.difference(shg.Polygon(interior))
    #
    # 				out_polys.append(out_poly)
    # 			out_multipolygon=shg.MultiPolygon(out_polys)
    # 			return out_multipolygon
    # 	# logger.debug('type(g2): %s',type(g2))
    # 	# for g2.exterior
    # 	# g2=shaff.scale(g2,xfact=1+np.random.rand()*1e-3*(try_count+1),yfact=1+np.random.rand()*1e-3*(try_count+1))
    # 	raise NotImplementedError
    
    # @staticmethod
    # def get_united(vectors: gpd.GeoDataFrame,geo_info):
    # 	vector_path=Vectorizer.get_saved(vectors,tempfile.mktemp('.geojson'))
    # 	transform=geo_info[0]
    # 	# vector_path=r'/home/lgblkb/PycharmProjects/imagination/tests/vector_results/ndvi_lgblkb_test_1_13.geojson'
    # 	# this_folder['rasters'].get_filepath('raster_result',ext='.tiff',iterated=True)
    # 	raster_path=rasterize(vector_path,tempfile.mktemp('.tiff'),burn_value=1,
    # 	                      x_res=transform[1],y_res=abs(transform[-1]),NoData_value=0)
    # 	logger.debug('raster_path: %s',raster_path)
    # 	vectors=Vectorizer(raster_path,no_data_value=0)\
    # 		.vectorize(bins=1).history.vectors
    # 	#get_vectorized(array=gds.DataSet(raster_path).array,bins=1,geo_info=geo_info)
    # 	os.remove(vector_path)
    # 	os.remove(raster_path)
    # 	logger.debug('vectors:\n%s',vectors)
    # 	return vectors
    
    # @staticmethod
    # def get_simplified(vectors: gpd.GeoDataFrame,geo_info,scale_factor,biggest_n=200,**kwargs):
    # 	vectors.geometry=vectors.apply(partial(Vectorizer._simplify_polygon,**kwargs),axis=1)
    #
    # 	# vectors=vectors.copy()
    # 	# vectors['area']=vectors.area
    # 	# total_area=vectors.area.sum()
    # 	# logger.debug('total_area: %s',total_area)
    # 	# vectors=vectors.sort_values(by=['area'],ascending=False).drop(columns=['area'])
    # 	# target_vectors: gpd.GeoDataFrame=vectors.iloc[:biggest_n,:].copy()
    # 	# logger.debug('target_vectors:\n%s',target_vectors)
    # 	# targets_area=target_vectors.area.sum()
    # 	# logger.debug('targets_area: %s',targets_area)
    # 	# delta_area=total_area-targets_area
    # 	# logger.debug('delta_area: %s',delta_area)
    #
    # 	# target_vectors.geometry=target_vectors.apply(partial(
    # 	# 	Vectorizer._simplify_polygon,area_threshold=target_vectors.area.min(),**kwargs),axis=1)
    # 	# smaller_vectors: gpd.GeoDataFrame=vectors.iloc[biggest_n:,:].copy()
    # 	# logger.debug('smaller_vectors:\n%s',smaller_vectors)
    # 	logger.debug('vectors:\n%s',vectors)
    # 	return vectors
    
    @logger.trace()
    def simplify(self, percent=10):
        temp_vector_path = self.save(tempfile.mktemp('.geojson'))
        output_path = tempfile.mktemp('.geojson')
        logger.debug('output_path: %s', output_path)
        run_cmd(f'mapshaper {temp_vector_path} -simplify {percent}% -o {output_path}', check=False)
        self.history.vectors = gpd.read_file(output_path, crs=3857)
        logger.debug('self.history.vectors:\n%s', self.history.vectors)
        
        # self.history.vectors=self.get_simplified(vectors=self.history.vectors,
        #                                          geo_info=self.geo_info,
        #                                          scale_factor=self.history.get('scale_factor',1),
        #                                          **kwargs)
        return self
    
    # @logger.trace()
    # def simplify_old(self,biggest_n=200,**kwargs):
    #
    # 	vectors: gpd.GeoDataFrame=self.history.combined_vectors
    # 	# self.history.interiors_lookup_data=list()
    # 	vectors.geometry=vectors.apply(partial(self._simplify_polygon,**kwargs),axis=1)
    # 	# interiors_lookup_table=ilt=gpd.GeoDataFrame(self.history.interiors_lookup_data)
    # 	# logger.debug('interiors_lookup_table:\n%s',interiors_lookup_table)
    # 	vectors['area']=vectors.area
    # 	vectors.sort_values(by=['area'],ascending=False,inplace=True)
    # 	target_vectors=vectors.iloc[:biggest_n,:].copy()
    # 	targets_area=target_vectors.area.sum()
    # 	logger.debug('targets_area: %s',targets_area)
    #
    # 	logger.debug('target_vectors:\n%s',target_vectors)
    #
    # 	# target_interior_geoms=ilt[ilt.parent_index.isin(target_vectors.index)].copy()
    # 	# target_interior_geoms=target_interior_geoms[target_interior_geoms.area<target_vectors.area.min()]
    # 	# logger.debug('target_interior_geoms:\n%s',target_interior_geoms)
    # 	# target_interior_geoms
    # 	# target_vectors.geometry=target_vectors.geometry.map(partial(self._simplify_polygon,**kwargs))
    # 	target_vectors.geometry=target_vectors.apply(partial(self._simplify_polygon,
    # 	                                                     area_threshold=target_vectors.area.min(),
    # 	                                                     **kwargs),axis=1)
    #
    # 	# ds_geom:gpd.GeoSeries=Vectorizer(self.ds,no_data_value=self.no_data_value)\
    # 	# 	.digitize(1).vectorize().history.combined_vectors.geometry
    #
    # 	# simplify_geom=lambda g:ThePoly(np.round(ThePoly(g).xy,decimals=decimals)).geometry
    # 	# vectors.geometry=vectors.geometry.map(simplify_geom)
    # 	# logger.debug('vectors.area:\n%s',vectors.area)
    # 	# groups=list()
    # 	# for dn,group in vectors.groupby('dn'):
    # 	# 	group: gpd.GeoDataFrame=group
    # 	# 	plt.hist(group.area,bins=100)
    # 	# 	plt.show()
    #
    # 	self.history.combined_vectors=target_vectors  #=vectors[vectors.area>min_area]
    # 	logger.debug('vectors:\n%s',self.history.combined_vectors)
    # 	return self
    
    # @logger.trace()
    # def differentiate(self):
    # 	vectors: gpd.GeoDataFrame=self.history.combined_vectors
    # 	vectors['area']=vectors.area
    # 	vectors=vectors.sort_values('area',ascending=True).drop(columns=['area']).reset_index(drop=True)
    # 	# logger.debug('vectors:\n%s',vectors)
    # 	polys=list()
    # 	for first_item in range(vectors.shape[0]):
    # 		logger.debug('item: %s',first_item)
    # 		previous_polys: gpd.GeoDataFrame=vectors.iloc[:first_item,:]
    # 		current_poly: gpd.GeoDataFrame=vectors.iloc[[first_item],:]
    # 		# next_polys=vectors.iloc[first_item+1:,:]
    # 		# logger.debug('current_poly:\n%s',current_poly)
    # 		# logger.debug('next_polys:\n%s',next_polys)
    # 		# if next_polys.empty:
    # 		# 	intersection=current_poly
    # 		# else:
    # 		# 	intersection=gpd.overlay(current_poly,next_polys,how='intersection')
    # 		# logger.debug('intersection:\n%s',intersection)
    # 		# logger.debug('current_poly:\n%s',current_poly)
    # 		# logger.debug('previous_polys:\n%s',previous_polys)
    # 		# logger.debug('previous_polys.cascaded_union:\n%s',previous_polys.cascaded_union)
    # 		# continue
    # 		difference=self._make_difference(current_poly,
    # 		                                 previous_polys.cascaded_union)  #current_poly.difference(previous_polys.cascaded_union)
    # 		# logger.debug('difference:\n%s',difference)
    #
    # 		# logger.debug('difference:\n%s',difference)
    # 		# logger.debug('type(difference): %s',type(difference))
    # 		if difference is None: continue
    # 		current_poly.geometry=[difference]
    # 		# logger.debug('current_poly:\n%s',current_poly)
    # 		# logger.debug('difference:\n%s',difference)
    # 		# if isinstance(difference,gpd.GeoSeries): difference=gpd.GeoDataFrame(difference).T
    #
    # 		# if previous_polys.empty:
    # 		# 	difference=current_poly
    # 		# else:
    # 		# 	difference=gpd.overlay(current_poly,previous_polys,how='difference')\
    # 		# 		.drop(columns=['dn_2'],errors='ignore').rename(columns=dict(dn_1='dn'))
    # 		# logger.debug('difference:\n%s',difference)
    # 		# # logger.debug('type(difference):\n%s',type(difference))
    # 		# logger.debug('difference.empty: %s',difference.empty)
    # 		# if difference.empty: continue
    # 		polys.append(current_poly.explode())
    # 	# return self
    # 	# polys.append(vectors.iloc[[-1],:])  # add the last smallest poly
    # 	resultant_vectors=gpd.GeoDataFrame(pd.concat(polys),crs=3857).reset_index(drop=True)
    # 	logger.debug('resultant_vectors:\n%s',resultant_vectors)
    # 	self.history.combined_vectors=resultant_vectors
    # 	return self
    
    @staticmethod
    def get_saved(vectors: gpd.GeoDataFrame, vector_path):
        if 'DN' in vectors.columns:
            property_getter = lambda s: dict(DN=np.round(s.DN, decimals=5))
        else:
            property_getter = lambda s: None
        
        features = vectors.apply(lambda s: geojson.Feature(geometry=s.geometry, properties=property_getter(s)), axis=1)
        # logger.debug('features:\n%s',features)
        data = geojson.FeatureCollection(features.tolist(), name=get_name(vector_path),
                                         crs=dict(type="name",
                                                  properties=dict(name="urn:ogc:def:crs:EPSG::3857")), )
        with open(vector_path, 'w') as fh:
            geojson.dump(data, fh)
        logger.debug('vector_path: %s', vector_path)
        return vector_path
    
    @logger.trace()
    def save(self, vector_path):
        return self.get_saved(self.history.vectors, vector_path)
