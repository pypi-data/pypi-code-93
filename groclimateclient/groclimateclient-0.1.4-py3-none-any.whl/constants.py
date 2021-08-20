"""Constants about the climate-related Gro Ontology entity ids. """

REGION_LEVELS = {
    'world': 1,
    'continent': 2,
    'country': 3,
    'province': 4,  # Equivalent to state in the United States
    'district': 5,  # Equivalent to county in the United States
    'city': 6,
    'market': 7,
    'other': 8,
    'coordinate': 9
}

CLIMATE_ITEMS_STR = """item_id	name
9126	Bulk density (fine earth) at 100 cm deep
9123	Bulk density (fine earth) at 15 cm deep
9127	Bulk density (fine earth) at 200 cm deep
9124	Bulk density (fine earth) at 30 cm deep
9122	Bulk density (fine earth) at 5 cm deep
9125	Bulk density (fine earth) at 60 cm deep
9121	Bulk density (fine earth) at the surface
9133	Cation exchange capacity at 100 cm deep
9130	Cation exchange capacity at 15 cm deep
9134	Cation exchange capacity at 200 cm deep
9131	Cation exchange capacity at 30 cm deep
9129	Cation exchange capacity at 5 cm deep
9132	Cation exchange capacity at 60 cm deep
9128	Cation exchange capacity at the surface
9140	Clay content at 100 cm deep
9137	Clay content at 15 cm deep
9141	Clay content at 200 cm deep
9138	Clay content at 30 cm deep
9136	Clay content at 5 cm deep
9139	Clay content at 60 cm deep
9135	Clay content at the surface
9147	Coarse fragments at 100 cm deep
9144	Coarse fragments at 15 cm deep
9148	Coarse fragments at 200 cm deep
9145	Coarse fragments at 30 cm deep
9143	Coarse fragments at 5 cm deep
9146	Coarse fragments at 60 cm deep
9142	Coarse fragments at the surface
17388	Drought
8834	Drought vulnerable land
8937	ET on cropland
5073	ET/PET
4395	Evapotranspiration
9166	In H₂O at 100 cm deep
9163	In H₂O at 15 cm deep
9167	In H₂O at 200 cm deep
9164	In H₂O at 30 cm deep
9162	In H₂O at 5 cm deep
9165	In H₂O at 60 cm deep
9161	In H₂O at the surface
9173	In KCl at 100 cm deep
9170	In KCl at 15 cm deep
9174	In KCl at 200 cm deep
9171	In KCl at 30 cm deep
9169	In KCl at 5 cm deep
9172	In KCl at 60 cm deep
9168	In KCl at the surface
10041	Land
3457	Land temperature (daytime)
14924	NDVI on corn, area-weighted
8936	NDVI on cropland
16496	NDVI on soy, area-weighted
21532	NDVI on spring wheat, area-weighted
20681	NDVI on winter wheat, area-weighted
9117	Saturated water content at 100 cm deep
9114	Saturated water content at 15 cm deep
9118	Saturated water content at 200 cm deep
9115	Saturated water content at 30 cm deep
9113	Saturated water content at 5 cm deep
9116	Saturated water content at 60 cm deep
9112	Saturated water content at the surface
9180	Silt content at 100 cm deep
9177	Silt content at 15 cm deep
9181	Silt content at 200 cm deep
9178	Silt content at 30 cm deep
9176	Silt content at 5 cm deep
9179	Silt content at 60 cm deep
9175	Silt content at the surface
5113	Snow depth
5112	Snowfall
7382	Soil moisture
8938	Soil moisture on cropland
9159	Soil organic carbon content (fine earth fraction) at 100 cm deep
9156	Soil organic carbon content (fine earth fraction) at 15 cm deep
9160	Soil organic carbon content (fine earth fraction) at 200 cm deep
9157	Soil organic carbon content (fine earth fraction) at 30 cm deep
9155	Soil organic carbon content (fine earth fraction) at 5 cm deep
9158	Soil organic carbon content (fine earth fraction) at 60 cm deep
9154	Soil organic carbon content (fine earth fraction) at the surface
8827	Soil organic carbon stock from 0 to 100 cm deep
8828	Soil organic carbon stock from 0 to 150 cm deep
8825	Soil organic carbon stock from 0 to 20 cm deep
8826	Soil organic carbon stock from 0 to 30 cm deep
8819	Soil organic carbon stock from 0 to 5 cm deep
8823	Soil organic carbon stock from 100 to 150 cm deep
9153	Soil organic carbon stock from 100 to 200 cm deep
9150	Soil organic carbon stock from 15 to 30 cm deep
8821	Soil organic carbon stock from 20 to 50 cm deep
9151	Soil organic carbon stock from 30 to 60 cm deep
8822	Soil organic carbon stock from 50 to 100 cm deep
9149	Soil organic carbon stock from 5 to 15 cm deep
8820	Soil organic carbon stock from 5 to 20 cm deep
9152	Soil organic carbon stock from 60 to 100 cm deep
8824	Soil organic carbon stock greater than 150 cm deep
8829	Soil organic carbon stock in the total soil profile
9194	Soil water capacity until wilting point at 100 cm deep
9191	Soil water capacity until wilting point at 15 cm deep
9195	Soil water capacity until wilting point at 200 cm deep
9192	Soil water capacity until wilting point at 30 cm deep
9190	Soil water capacity until wilting point at 5 cm deep
9193	Soil water capacity until wilting point at 60 cm deep
9189	Soil water capacity until wilting point at the surface
9096	Soil water capacity with FC = pF 2.0 at 100 cm deep
9093	Soil water capacity with FC = pF 2.0 at 15 cm deep
9097	Soil water capacity with FC = pF 2.0 at 200 cm deep
9094	Soil water capacity with FC = pF 2.0 at 30 cm deep
9092	Soil water capacity with FC = pF 2.0 at 5 cm deep
9095	Soil water capacity with FC = pF 2.0 at 60 cm deep
9091	Soil water capacity with FC = pF 2.0 at the surface
9103	Soil water capacity with FC = pF 2.3 at 100 cm deep
9100	Soil water capacity with FC = pF 2.3 at 15 cm deep
9104	Soil water capacity with FC = pF 2.3 at 200 cm deep
9101	Soil water capacity with FC = pF 2.3 at 30 cm deep
9099	Soil water capacity with FC = pF 2.3 at 5 cm deep
9102	Soil water capacity with FC = pF 2.3 at 60 cm deep
9098	Soil water capacity with FC = pF 2.3 at the surface
9110	Soil water capacity with FC = pF 2.5 at 100 cm deep
9107	Soil water capacity with FC = pF 2.5 at 15 cm deep
9111	Soil water capacity with FC = pF 2.5 at 200 cm deep
9108	Soil water capacity with FC = pF 2.5 at 30 cm deep
9106	Soil water capacity with FC = pF 2.5 at 5 cm deep
9109	Soil water capacity with FC = pF 2.5 at 60 cm deep
9105	Soil water capacity with FC = pF 2.5 at the surface
8816	Soil water storage from 0 to 100 cm deep
8817	Soil water storage from 0 to 150 cm deep
8814	Soil water storage from 0 to 20 cm deep
8815	Soil water storage from 0 to 30 cm deep
8808	Soil water storage from 0 to 5 cm deep
8812	Soil water storage from 100 to 150 cm deep
8810	Soil water storage from 20 to 50 cm deep
8811	Soil water storage from 50 to 100 cm deep
8809	Soil water storage from 5 to 20 cm deep
8813	Soil water storage greater than 150 cm deep
8832	Soil water storage in the root zone
8818	Soil water storage in the total soil profile
321	Vegetation (NDVI)
7828	Water areas""".split('\n')[1:]
CLIMATE_ITEMS = {int(line.split('\t')[0]): line.split('\t')[1] for line in CLIMATE_ITEMS_STR}

