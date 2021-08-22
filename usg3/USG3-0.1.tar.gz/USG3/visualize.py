<<<<<<< HEAD
"""

This module focuses on the visualization of geospatial data 

"""


=======
>>>>>>> 5008b8b2173e1144705e22b428283a3ac74ca6ac
import numpy as np
import plotly.offline as go_offline
import plotly.graph_objects as go
import sys
import os
import logging
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation,LinearTriInterpolator
import rasterio
import pandas as pd
from shapely.geometry import Point
from rasterio.transform import Affine
from rasterio.crs import CRS
from shapely.geometry import Polygon
from rasterio.plot import show
<<<<<<< HEAD
=======
import earthpy.plot as ep
>>>>>>> 5008b8b2173e1144705e22b428283a3ac74ca6ac


logging.basicConfig(filename='../logs/visaulize.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)


def visualize_3D(las_file,output_name, **kwargs):
    
    print ("#### Accessing 3D plotting function #### \n")
    logging.info(" #### Accessing 3D plotting function #### \n ")
    
    #we get the column we require for plotting the 3d plot
    try:
        
        print(" #### Obtaining data files #### \n")
        x=las_file['X'][:3900]
        y=las_file['Y'][:3900]
        z=las_file['Z'][:3900]
    
        print(" #### Successfull #### \n")
        logging.info(" #### Successfull #### \n")
    
    #handle any exception and exit system safely
    except Exception as e:
        
        print(" !!! Error !!!!! \n")
        print (" !!! An excetion occurred Error: {} ".format(e.__class__))
        logging.error(" !!! Error Program Failed !!!!! \n")
        logging.error("Safely exiting the program")
        print("Safely exiting the program")
        sys.exit(1)
        

    print(" #### getting distance function #### \n ")
    logging.info("#### getting distance function #### \n")
    def distance(x1,y1,x2,y2):
        
        d=np.sqrt((x1-x2)**2+(y1-y2)**2)
        return d
    
    
    #this function calcualtes points it has to plot
    
    print(" #### plotting function accessed #### \n")
    def idw_npoint(xz,yz,n_point,p):
        r=10 #block radius iteration distance
        nf=0
        while nf<=n_point: #will stop when np reaching at least n_point
            x_block=[]
            y_block=[]
            z_block=[]
            r +=10 # add 10 unit each iteration
            xr_min=xz-r
            xr_max=xz+r
            yr_min=yz-r
            yr_max=yz+r
            for i in range(len(x)):
                # condition to test if a point is within the block
                if ((x[i]>=xr_min and x[i]<=xr_max) and (y[i]>=yr_min and y[i]<=yr_max)):
                    x_block.append(x[i])
                    y_block.append(y[i])
                    z_block.append(z[i])
            nf=len(x_block) #calculate number of point in the block

        #calculate weight based on distance and p value
        w_list=[]
        for j in range(len(x_block)):
            d=distance(xz,yz,x_block[j],y_block[j])
            if d>0:
                w=1/(d**p)
                w_list.append(w)
                z0=0
            else:
                w_list.append(0) #if meet this condition, it means d<=0, weight is set to 0

        #check if there is 0 in weight list
        w_check=0 in w_list
        if w_check==True:
            idx=w_list.index(0) # find index for weight=0
            z_idw=z_block[idx] # set the value to the current sample value
        else:
            wt=np.transpose(w_list)
            z_idw=np.dot(z_block,wt)/sum(w_list) # idw calculation using dot product
            
        return z_idw
    
    
    n=100 #number of interpolation point for x and y axis
    x_min=min(x)
    x_max=max(x)
    y_min=min(y)
    y_max=max(y)
    w=x_max-x_min #width
    h=y_max-y_min #length
    wn=w/n #x interval
    hn=h/n #y interval

    #list to store interpolation point and elevation
    y_init=y_min
    x_init=x_min
    x_idw_list=[]
    y_idw_list=[]
    z_head=[]
    for i in range(n):
        print(" ##### fine tuning image, layer : {} #### \n ".format(i))
        xz=x_init+wn*i
        yz=y_init+hn*i
        y_idw_list.append(yz)
        x_idw_list.append(xz)
        z_idw_list=[]
        for j in range(n):
            xz=x_init+wn*j
            z_idw=idw_npoint(xz,yz,5,1.5) #min. point=5, p=1.5
            z_idw_list.append(z_idw)
        z_head.append(z_idw_list)
    
    print("#### Plotting 3D Image #### \n ")
    fig=go.Figure()
    fig.add_trace(go.Surface(z=z_head,x=x_idw_list,y=y_idw_list,colorscale=[[0, "rgb(166,206,227)"],
                [0.25, "rgb(31,120,180)"],
                [0.45, "rgb(178,223,138)"],
                [0.65, "rgb(51,160,44)"],
                [0.85, "rgb(251,154,153)"],
                [1, "rgb(227,26,28)"]]))
    print(" #### updating_layout #### \n ")
    fig.update_layout(scene=dict(aspectratio=dict(x=2, y=2, z=0.5),xaxis = dict(range=[x_min,x_max],),yaxis = dict(range=[y_min,y_max])))
    file_store=output_name+".html"
    go_offline.plot(fig,filename=file_store,validate=True, auto_open=False)
    
    
def standardize_plot(geo_frame,setcrs,tiff_file,shp_output):
    
    
    print(" #### Accessing Standardized plot ##### \n")
    
    try:
        print("### Reading Shape plot #### \n")
        points=pd.read_csv(geo_frame)
        geoDF=points[['X','Y','Z']]
        
    except FileNotFoundError as f:
        print(" !!! The file file doesn't exist !!!! ")
        sys.exit(1)
        
        
    try:    
        print(" #### converting into a geopandas df #### \n")
        geometry=[Point(xy)for xy in zip(pd.to_numeric(geoDF['X']),pd.to_numeric(geoDF['Y']))]
        print(" #### Setting Cordinate refrence system reprojection #### \n")
        geoDF=gpd.GeoDataFrame(geoDF,crs=setcrs,geometry=geometry)
        geoDF=geoDF[['Z','geometry']]
        geoDF.reset_index()
    
    except Exception as e:
        
        print(" !!! Error !!!!! \n")
        print (" !!! An excetion occurred Error: {} ".format(e.__class__))
        logging.error(" !!! Error Program Failed !!!!! \n")
        logging.error("Safely exiting the program")
        print("Safely exiting the program")
        sys.exit(1)
        
    totalPointsArray=np.zeros([geoDF.shape[0],3])
    for index ,point in geoDF.iterrows():
        pointArray=np.array([point.geometry.coords.xy[0][0],point.geometry.coords.xy[1][0],point['Z']])
        totalPointsArray[index]=pointArray
        
    triFn=Triangulation(totalPointsArray[:,0],totalPointsArray[:,1])

    linTriFin=LinearTriInterpolator(triFn,totalPointsArray[:,2])
    
    rasterRes=1

    xCoords =np.arange(totalPointsArray[:,0].min(),totalPointsArray[:,0].max()+rasterRes,rasterRes)
    yCoords=np.arange(totalPointsArray[:,1].min(),totalPointsArray[:,1].max()+rasterRes,rasterRes)
    zCoords=np.zeros([yCoords.shape[0],xCoords.shape[0]])

    for indexX, x in np.ndenumerate(xCoords):
        for indexY, y in np.ndenumerate(yCoords):
            tempZ=linTriFin(x,y)

            if tempZ==tempZ:
                zCoords[indexY,indexX]=tempZ
            else:
                zCoords[indexY,indexX]=np.nan

    plt.imshow(zCoords)
        
    
    
    transform=Affine.translation(xCoords[0] -rasterRes/2,yCoords[0] - rasterRes/2) *Affine.scale(rasterRes,rasterRes)
    
    from rasterio.crs import CRS
    rasterCrs=CRS.from_epsg(32718)
    rasterCrs.data
    
    
    triInterpRaster = rasterio.open(tiff_file,
                                'w',
                                driver='GTiff',
                                height=zCoords.shape[0],
                                width=zCoords.shape[1],
                                count=1,
                                dtype=zCoords.dtype,
                                #crs='+proj=latlong',
                                crs={'init': 'epsg:32718'},
                                transform=transform,
                                )
    triInterpRaster.write(zCoords,1)
    triInterpRaster.close()
    
    geoDFR=geoDF.drop(labels='Z',axis=1)
    geoDFR.reset_index()
    
    
    interpolatedPoints = geoDFR[:500000]
    interpolatedPoints['elev'] = ''
    for index, point in interpolatedPoints.iterrows():
        tempZ = linTriFin(point.geometry.coords.xy[0][0],point.geometry.coords.xy[1][0])
        if tempZ == tempZ:
            interpolatedPoints.loc[index,'elev'] = float(tempZ)
        else:
            interpolatedPoints.loc[index,'elev'] = np.nan
    #save as shapefile
    interpolatedPoints.to_file(shp_output)
    
    
    src = rasterio.open(tiff_file)

    fig, ax = plt.subplots(figsize=(24,16))

    geoDF.plot(ax=ax, marker='D',markersize=50,aspect=1)
    interpolatedPoints.plot(ax=ax, markersize=10, color='orangered',aspect=1)
    show(src)
    plt.show()

<<<<<<< HEAD
=======
def visualize_raster(tiff_file, **kwargs):
    raster_image=rasterio.open(tiff_file)
    show(raster,cmap='Reds')
    
def visalize_clean_raster(raster_path,**kwargs):
    print(" #### Accessed clean visaulization function #### \n")
    
    try:
        with rasterio.open(raster_path) as dem_src:
            dtm_pre_arr=dem_src.read(1)
            
    except Exception as e:
        
        print(" !!! Error !!!!! \n")
        print (" !!! An excetion occurred Error: {} ".format(e.__class__))
        logging.error(" !!! Error Program Failed !!!!! \n")
        logging.error("Safely exiting the program")
        print("Safely exiting the program")
        sys.exit(1)
        
    ep.plot_bands(dtm_pre_arr)
    
    
    print("the minimum raster value is: ", dtm_pre_arr.min())
    print("the maximum raster value is: \n", dtm_pre_arr.max())
    
    
    print(" #### Plotting histogram ##### \n ")
    ep.hist(dtm_pre_arr,
        figsize=(10, 6))
    plt.show()
    
    
    # Read in your data and mask the no data values
    with rasterio.open(raster_path) as dem_src:
    # Masked=True will mask all no data values
        dtm_pre_arr = dem_src.read(1, masked=True)
    
    print("the minimum raster value is: ", dtm_pre_arr.min())
    print("the maximum raster value is: ", dtm_pre_arr.max())
    
    # A histogram can also be helpful to look at the range of values in your data
    ep.hist(dtm_pre_arr,
            figsize=(10, 6),
            title="Histogram of the Data with No Data Values Removed")
    plt.show()
    
    # Plot data using earthpy
    ep.plot_bands(dtm_pre_arr,
              title="Lidar Digital Elevation Model (DEM) \n ",
              cmap="Greys")

    plt.show()
>>>>>>> 5008b8b2173e1144705e22b428283a3ac74ca6ac
    