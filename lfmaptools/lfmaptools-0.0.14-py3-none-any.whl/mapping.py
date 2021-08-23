from lfmaptools.epsg_defs import webmerc, wgs84

import numpy as np
import rasterio as rio
import contextily as ctx
import geopandas as gpd
import pyproj as Proj
import osmnx as osm

from shapely import wkt
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon, LineString, MultiLineString, LinearRing, mapping
from shapely.ops import transform, linemerge, unary_union, polygonize
from shapely.affinity import translate

from functools import partial

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import matplotlib.colors as colors

def expand_axes(ax,abs_x=0,abs_y=0):
	x0, x1, y0, y1 = ax.axis()
	x0 = x0-abs_x/2.
	x1 = x1+abs_x/2.
	y0 = y0-abs_y/2.
	y1 = y1+abs_y/2.
	ax.set_xlim(x0,x1)
	ax.set_ylim(y0,y1)
	return

def set_min_axes(ax,min_width=50000,min_height=50000):
	x0, x1, y0, y1 = ax.axis()
	x0=x0
	x1=x1
	y0=y0
	y1=y1
	w = (x1-x0)
	h = (y1-y0)
	ew = max(0,min_width-w)
	eh = max(0,min_height-h)
	ax.set_xlim(x0-ew/2,x1+ew/2)
	ax.set_ylim(y0-eh/2,y1+eh/2)
	return

def add_basemap(ax,zoom,provider='Stamen',style='TerrainBackground',zorder=0):
	valid_providers = ctx.providers.keys()
	if provider not in valid_providers:
		raise ValueError("in add_basemap: provider must be one of %r." % valid_providers)
	valid_styles = ctx.providers[provider].keys()
	if style is not None:
		if style not in valid_styles:
			raise ValueError("in add_basemap: style must be one of %r." % valid_styles)
		ctx.add_basemap(ax,zoom=zoom,source=ctx.providers[provider][style],zorder=zorder)
	else:
		ctx.add_basemap(ax,zoom=zoom,source=ctx.providers[provider],zorder=zorder)
	return ax

def add_stamen_basemap(ax, zoom, variant='terrain', zorder=0): 
	validStamen = {'terrain','background','labels','lines'}
	if variant not in validStamen:
		raise ValueError("in add_stamen_basemap: stamen must be one of %r." % validStamen)
	if variant=='background':
		url='http://tile.stamen.com/terrain-background/{z}/{x}/{y}.png'
	elif variant=='labels':
		url='http://tile.stamen.com/terrain-labels/{z}/{x}/{y}.png'
	elif variant=='lines':
		url='http://tile.stamen.com/terrain-lines/{z}/{x}/{y}.png'
	else:
		url='http://tile.stamen.com/terrain/{z}/{x}/{y}.png'
	xmin, xmax, ymin, ymax = ax.axis()
	basemap, extent = ctx.bounds2img(xmin, ymin, xmax, ymax, zoom=zoom, source=url)
	ax.imshow(basemap, extent=extent, interpolation='bilinear',zorder=zorder)
	# restore original x/y limits 
	ax.axis((xmin, xmax, ymin, ymax))
	return ax

def _geodesic_point(poiGDF,xy_displ):
	lat = poiGDF.y
	lon = poiGDF.x
	pointsGDF = gpd.GeoDataFrame()
	pointsGDF['geometry']=None
	pointsGDF['distance']=None
	pointsGDF.crs = poiGDF.crs
	aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
	project = partial(
		Proj.transform,
		Proj.Proj(aeqd_proj.format(lat=lat,lon=lon)),
		Proj.Proj(poiGDF.crs)
		)
	for j,[x,y] in enumerate(xy_displ):
		pt = translate(Point(0,0),xoff=x,yoff=y)
		pointsGDF.loc[j,'geometry'] = transform(project,pt)
		pointsGDF.loc[j,'distance'] = np.sqrt(x*x+y*y)
	return pointsGDF