CLIMATE_METRICS_STR = """metric_id	name
15852116	Aspect
15852972	Atmospheric Greenhouse Gas Concentration
15852973	Atmospheric Greenhouse Gas Concentration, Seasonally Corrected
15531092	Availability in soil (amount of substance)
15530031	Availability in soil (length)
15530037	Availability in soil (mass/area)
15531050	Availability in soil (mass/mass)
15531082	Availability in soil (volume/volume)
15741072	Density
15550031	Depth
5750029	Drought indicator (index)
5750042	Drought indicator (percent)
15852252	Drought Severity and Coverage Index
15851800	Elevation
15851977	El Niño Southern Oscillation Index
15852239	Evapotranspiration difference from 10-yr median (2003-2013)
4660031	Evapotranspiration Value
15851986	Humidity
2120042	Land Cover (percent)
15853048	Occurrence
15760040	pH
2100131	Precipitation 10-yr mean (2001-2010)
2100132	Precipitation 10-yr trailing mean
2100133	Precipitation 5-yr trailing mean
2110131	Precipitation difference from 10-yr mean (2001-2010)
2110132	Precipitation difference from 10-yr trailing mean
2110133	Precipitation difference from 5-yr trailing mean
2100031	Precipitation Quantity
15853046	Recurrence
15853045	Seasonality
15852115	Slope
3140031	Snow Depth
15560042	Soil Landscapes
2540047	Temperature
15852217	Temperature 10-yr mean (2001-2010)
15852220	Temperature difference from 10-yr mean (2001-2010)
15750042	Texture
15852181	Time Length
15852978	Variation of Precipitation
15852979	Variation of Precipitation Difference from 10-yr Mean
15852976	Variation of Temperature
15852977	Variation of Temperature Difference from 10-yr Mean
70029	Vegetation Indices
430132	Vegetation Indices 10-yr mean (2001-2010)
430131	Vegetation Indices 10-yr trailing mean
430130	Vegetation Indices 5-yr trailing mean
431132	Vegetation Indices difference from 10-yr mean (2001-2010)
431131	Vegetation Indices difference from 10-yr trailing mean
431130	Vegetation Indices difference from 5-yr trailing mean
15852329	Volatility-adjusted YOY Change, Retail Prices by Count (percent)
15852328	Volatility-adjusted YOY Change, Retail Prices by Mass (percent)
15852331	Volatility-adjusted YOY Change, Wholesale Prices by Count (percent)
15852330	Volatility-adjusted YOY Change, Wholesale Prices by Mass (percent)""".split('\n')[1:]
CLIMATE_METRICS = {int(line.split('\t')[0]): line.split('\t')[1] for line in CLIMATE_METRICS_STR}

CLIMATE_SOURCES = [3,20,22,26,35,43,44,78,80,82,87,89,97,105,112,124,126,133,145,150,152,163,167,172,192,190,189,191,178,187,188]
CMIP6_SOURCES = [178, 189, 190, 191, 192]

