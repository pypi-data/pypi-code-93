
import os
import sys
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import requests
from unidecode import unidecode
import json
from shapely.geometry import Point

sys.path.append("../..")


from pkg_resources import resource_filename


def convertToGeoFormat(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    This function transforms a dataframe into a geodataframe using the geometry column.

    Parameters:
    ----------
    df: DataFrame
        dataframe that will be converted

    Errors:
    ------
    RuntimeError: if the dataframe does not have the geometry column
    Return:
    -------
    dispersion_df: gpd.GeoDataFrame
        dataframe resulting from conversion
    """
    
    if "geometry" in df.columns:
        df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])
        new_df = gpd.GeoDataFrame(df, geometry="geometry")
    else:
        raise RuntimeError("The dataframe needs a column named geometry")
    if "Unnamed: 0" in new_df.columns:
        new_df = new_df.drop(columns=["Unnamed: 0"], axis=1)
  
    
    return new_df

def state_map(state: str):
	"""
	This function maps the states reported as an abbreviation to the full state name.

	Parameters:
	----------
	state: str
		State abbreviation. Example: MG, SP, GO, MS
	Return:
	-------
	str: 
		Full name of state. Example: Minas Gerais, São Paulo, Goiás...
	"""

	states = {
		'AC': 'Acre',
		'AL': 'Alagoas',
		'AP': 'Amapá',
		'AM': 'Amazonas',
		'BA': 'Bahia',
		'CE': 'Ceará',
		'DF': 'Distrito Federal',
		'ES': 'Espírito Santo',
		'GO': 'Goiás',
		'MA': 'Maranhão',
		'MT': 'Mato Grosso',
		'MS': 'Mato Grosso do Sul',
		'MG': 'Minas Gerais',
		'PA': 'Pará',
		'PB': 'Paraíba',
		'PR': 'Paraná',
		'PE': 'Pernambuco',
		'PI': 'Piauí',
		'RJ': 'Rio de Janeiro',
		'RN': 'Rio Grande do Norte',
		'RS': 'Rio Grande do Sul',
		'RO': 'Rondônia',
		'RR': 'Roraima',
		'SC': 'Santa Catarina',
		'SP': 'São Paulo',

		'SE': 'Sergipe',
		'TO': 'Tocantins'
	}
	
	value = states.get(state)
	if value == None:
		raise KeyError("Do not possible find the state key")
	else:
		return unidecode(states[state].lower())


def getCityCode(state: str, city: str) -> int:
	"""
	
	This function will obtain the code of a city from an IBGE city code table. 
	This search is made through the city and its respective state.

	Parameters:
	----------
	state: str
		brazilian state.
	city: str
		city ​​of state informed.

	Return:
	------
	int:
		city code.

	"""
	codes_path = Path(__file__).parent.resolve()
	codes_path = Path.joinpath(codes_path, "relatorio.xls")

	city_codes = pd.read_excel(resource_filename('GeoAPI','Data/relatorio.xls'))

	
	
	state = unidecode(state.lower())
	city = unidecode(city.lower())
	
	if len(state) == 2:		
		state = state_map(state.upper())
		
	
	codes = city_codes.filter(items=['Nome_UF', 'Código Município Completo'
					, 'Nome_Município'])

	codes['Nome_UF'] = codes['Nome_UF'].apply(lambda x : unidecode(x.lower()))
	codes['Nome_Município'] = codes['Nome_Município'].apply(lambda x : unidecode(x.lower()))
		
	codes = codes.loc[((codes['Nome_UF'] == state) & 
							(codes['Nome_Município'] == city)), 'Código Município Completo']
	
	if codes.empty:
		return -1
	else:
		return codes.item()

def getCityLimits(city_code: int, year: int = 2020) -> json:
	
	"""
	This function receives the city code and from it, a request is made to get the city limits.

	Parameters:
	----------
	city_code: int
		code associated with the searched city.
	year: int
		period in which city limits will be obtained.
	Return:
	-------
	
	json:
		returns a json containing the city's geometry
	"""
	END_POINT = 'http://servicodados.ibge.gov.br/api/v3/malhas/municipios/'
		
	try:
		city = requests.get(END_POINT +
		 	'{}?formato=application/vnd.geo+json&qualidade=maxima&periodo={}'.format(
			 	city_code, year
		))		
		if city.status_code == 200:
			request_json = city.json()	
			return request_json
		else:
			return None
	except requests.exceptions.HTTPError as err:
		raise SystemExit(err)
	except requests.exceptions.Timeout:
		raise SystemExit()
		
			
def isContained(longitude: float, latitude: float, city_limits: gpd.GeoDataFrame) -> bool:
	"""
	This function checks whether a point is contained in certain geometry.
	
	
	Parameters:
	----------
	longitude: int
		longitude coordinate.
	latitude: int
		latitude coordinate.
	city_limits: QgsVectorLayer
		vector layer of city limits

	Return:
	-------
	bool:
		The function returns true if the point is contained in the geometry of the city.
		Otherwise, return false.
	"""
	point = Point(longitude, latitude)
	
	if city_limits.contains(point).bool():
		return True
	else:
		return False

def contains(state:str, city: str, longitude: float, latitude: float) -> bool:
	"""
	This function is responsible for performing the entire
	verification process to determine if a point is contained in a geometry.

	Parameters:
	----------
	state: str
		brazilian state.
	city: str
		city ​​of state informed.
	longitude: int
		longitude coordinate.
	latitude: int
		latitude coordinate.

	Return:
	-------
	
	bool:
		The function returns true if the point is contained within a city boundary.
		Otherwise, return false.
	"""
	city_code = getCityCode(state, city)
	
	if city_code != -1:
		if not isFileExists(city):
			city_limits = getCityLimits(city_code)
			save(city_limits, city)
			layer = load(city, "gpd")
			if isContained(longitude, latitude, layer):
				return True
			else:
				return False
		else:
			layer = load(city, "gpd")
			
			if isContained(longitude, latitude, layer):
				return True
			else:
				return False

	


def save(city_limits: json, city_name: str, directory_path: str = "Data/ibge/"):
	"""
	This function will be save the IBGE files, 
	which concern the limits of a certain city. '

	Parameters:
	-----------
	city_limits: json
		response to the request to IBGE
	city_name: str
		name of geojson file.
	directory_path: str
		path to save json. 
	"""
	try:
		os.makedirs(directory_path, exist_ok = True)
	except OSError as error:
		raise SystemError()
	
	with open(directory_path+ '{}_ibge.geojson'.format(city_name.lower()), 'w') as f:
			json.dump(city_limits, f)



def load(city_name: str, return_type: str, directory_path: str = 'Data/ibge/'):
	"""
	This function will load a geojson referring to the boundaries of a municipality
	and from a return type it returns an object. 

	Parameters:
	----------
	city_name: str 
		symbolizes the name of the file to be searched.
	return_type: str  
		the return type will tell if the method will return a qgis vector layer 
				or a geo dataframe.
	directory_path: str
		path to load a json.

	Returns:
	--------
	QgsVectorLayer: 
		returns the geojson of the city entered in vector layer format.
	GeoDataFrame:
		returns the geojson of the city entered in GeoDataFrame format. 
	"""
	
	if unidecode(return_type.lower()) == "qgis":
		pass
		#return QgsVectorLayer(directory_path+'{}_ibge.geojson'.format(city_name),
		 #			'{}'.format(city_name), 'ogr')

	elif unidecode(return_type.lower()) == "gpd":
		return gpd.read_file(directory_path
							+'{}_ibge.geojson'.format(city_name.lower()))

def isFileExists(city_name:str, directory_path: str = "Data/ibge/") -> bool:
	"""
	This function checks if a file already exists in a specific directory.

	Parameters:
	-----------
	city_name: str
		Files are saved by city name.
	directory_path: str
		Directory where these files were saved.
	
	Return:
	------
	bool: 
		True -> if file exists
		False -> otherwise
	"""
	if os.path.exists(directory_path
						+"{}_ibge.geojson".format(city_name.lower())):
		return True
	else:
		return False
		
def renderCityLimits(city:str):
	"""
	This function will display a graph representing the boundaries of a particular city.

	Parameters:
	----------
	city: string
		the city we want to show.

	"""
	city_limits = load(city, "gpd")	
	city_limits.plot()
	plt.show()	

def outside_geometry_limits(points : list, state: str, city = []) -> pd.DataFrame:
	"""
	This function will analyze if a certain point is contained
	in one of the cities present in the list of cities.


	Parameters:
	-----------
	latitude: float
		latitude coordinate
	longitude: float
		longitude coordinate
	state: str
		Brazilian state
	city: list
		list of cities to check

	Return:
	-------
	DataFrame:
		This dataframe will contain the answer if a certain point is contained for a list of cities.
	
	"""
	index = city
	
	dataframe = pd.DataFrame(columns=['latitude', 'longitude', 'estado', 'outside'])	
	
	if len(city) < 1:
		raise Exception("it is necessary to inform at least one city") 
	if len(city) == 1:
		city = city[0]
	

	lines = []
	for city in index:
		for point in points:
			if contains(state=state, city=city, longitude=point[0],latitude=point[1]):				
				line = pd.DataFrame([{"latitude" : point[1], "longitude": point[0],
					"estado": state, "outside": 0,}], index=[city])
				
				lines.append(line)
			else:
				line = pd.DataFrame([{"latitude" : point[1], "longitude": point[0],
					"estado": state, "outside": 1,}], index=[city])
				
				lines.append(line)
				
	for i in lines:
		dataframe = dataframe.append(i, ignore_index=False)


	dataframe = dataframe.reset_index().rename(columns={"index": "cidade"})

	dataframe = dataframe.groupby(by=["cidade", "estado" ]).apply(lambda x: x.sort_index())

	dataframe.index = dataframe.index.droplevel(-1)
	
	dataframe.drop(columns=["cidade", "estado"], axis=1, inplace=True)
	
	
	
	return dataframe
	
def batch_outside_geometry_limits(geocoded_df: pd.DataFrame):		
	"""
	This function checks if a set of points is contained within the limits of a city, 
	creating a column that is responsible for symbolizing which ones are inside or outside the limits.
	
	Parameters:
	-----------
	
	geocoded_df: DataFrame 
		a set of geocoded points that will be tested
	
	Return:
	------
	GeoDataFrame:
		The return is a GeoDataFrame with the marking of points that are outside the city limits.
	"""

	outside = []

	df = geocoded_df.copy()
    
	if type(df) != gpd.GeoDataFrame:
		df = convertToGeoFormat(df)
	
	if "geometry" in df.columns:
		for row in df.itertuples():
			if contains(row.estado, row.cidade, row.geometry.x, row.geometry.y):
				outside.append(0)
			else:
				outside.append(1)
	elif (("latitude" in df.columns) & ("longitude" in df.columns)):
		for row in df.itertuples():
			if contains(row.estado, row.cidade, longitude = row.longitude, latitude=row.latitude):
				outside.append(0)
			else:
				outside.append(1)

			
	df = df.assign(outside = outside)
	#geocoded_df.insert(0, "outside", outside, True)
	return df