def add_north_arrow(ax,
			   pos='upper right',
			   rel_shift=[None,None],
			   shift=[0,0],
			   color='k',
			   label='N',
			   zorder=11,
			   fontsize=20):
	validPos ={'upper right',1,
						'upper left',2,
						'lower left',3,
						'lower right',4,
						'right',5,
						'center left',6,
						'center right',7,
						'lower center',8,
						'upper center',9,
						'center',10}
	if pos not in validPos:
		raise ValueError('in scaleBar: pos must be one of %r.' % validPos)
	
	x0, x1, y0, y1 = ax.axis()
	w = (x1-x0)
	h = (y1-y0)
	
	if pos in {'upper right',1}:
		px0 = x1
		py0 = y1
		if rel_shift[0] is None:
			rel_shift=[-0.1,-0.1]
	if pos in {'upper left', 2}:
		px0 = x0
		py0 = y1
		if rel_shift[0] is None:
			rel_shift=[0.1,-0.1]
	if pos in {'lower left', 3}:
		px0 = x0
		py0 = y0
		if rel_shift[0] is None:
			rel_shift=[0.1,0.1]
	if pos in {'lower right',4}:
		px0 = x1
		py0 = y0
		if rel_shift[0] is None:
			rel_shift=[-0.1,0.1]
	if pos in {'right','center right',5,7}:
		px0 = x1
		py0 = y0+0.5*h
	if pos in {'center left',6}:
		px0 = x0
		py0 = y0+0.5*h
	if pos in {'lower center',8}:
		px0 = x0+0.5*w
		py0 = y0
	if pos in {'upper center',9}:
		px0 = x0+0.5*w
		py0 = y1
	if pos in {'center',10}:
		px0 = x0+0.5*w
		py0 = y0+0.5*h
	
	if rel_shift[0] is None: rel_shift[0]=0
	if rel_shift[1] is None: rel_shift[1]=0
	
	px0 += rel_shift[0]*w + shift[0]
	py0 += rel_shift[1]*h + shift[1]
	
	deltaX = 0.03*w
	deltaY = 0.03*h
	
	if len(color)==2:
		colL = color[0]
		colR = color[1]
	else:
		colL = color
		colR = color
	
	arrowPatches = []
	arrowL = np.empty([4,2])
	arrowR = np.empty([4,2])
	arrowL[0,:] = [px0,py0]
	arrowR[0,:] = [px0,py0]
	arrowL[1,:] = [px0,py0+deltaY]
	arrowR[1,:] = [px0,py0+deltaY]
	arrowL[2,:] = [px0-deltaX,py0-0.5*deltaY]
	arrowR[2,:] = [px0+deltaX,py0-0.5*deltaY]
	arrowL[3,:] = arrowL[0,:]
	arrowR[3,:] = arrowR[0,:]
	arrowL_patch = mpatches.Polygon(arrowL,closed=True,facecolor=colL)
	arrowR_patch = mpatches.Polygon(arrowR,closed=True,facecolor=colR)
	arrowPatches.append(arrowL_patch)
	arrowPatches.append(arrowR_patch)
	p = PatchCollection(arrowPatches,match_original=True,zorder=zorder)
	
	ax.add_collection(p)
	Ntext = 'N'
	ntext = ax.text(px0,py0+1.1*deltaY,Ntext,ha='center',fontsize=fontsize,color=color,zorder=zorder)
	return (p,ntext)

