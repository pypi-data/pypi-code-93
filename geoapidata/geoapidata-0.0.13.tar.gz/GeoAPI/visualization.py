import sys
from numpy.lib.shape_base import split
from pandas.core.frame import DataFrame
sys.path.append("..")
from matplotlib.pyplot import text
import pandas as pd
import plotly.graph_objects as go
import plotly.express as xp
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from sklearn.metrics.pairwise import haversine_distances,euclidean_distances
from math import radians

from GeoAPI.point_validation import *




def splitFullAddress(dataframe: pd.DataFrame) -> pd.DataFrame: 
    """
    This function decomposes a string referring to the complete address into smaller parts.
    
    Parameters:
	----------
	dataframe: DataFrame
		dataframe containing a column with full address information
	
	Return:
	-------
	
	dispersion_df: DataFrame
        A new dataframe with new columns referring to the decomposition
        of this address, with street, number, city and state.
    
    """
  
    numbers = []
    cities = []
    states = []
    addresses = []
    for i in dataframe.iloc():
        addresses.append(i['end_completo'].split(",")[0])
        numbers.append(i['end_completo'].split(",")[1].strip())
        cities.append(i['end_completo'].split(",")[2].split("-")[0].strip())
        states.append(i['end_completo'].split(",")[2].split("-")[1].strip())

    dataframe['endereco'] = pd.Series(data=addresses, dtype='str')
    dataframe['numero'] = pd.Series(data=numbers, dtype='str')
    dataframe['cidade'] = pd.Series(data=cities, dtype='str')
    dataframe['estado'] = pd.Series(data=states, dtype='str')

    return dataframe

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function receives a dataframe, decomposes the complete address into smaller parts 
    and then this dataframe is submitted to a function that checks points outside the city's geometry.
    
    Parameters:
    ----------
    df: pd.DataFrame
        Dataframe with end_completo column

    Return:
    ------
    df: pd.DataFrame
        dataframe resulting from the transformation

    """

    df = splitFullAddress(df)
    df.cidade = df.cidade.apply(lambda x: x.lower())
    df = batch_outside_geometry_limits(df)
    return df

def plot_coordinates(df: pd.DataFrame):
    """
    This function will display a coordinate map of the geocoding process
    
    Parameters:
    -----------
    dataframe: pd.DataFrame:
        dataframe with coordinates of geocoding. 
    
    Return:
    ------
    Nothing

    """
    dataframe = df.copy()
    if type(dataframe) != gpd.GeoDataFrame:
        dataframe = convertToGeoFormat(dataframe)
    
    if "geometry" in dataframe.columns:
        dataframe['latitude'] = dataframe.geometry.y
        dataframe['longitude'] = dataframe.geometry.x

    fig = xp.scatter_mapbox(dataframe, lat = "latitude", lon = "longitude",
                         hover_data = ["end_completo"],
                        color_discrete_sequence = ["salmon"], zoom = 10, height = 1000)
    fig.update_layout(mapbox_style = "open-street-map")
    fig.update_layout(margin = {"r":0,"t":0,"l":0,"b":0})
    fig.show()



def visualizeOutsidePoints(df: pd.DataFrame):
    """
	This function receives a dataframe that will be used 
    to render the points that are or are not contained in the city's geometry.

	Parameters:
	----------
	df: DataFrame
		dataframe containing information whether the points are contained or not in the city's geometries
	
	Return:
	-------
	
	Nothing
	
    """
    dataframe = df.copy()
    if type(dataframe) != gpd.GeoDataFrame:
        dataframe = convertToGeoFormat(dataframe)
    
    if "geometry" in dataframe.columns:
        dataframe['latitude'] = dataframe.geometry.y
        dataframe['longitude'] = dataframe.geometry.x

    dataframe['outside'] = dataframe['outside'].apply(lambda x : "yes" if x == 1 else "no")
    fig = xp.scatter_mapbox(dataframe, lat = "latitude", lon = "longitude",
                        hover_name = "idcliente", hover_data = ["end_completo", "idcliente"],
                         zoom = 4, height = 1000, color="outside",
                         size_max=8, color_discrete_map={
                             "yes": "red",
                             "no": "blue",
                              
                         }, category_orders={"outside": ["yes", "no"]})
 
    fig.update_layout(mapbox_style = "open-street-map", coloraxis_showscale=False,
                    showlegend=True,
                    legend=dict(
                        traceorder="normal",
                        yanchor="top",
                        y=0.97,
                        font=dict(size=20)
                    ),
                    margin = {"r":0,"t":0,"l":0,"b":0},
                    
    )

    fig.show()
    
def visualizeByGeocodeService(df: pd.DataFrame):
    """
    This function receives a dataframe that contains several points referring 
    to different geocoding API's and will show these points differentiated by API.

    Parameters:
    ----------
    df: pd.DataFrame
        This dataframe needs a GeoAPI column to differentiate the points
    Return:
    ------

    Nothing
    """
    fig = go.Figure()

    dataframe = df.copy()
    if type(dataframe) != gpd.GeoDataFrame:
      dataframe = convertToGeoFormat(dataframe)
    
    color_map = ('#0000FF','#FF0000','#FFA500','#8B008B','#FF6F9C','#343a40','#008000')
    opaci_map = (0.80,0.80,0.85,0.80,0.85,0.75,0.70)

    i = 0
    fig = go.Figure()
    for api in dataframe.GeoAPI.unique():
        fig.add_trace(go.Scattermapbox(lat = dataframe.loc[dataframe['GeoAPI'] == api].geometry.y, 
                      lon = dataframe.loc[dataframe['GeoAPI'] == api].geometry.x, mode='markers+text', 
                      marker=dict(size=10, color = color_map[i], opacity = opaci_map[i]), 
                                       name=api, text=dataframe.loc[dataframe['GeoAPI'] == api].end_completo))
        i += 1

    fig.update_layout(
        mapbox = {
            'style':"open-street-map",
            'zoom': 4.2,
            'center': dict(
                lon=-51.92528,
                lat=-14.235004,
            )
        },
        legend = dict(
            font=dict(
                size = 20,
            ),
            y = 0.96,
            yanchor="top",
        )    
    )
    fig.update_layout(margin = {"r":0,"t":0,"l":0,"b":0})
    fig.show()

def get_worst_GeoAPI(dispersion_df, multi_sum):
    """
    This function is used in get_dispersion. It will get the API that has 
    the worst dispersion.

    Parameters:
    ----------
    dispersion_df: pd.DataFrame
        This dataframe containing the adreesses
    multi_sum: pd.DataFrame
        This dataframe containing latitudes and longitudes of each API for each address in dispersion_df

    Return:
    ------

    worst_api : list
        Return a list containing the worst api for each address
    """
    worst_api = []
    for end in dispersion_df.end_completo:
        y = multi_sum.xs(end).mean().values
        y = y.reshape(1, -1) 
        x = multi_sum.xs(end).values
        worst = multi_sum.index.get_level_values('GeoAPI').unique()[euclidean_distances(x,y).argmax()]
        worst_api.append(worst)
    return worst_api

def get_mean_per_end(dispersion_df, multi_sum) -> list:
    """
    This function will group the values ​​by address and calculate the average 
    of the latitudes and longitudes.
    
    Parameters:
    ----------
    dispersion_df: pd.DataFrame
        This dataframe containing the adreesses
    multi_sum: pd.DataFrame
        This dataframe containing latitudes and longitudes of each API for each address in dispersion_df
    Return:
    ------
    Two lists:
        mean of longitude and mean of latitude
    """
    lat_mean = []
    lon_mean = []
    for end in dispersion_df.end_completo:
        x = multi_sum.xs(end).longitude.mean()
        lon_mean.append(x)
        y = multi_sum.xs(end).latitude.mean()
        lat_mean.append(y)
    return lon_mean,lat_mean

def get_coord_per_end(dispersion_df: pd.DataFrame, multi_sum) -> list:
    """
    
    Parameters:
    -----------
    dispersion_df: DataFrame
        This dataframe containing the adreesses
    multi_sum: DataFrame
        This dataframe containing latitudes and longitudes of each API for each address in new_df
    Return:
    ------
    coord_per_end: list
        Return a list with a coordinate of each addres generated by each API
    """
    coord_per_end = []
    for end in dispersion_df.end_completo:
        x = [tuple(x) for x in multi_sum.xs(end).values]
        coord_per_end.append(x)
    return coord_per_end

def coord_to_radians(list_coord:list) -> list:
    """
    This function converts coordinates to radians.


    Parameters:
    ----------
    list_coord: list
        receive a list of coordinates.

    Return:
    ------
    list:
        returns a list of tuples containing coordinates in radians.
    """

    coord_in_radians = [tuple([radians(i[0]),radians(i[1])]) for i in list_coord]
    return coord_in_radians
    
def max_dist(coord_in_radians:list) -> float:
    """
    This function receives a list of coordinates in radians and will calculate the greatest distance
    from the midpoint of the coordinates using haversine distance.

    Parameters:
    ----------
    coord_in_radians: list
        coordinate list in radians.
    Return:
    -------
    float: returns a float number representing the greatest distance from the midpoint
    """
    const = 6371000/1000 
    max_dist = round(haversine_distances(coord_in_radians).max()*const,2)
    return max_dist

def get_dispersion(geocoded_data: pd.DataFrame, metrics: list) -> pd.DataFrame:
    """
    This function will do the scatter calculation based on a metric and 
    will return a new dataframe containing this information.
    
    Parameters:
    ----------
    geocoded_data: DataFrame

    metric: str
        dispersion metric that will be used

    Return:
    ------
    DataFrame:
        This function will be return a new dataframe with a new column "dispersion"
    """

    if len(metrics) < 1:
        raise Exception("it is necessary to inform at least one metric")


    
    geo_df = geocoded_data.copy()
    if type(geo_df) != gpd.GeoDataFrame:
      geo_df = convertToGeoFormat(geo_df)
    
    geo_df['longitude'] = geo_df.geometry.apply(lambda p: p.x)
    geo_df['latitude'] = geo_df.geometry.apply(lambda p: p.y)


    multi_sum = geo_df.groupby(['end_completo','GeoAPI'])[['longitude','latitude']].sum() #precisa mudar
    dispersion_df = pd.DataFrame()
    dispersion_df = dispersion_df.assign(end_completo = multi_sum.index.get_level_values('end_completo').unique())
    
    max_list = []
    
    lon,lat = get_mean_per_end(dispersion_df, multi_sum)
    worst_api = get_worst_GeoAPI(dispersion_df, multi_sum)
 
    dispersion_df.insert(0, "worst_api", worst_api, True)
    for disp_metric in metrics:
        if disp_metric == "DistanceFromMean":
            for coord in get_coord_per_end(dispersion_df, multi_sum):
                _max = max_dist(coord_to_radians(coord))
                max_list.append(_max)
        dispersion_df.insert(0, disp_metric, max_list, True)
    
  
    
    dispersion_df.insert(0, "longitude", lon, True)
    dispersion_df.insert(0, "latitude", lat, True)
    
    return dispersion_df
    

def visualizeDispersionGeo(dispersion_df):
    """
    Renders a map containing geographic points and information associated with them, 
    such as: full address, the result of a dispersion based on a metric and 
    which geoapi obtained the worst result in relation to the dispersion value.
    
    Parameters:
    ----------
    dispersion_df

    Return:
    -------
    This function will render a map on https://127.0.0.1
    """
    fig = xp.scatter_mapbox(dispersion_df, lat = "latitude", lon = "longitude",
                        hover_data = ["end_completo", "worst_api", "DistanceFromMean"],
                        zoom = 4, height = 1000, color="DistanceFromMean",
                        size_max=15,  color_continuous_scale="rainbow")
 
    fig.update_layout(mapbox_style = "open-street-map", showlegend=True,
                  margin = {"r":0,"t":0,"l":0,"b":0},
                  legend=dict(yanchor="top",y=0.97,))

    fig.show()

def visualize_dispersion(dispersion_df, metric : str ="DistanceFromMean"):
    """
    It will plot a map with a point for each address, this point will have the worst dispersion and the API that 
    obtained the worst dispersion.
    
    Parameters:
    ----------
    new_df: DataFrame

    Return:
    ------
    Nothing
    """
    app = dash.Dash()
    app.layout = html.Div([
        dcc.Graph(id="scatter-plot"),
        html.P("Distancia entre APIs:"),
        dcc.RangeSlider(
            id='range-slider',
            min=0, max=1000, step=0.1,
            marks={0: '0', 1000: '1000'},
            value=[0, 1000]),
        
    ])

    @app.callback(
        Output("scatter-plot", "figure"), 
        [Input("range-slider", "value")])
    
    def update_bar_chart(slider_range):
        low, high = slider_range
        filter1 = dispersion_df[metric] < high
        filter2 = dispersion_df[metric] > low
        clean_df = dispersion_df.where(filter1&filter2)

        fig = xp.scatter_mapbox(clean_df, lat = "latitude", lon = "longitude",
                                hover_name = "end_completo", hover_data = ['end_completo','worst_api'],
                                zoom = 4, height = 600, color="{}".format(metric),
                                size_max=10,color_continuous_scale='rainbow')

        fig.update_traces(marker=dict(size=8),
                        selector=dict(mode='markers'))

        fig.update_layout(mapbox_style = "open-street-map",
                            showlegend=True,
                            legend=dict(
                                yanchor="top",
                                y=0.97,
                            ),
                            margin = {"r":0,"t":0,"l":0,"b":0})
        
    
        return fig

    app.run_server(debug=True, use_reloader=False) 



geo = pd.read_csv("data2.csv")

# points_list = [
#     (-42.87076771266466, -20.76023241856432), 
#     (-42.859527304490385, -20.649620625804907),
#     (-49.17239,-25.58285),
#     (-49.21087,-25.5415),
#     (-42.800432680590276, -20.856010589809234),
#     (-49.21211, -25.56489),
#     (-48.697006, -26.890906), 

# ]
# result = outside_geometry_limits(points_list,
#  			state="MG", city = ["viçosa", "teixeiras", "coimbra", "juiz de fora"])
 
# print(result)
# print("\n")

# dispersion_df = get_dispersion(geo, metrics=["DistanceFromMean"])
# print(dispersion_df)
visualizeByGeocodeService(geo)

# geo = splitFullAddress(geo)
# geo = batch_outside_geometry_limits(geo)
# print(type(geo))
# print(geo)

# visualizeOutsidePoints(geo)
# visualize_dispersion(dispersion_df)
