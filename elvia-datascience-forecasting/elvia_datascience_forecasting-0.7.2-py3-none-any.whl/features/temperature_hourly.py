from pandas import DataFrame, to_datetime, concat
import requests
import time
from ..errors import WeatherIngestRequestTimeout, RequestFailed
from ..enums import Weather
from .. import PACKAGE_NAME, __version__

def temperature_hourly(df,
                       weather_variable: str,
                       start_date: str,
                       end_date: str,
                       inference: bool = False,
                       weather_token_id: str = '') -> DataFrame:
    """
    This function loads the weather data for a specific substation for a given start_date & end_date and latitude & longitude. 

    # Parameters
    --------------
    df              : Pandas dataframe
    weather_variable: Refers to which weather variable we use. Here it is 'temperature'.
    start_date      : The day the temperature readings are started to be taken
    end_date        : The day the temperature readings are ended to be taken
    weather_token_id: Token ID for accesing Weather API

    # Returns:
    --------------
    A dataframe with temperature and related substation ID variables with the index of datetime.
    """
    token = weather_token_id

    dataframe_list = []
    # Looping in substaions and getting temperature values from the Weather API. Then save it as a dataframe to dataframe_list
    for station in df['trafo_id'].unique():
        # latitude and longitude of each trafo
        longitude = df.loc[df['trafo_id'] == station]['long'][0]
        latitude = df.loc[df['trafo_id'] == station]['lat'][0]

        # Loads data for the respective weather variable
        input_data = {
            "startTime": start_date,
            "endTime": end_date,
            "coordinates": [{
                "latitude": latitude,
                "longitude": longitude
            }],
            "variables": [weather_variable]
        }

        # Access token and the media type of body sent to the API
        headers = {
            'Content-Type': 'application/json-patch+json',
            'Ocp-Apim-Subscription-Key': token
        }
        # Requesting data based on the input_data from the weather API
        r = requests.post(Weather.ENDPOINT_HST, json=input_data, headers=headers)

        # If it fails, let's try again 5 timeds, with a pause of 2s btw tries
        if r.status_code != 200:
            inc=0
            while r.status_code != 200 & inc<5:
                inc=inc+1
                time.sleep(2)
                r = requests.post(Weather.ENDPOINT_HST, json=input_data, headers=headers)
            # if we come out of the while and it is still not 200, then raise an error
            if r.status_code != 200:
                raise WeatherIngestRequestTimeout
        
        # Read the JSON response
        weather_data_json = r.json()
        weather_data_temp = weather_data_json['coordinates'][0]['variables'][
            0]['data']
        # Make it a DataFrame
        weather_data_df = DataFrame.from_records(
            weather_data_temp)

        # Convert to datetime object and set as index 
        weather_data_df['time'] = to_datetime(weather_data_df['time'], utc=True)
        weather_data_df = weather_data_df.set_index('time')
        
        # Name the column 
        weather_data_df.rename(columns={'value': weather_variable},
                               inplace=True)
        
        # Add the trafo_id to assign the temparature to a trafo
        weather_data_df['trafo_id'] = station
        
        # If we are doing inference, we need the forecast for the next hours
        # Doing this under here
        if inference:
            # Creating the header
            headers_fcst = {
                'user-agent': f'{PACKAGE_NAME}/{__version__}'
            }
            fcst_r = requests.get(
                f'{Weather.ENDPOINT_FCST}?lat={latitude}&lon={longitude}',
                headers=headers_fcst)
            if fcst_r.status_code != 200:
                raise RequestFailed

            # Read the JSON response
            fcst_data_json = fcst_r.json()

            # Fetch dates and variables in the JSON file
            if weather_variable=='temperature':
                weather_var_fcst = 'air_temperature'
            time_fcst = [d['time'] for d in fcst_data_json['properties']['timeseries']]
            time_fcst_dt = to_datetime(time_fcst,utc=True)
            temp_fcst = [d['data']['instant']['details'][weather_var_fcst] for d in fcst_data_json['properties']['timeseries']]

            # Create a DataFrame with the data
            fcst_df = DataFrame(index = time_fcst_dt, data = temp_fcst, columns=[weather_variable])
            fcst_df['trafo_id'] = station

            # Convert temperature from Celsius to Kelvin
            fcst_df['temperature'] = fcst_df['temperature'] + 273.15

            # Concat the history and the forecast
            weather_data_df = concat([weather_data_df, fcst_df])
        
        # Append to the others trafos
        dataframe_list.append(weather_data_df)

    # concatenating all dataframes from all trafos    
    all_weather_data_df = concat(
        dataframe_list)  
    
    # Cleaning and changing type
    all_weather_data_df = all_weather_data_df.rename_axis('time').reset_index(drop=False)
    all_weather_data_df['temperature'] = all_weather_data_df[
        'temperature'].astype('float32')

    return all_weather_data_df