def add_scale_bar(ax,
				  pos='lower left',
				  rel_shift=[None,None],
				  shift=[0,0],
				  segments=5,
				  width=None,
				  zorder=11,
				  frame=True,
				  fontsize=6,
				  facecolor=[0.7,0.7,0.7],
				  frame_alpha=1):
	
	validPos ={'upper right',1,
						'upper left',2,
						'lower left',3,
						'lower right',4,
						'right',5,
						'center left',6,
						'center right',7,
						'lower center',8,
						'upper center',9,
						'center',10}
	if pos not in validPos:
		raise ValueError('in scaleBar: pos must be one of %r.' % validPos)
	
	fig = ax.figure

	x0, x1, y0, y1 = ax.axis()
	w = (x1-x0)
	h = (y1-y0)
	
	if width is None:
		width = (ax.get_xticks()[1]-ax.get_xticks()[0])/4
	width = round(width/1000)*1000
	width = max(1000,width)
	height = width/5
	
	if pos in {'upper right',1}:
		px0 = x1
		py0 = y1
		if rel_shift[0] is None:
			rel_shift=[-0.25,-0.05]
	if pos in {'upper left', 2}:
		px0 = x0
		py0 = y1
		if rel_shift[0] is None:
			rel_shift=[0.05,-0.05]
	if pos in {'lower left', 3}:
		px0 = x0
		py0 = y0
		if rel_shift[0] is None:
			rel_shift=[0.05,0.05]
	if pos in {'lower right',4}:
		px0 = x1 - (segments+1)*width
		py0 = y0
		if rel_shift[0] is None:
			rel_shift=[-0.05,0.05]
	if pos in {'right','center right',5,7}:
		px0 = x1
		py0 = y0+0.5*h
	if pos in {'center left',6}:
		px0 = x0
		py0 = y0+0.5*h
	if pos in {'lower center',8}:
		px0 = x0+0.5*w
		py0 = y0
	if pos in {'upper center',9}:
		px0 = x0+0.5*w
		py0 = y1
	if pos in {'center',10}:
		px0 = x0+0.5*w
		py0 = y0+0.5*h
	
	if rel_shift[0] is None: rel_shift[0]=0
	if rel_shift[1] is None: rel_shift[1]=0
	
	px0 += rel_shift[0]*w + shift[0]
	py0 += rel_shift[1]*h + shift[1]
	
	segs = [[x*width,0] for x in range(0,segments+1)]
	pts = _geodesic_point(_ax_gdf(ax).centroid,segs)
	
	xoff = pts.loc[0,'geometry'].x - px0
	yoff = pts.loc[0,'geometry'].y - py0
	
	rect = []
	col = ['k','w']
	texts=[]
	for j in range(1,segments+1):
		anchor_x = pts.loc[j-1,'geometry'].x - xoff
		anchor_y = pts.loc[0,'geometry'].y - yoff
		this_w = pts.loc[j,'geometry'].x - xoff - anchor_x
		rect.append(mpatches.Rectangle((anchor_x,anchor_y),this_w,height,fc=col[0],ec=None,joinstyle='miter'))
		col.reverse()
		scale_text = r'{:d}'.format(int(segs[j][0]/1000))
		if j==segments:
			texts.append(ax.text(anchor_x+this_w,py0-0.02*h,scale_text,fontsize=fontsize,horizontalalignment='center',zorder=zorder))
		else:
			if j==1:
				texts.append(ax.text(anchor_x,py0-0.02*h,r'{:d}'.format(0),fontsize=fontsize,horizontalalignment='center',zorder=zorder))
			texts.append(ax.text(anchor_x+this_w,py0-0.02*h,scale_text,fontsize=fontsize,horizontalalignment='center',zorder=zorder))
	plt.draw()
	inv = ax.transData.inverted()
	bb = inv.transform(texts[-1].get_tightbbox(fig.canvas.get_renderer()).extents)
	texts.append(ax.text(bb[2],py0-0.02*h,r'  km',fontsize=fontsize,horizontalalignment='left',zorder=zorder))
	plt.draw()
	bb1 = inv.transform(texts[-1].get_tightbbox(fig.canvas.get_renderer()).extents)
	
	if frame:
		bbs = np.array([list(r.get_bbox().extents) for r in rect])
		scale_x0 = min(bbs[:,0])
		scale_x1 = max(max(bbs[:,2]),bb1[2])
		scale_y0 = min(bbs[:,1])
		scale_y1 = max(bbs[:,3])
		
		barframe = mpatches.Rectangle((scale_x0-0.02*w,scale_y0-0.02*h),(scale_x1-scale_x0+0.03*w),(scale_y1-scale_y0+0.04*h),fc=facecolor,alpha=frame_alpha,ec=None,zorder=zorder-1)
		ax.add_patch(barframe)
	else:
		barframe = None
	
	p = PatchCollection(rect,zorder=zorder,match_original=True)
	
	ax.add_collection(p)
	
	return (p, barframe)

def _ax_poly(ax,pad_x=0,pad_y=0):
	x0,x1,y0,y1 = ax.axis()
	return Polygon([(x0-pad_x,y0-pad_y),(x0-pad_x,y1+pad_y),(x1+pad_x,y1+pad_y),(x1+pad_x,y0-pad_y)])

def _ax_gdf(ax,crs=webmerc['init'], pad_x=0, pad_y=0):
	axDF = gpd.GeoDataFrame()
	axDF.loc[0,'geometry'] = _ax_poly(ax,pad_x=pad_x,pad_y=pad_y)
	axDF.crs = crs
	return axDF

def _ax_bbox(ax,crs=webmerc):
	axGDF = _ax_gdf(ax,crs=crs).to_crs(wgs84)
	north = axGDF.bounds.maxy.values[0]
	south = axGDF.bounds.miny.values[0]
	east = axGDF.bounds.maxx.values[0]
	west = axGDF.bounds.minx.values[0]
	return north, south, east, west

def _get_osm_roads(ax, crs=webmerc['init']):
	north, south, east, west = _ax_bbox(ax, crs=crs)
	G = osm.graph_from_bbox(north, south, east, west,
							network_type='drive_service')
	nodes, edges = osm.graph_to_gdfs(G)
	roads = edges.to_crs(crs)
	return roads

def _get_osm_buildings(ax, crs=webmerc['init']):
	north, south, east, west = _ax_bbox(ax, crs=crs)
	fp=osm.geometries.geometries_from_bbox(north=north,
										   south=south,
										   east=east,
										   west=west,
										   tags={'building':True})
	buildings = fp.to_crs(crs)
	return buildings

def add_osm(ax,
			roads=True,
			buildings=False,
			road_color='black',
			building_color='gray'):
	if roads:
		roads = _get_osm_roads(ax)
		roads.plot(ax=ax, color=road_color)
	if buildings:
		buildings = _get_osm_buildings(ax)
		buildings.plot(ax=ax, color=building_color)
	return


def add_POI_marker(POI,
				   ax=None,
				   marker='.',
				   markersize=8,
				   color='k',
				   edgecolor='k',
				   linewidth=0,
				   label=None,
				   zorder=0,
				   avoid_overlap=None):
	if type(color)==colors.ListedColormap:
		col = lambda x: color(x)
	elif type(color)==list:
		col = lambda x: color[x]
	elif color is None:
		col = lambda x: 'none'
	else:
		col = lambda x: color
	x0, x1, y0, y1 = ax.axis()
	axPoly = _ax_poly(ax)
	
	if label is not None:
		if label not in POI.columns:
			raise RuntimeError('in add_POI_marker plot, label must be in the POI columns')
	
	POIax = POI[POI.geometry.intersects(axPoly)]
	
	for i, p in POI.iterrows():
		px = p.geometry.x
		py = p.geometry.y
		if x0<=px<=x1 and y0<=py<=y1:
			if avoid_overlap is not None:
				if len(avoid_overlap[avoid_overlap.geometry==p.geometry])>0:
					px = px + min(0.01*(x1-x0),1000)
					py = py + min(0.01*(y1-y0),1000)
			if label is not None:
				ax.scatter(px,py,markersize,marker=marker,facecolor=col(p[label]),edgecolors=edgecolor,linewidths=linewidth,zorder=zorder)
			else:
				ax.scatter(px,py,markersize,marker=marker,facecolor=col(0),edgecolors=edgecolor,linewidths=linewidth,zorder=zorder)
	
	leg_handles = []
	leg_labels = []
	if label is not None:
		p1 = plt.scatter([],[],markersize,marker=marker,facecolor=col(p[label]),edgecolors=edgecolor,linewidths=linewidth)
		leglabel = label
	else:
		p1 = plt.scatter([],[],markersize,marker=marker,facecolor=col(0),edgecolors=edgecolor,linewidths=linewidth)
		leglabel = None
	
	return (p1, leglabel)