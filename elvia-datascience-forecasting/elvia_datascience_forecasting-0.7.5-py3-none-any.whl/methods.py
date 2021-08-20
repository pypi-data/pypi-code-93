from azureml.core import Dataset  # type: ignore
from datetime import timedelta, datetime
import inspect
import logging
from logging import Logger
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from types import FrameType
from typing import cast, Optional, Union

from forecast_dataprep.data_models import EndpointRequest
from forecast_dataprep.errors import NotEnoughDataError, UnspecifiedTimeSpanError, DataNotFound
from forecast_dataprep.logs import LogEntry
from forecast_dataprep.features.add_metadata import add_metadata
from forecast_dataprep.features.dayofweek import dayofweek
from forecast_dataprep.features.hourofday import hourofday
from forecast_dataprep.features.monthyear import monthyear
from forecast_dataprep.features.hourofweek import hourofweek
from forecast_dataprep.features.school_holiday import school_holiday
from forecast_dataprep.features.national_holiday import national_holiday
from forecast_dataprep.features.temperature_hourly import temperature_hourly
from forecast_dataprep.features.average_weekly_data import average_weekly_data
from forecast_dataprep.features.shifted_hourly_load import shifted_hourly_load
from forecast_dataprep.features.sin_cos_cyclical_feature import sin_cos_transformation
from forecast_dataprep.enums import Features


def ingest_data(  # NOSONAR
        hist_cons_dataset: Dataset,  # NOSONAR
        metadata_dataset: Dataset,
        hist_cons_start: datetime = None,
        hist_cons_end: datetime = None,
        percentage: float = 0.9,
        inference: bool = False,
        forecast_horizon: int = 67,
        outliers_exclusion: int = 5,
        logger: Optional[Logger] = None,
        endpoint_request: Optional[EndpointRequest] = None) -> pd.DataFrame:
    '''
    This function takes in Azure energy consumption dataset and its Azure metadata dataset. Substation Ids in the Azure energy consumption dataset
    will be renamed by using Driftsmerking name in the Azure metadata dataset. 

    # Parameters
    --------------
    hist_cons_dataset : Azure energy consumption dataset
    metadata_dataset   : Energy consumption Azure metadata dataset
    hist_cons_start    : First data point requested to the database for the energy consumption data (datetime)
    hist_cons_end      : Last data point requested to the database for the energy consumption data (datetime)
    percentage    : Percentage that is used to select the appropriate transformers
    time_zone     : Substation data comes with timezone UTC. It can be set to Oslo-timezone by writing 'time_zone = True'
    inference    : If this function is used in inference, it should be set as 'True', otherwise 'False'
    logger        : Logger object, optional
    endpoint_request : Argument to be used together with loggers of type LogEntry, optional

    # Returns
    --------------
    A pandas dataframe with the transformers that has rows greater than determined percentage(90%) of the number of hours in the selected date range

    :raises UnspecifiedTimeSpanError: hist_cons_start and hist_cons_end were needed, but at least one of them was unspecified
    :raises NotEnoughDataError: Not enough data  
    :raises DataNotFound: Excpected variables were not found   
    '''

    # Logger init
    log_counter: int = 0

    # From Azure dataset to Pandas dataframe
    hist_cons_df: pd.DataFrame = hist_cons_dataset.to_pandas_dataframe()
    log_counter = add_debug_trace(
        f'Incoming historical consumption data size: {str(hist_cons_df.shape)}',
        logger, endpoint_request, log_counter)

    # Transform the datetime string to a Datetime object -> datetime64[ns, UTC]
    hist_cons_df['datetime_utc'] = pd.to_datetime(
        hist_cons_df['datetime_utc'], 
        infer_datetime_format=True,
        utc=True) 
    
    # Log the dtypes
    log_counter = add_debug_trace(
        f'Variable type after changing to datetime object: {hist_cons_df.dtypes.to_string()}', 
        logger, endpoint_request, log_counter)


    if inference:
        # Set datetime as index
        hist_cons_df = hist_cons_df.set_index('datetime_utc')
        ### Checking we got enough history to create the features
        # Necessary dates to have create the features
        for hist_feat in Features.SHIFT_HOURS:
            # Required hours to create this feature
            hours_req = pd.date_range(
                start=hist_cons_end-timedelta(hours=hist_feat), 
                end=hist_cons_end-timedelta(hours=hist_feat-forecast_horizon+1), 
                freq='H',
                tz='utc')
            
            # Interesection between required hours and existing hours 
            missing_hours = [hour_req for hour_req in hours_req if hour_req not in hist_cons_df.index]

            # Log the new size of the Dataframe
            if missing_hours:
                log_counter = add_debug_trace(
                    f'Feature consumption delayed {hist_feat} hours cannot be done fully. Missing {len(missing_hours)} hours:\n {str(missing_hours)}',
                    logger, endpoint_request, log_counter)
            else:
                log_counter = add_debug_trace(
                    f'Feature consumption delayed {hist_feat} hours can be done fully',
                    logger, endpoint_request, log_counter)

        ### Adding forecast_horizon hours to the index by shifting the existing index of forecast_horizon steps
        # We will add dates with null consumption also in history if we didn't fetch any data from the database
        minimum_hour = min(
            hist_cons_df.index[-1].replace(tzinfo=None),
            hist_cons_end.replace(tzinfo=None)
            )
        # Create an Empty Dataframe with indexes covering the missing historical value and the next 67 hours
        inference_df = pd.DataFrame(
            index=pd.date_range(
                start=minimum_hour,
                end=hist_cons_end+timedelta(hours=forecast_horizon-1), 
                freq='H',
                tz='utc'),
            columns=['trafo_id','value_wh']                    
        )
        # Append the new hours and set the index as a column again
        hist_cons_df = hist_cons_df.append(inference_df).rename_axis('datetime_utc').reset_index(drop=False)

        # Set the trafo_id to the value of the first entry
        hist_cons_df.loc[hist_cons_df['trafo_id'].isna(),'trafo_id'] = hist_cons_df['trafo_id'][0]

        # If any duplcations in the index, remove it by keeping the first (happens because of timezones...)
        hist_cons_df = hist_cons_df.drop_duplicates(['datetime_utc'],keep='first')

        # Log the new size of the Dataframe
        log_counter = add_debug_trace(
            f'Historical consumption data size after adding {forecast_horizon} hours for inference: {str(hist_cons_df.shape)}',
            logger, endpoint_request, log_counter)

    else:  # training part

        # check the input data
        df = _check_input_data(hist_cons_df,
                               percentage=0.1,
                               value_col='value_wh',
                               trafo_col='trafo_id',
                               len_history=len(hist_cons_df['datetime_utc'].unique()))

        log_counter = add_debug_trace(
            f'df after calling _check_input_data: {str(hist_cons_df.head().to_string())}',
            logger, endpoint_request, log_counter)

        # Keep columns that have more than 90% of the number of hours in the selected date range
        if not hist_cons_start or not hist_cons_end:
            raise UnspecifiedTimeSpanError

        date_range = hist_cons_end - hist_cons_start
        diff_hour = date_range.total_seconds(
        ) / 3600  # difference based on hour

        df_ranged = pd.DataFrame(columns=hist_cons_df.columns)
        for station_id in hist_cons_df['trafo_id'].unique():
            data_set = hist_cons_df.loc[hist_cons_df['trafo_id'] == station_id]
            if len(data_set) < diff_hour * percentage:
                continue
            df_ranged = df_ranged.append(data_set, ignore_index=True)
        hist_cons_df = df_ranged

        log_counter = add_debug_trace(
            f'hist_cons_df after selecting trafo with more than 90% of data: {str(hist_cons_df.head().to_string())}',
            logger, endpoint_request, log_counter)

        # Raise exception if the dataframe is empty
        if hist_cons_df.empty:
            log_counter = add_debug_trace(
                'NotEnoughDataError: DataFrame is empty', logger,
                endpoint_request, log_counter)
            raise NotEnoughDataError

        # Remove outliers
        for station_id in hist_cons_df['trafo_id'].unique():
            v = hist_cons_df.loc[hist_cons_df['trafo_id'] == station_id, 'value_wh']
            w = _remove_outliers(v, -outliers_exclusion, outliers_exclusion)
            hist_cons_df.loc[hist_cons_df['trafo_id'] == station_id, 'value_wh'] = w.values

        log_counter = add_debug_trace(
            f'df.shape after removing outliers: {str(hist_cons_df.shape)}', logger,
            endpoint_request, log_counter)
        log_counter = add_debug_trace(
            f'df.head() after removing outliers: {str(df.head().to_string())}',
            logger, endpoint_request, log_counter)

    ### Merging dataframe with substation metadata to add kommunenavn, latitude and longitude to the dataframe
    # From Azure dataset to Pandas dataframe
    df_metadata = metadata_dataset.to_pandas_dataframe()

    ### Redo this part -> find the substation lat lon and name based on the trafo name
    # First set trafo_id to Categorical to accelarate the process
    if 'trafo_id' in hist_cons_df.columns:
        hist_cons_df['trafo_id'] = hist_cons_df['trafo_id'].astype('category')
    else:
        log_counter = add_debug_trace(
                'DataNotFound: Could not find column trafo_id in hist_cons_df', logger,
                endpoint_request, log_counter)
        raise DataNotFound 
    # The logic is present in the function add_metadata and create the column substation_id
    hist_cons_df['substation_id'] = hist_cons_df['trafo_id'].apply(add_metadata, df_metadata=df_metadata)
    # Logging the step above
    trafo_ids_uni = hist_cons_df['trafo_id'].unique()
    station_ids_uni = [hist_cons_df.loc[hist_cons_df['trafo_id']==v,'value_wh'].unique() for v in trafo_ids_uni]
    log_counter = add_debug_trace(
        f'Unique trafo_ids {trafo_ids_uni} and station_ids {station_ids_uni}',
        logger, endpoint_request, log_counter)

    # Merge the metadata containing lat, lon and fylkesnavn to the historical consumption
    df_metadata.drop_duplicates(subset=['Driftsmerking'], inplace=True)
    hist_cons_df = hist_cons_df.merge(df_metadata,
                  left_on=['substation_id'],
                  right_on=['Driftsmerking'],
                  how='left')
    hist_cons_df.drop(['Driftsmerking'], axis=1, inplace=True)
    log_counter = add_debug_trace(
        f'First five rows after merging metadata: {str(hist_cons_df.head().to_string())}',
        logger, endpoint_request, log_counter)

    # Casting object type to columns
    hist_cons_df = _cast_type_df(hist_cons_df, log_counter, logger, endpoint_request)
    log_counter = add_debug_trace(
        f'Final DataFrame shape and columns: {str(hist_cons_df.shape)} \n {str(hist_cons_df.columns)}', 
        logger, endpoint_request, log_counter)

    return hist_cons_df


def enrich(
        df: pd.DataFrame,  # NOSONAR
        weekly_dataset: Dataset,
        holiday_path: str = '',
        token_weather: str = '',
        inference: bool = False,
        logger: Optional[Logger] = None,
        endpoint_request: Optional[EndpointRequest] = None) -> pd.DataFrame:
    """
    This function takes in substations load as dataframe(df) and adds new features to 
    the dataframe which will be used to build machine learning models

    :param pandas.DataFrame df: Dataframe of consumption data
    :param azureml.core.Dataset weekly_dataset: Weekly average cumsumption
    :param str holiday_path: The path to the json file that contains dates of national and school holidays
    :param str token_weather: Token for Weather API
    :param bool inference: If this function is used in inference step, it should be set as 'True'. Default False.
    :param logging.Logger logger: Logger object, optional
    :param forecast_dataprep.data_models.EndpointRequest endpoint_request: Object describing an HTTP request, optional
    :return: A pandas dataframe without index of 'datetime_utc' and feature of 'trafo'
    :rtype: pandas.DataFrame
    """

    # Logger init
    log_counter: int = 0

    # Check the incoming table size
    log_counter = add_debug_trace(
        f'Incoming df.shape: {str(df.shape)}',
        logger, endpoint_request, log_counter)

    # Set the datetime column as index
    df = df.set_index('datetime_utc')

    # Adding 72, 96 and 168 hours shifting
    for hour in Features.SHIFT_HOURS:
        df = shifted_hourly_load(df, t=hour)
    # Check the incoming table size
    log_counter = add_debug_trace(
        f'Shape after adding the historical features: {str(df.shape)}',
        logger, endpoint_request, log_counter)

    # Adding days of a week to dataframe
    df = dayofweek(df)
    log_counter = add_debug_trace(
        f'After applying dayofweek: {str(df.head().to_string())}', logger,
        endpoint_request, log_counter)

    # Adding hours of a day to dataframe
    df = hourofday(df)
    log_counter = add_debug_trace(
        f'After applying hourofday: {str(df.head().to_string())}', logger,
        endpoint_request, log_counter)

    # Adding hour of week to dataframe (0 - 167)
    df = hourofweek(df)
    log_counter = add_debug_trace(
        f'After applying hourofweek: {str(df.head().to_string())}', logger,
        endpoint_request, log_counter)

    # Adding month of a year to dataframe
    df = monthyear(df)
    log_counter = add_debug_trace(
        f'After applying monthyear: {str(df.head().to_string())}', logger,
        endpoint_request, log_counter)

    # we reset index before merging with average_weekly_data, otherwise we will lose 'datetime_utc' index
    df.reset_index(inplace=True)
    log_counter = add_debug_trace(
        f'After resetting the index: {str(df.head().to_string())}', logger,
        endpoint_request, log_counter)

    # Adding average_weekly_data to dataframe
    df_average_weekly = average_weekly_data(weekly_dataset)
    df = df.merge(df_average_weekly,
                  left_on=['hourofweek', 'trafo_id'],
                  right_on=['houroftheweek', 'trafo'],
                  how='left')
    df.drop(['houroftheweek', 'hourofweek','trafo'], axis=1, inplace=True)
    log_counter = add_debug_trace(
        f'After merging with df_average_weekly: {str(df.head().to_string())}',
        logger, endpoint_request, log_counter)

    df = df.set_index('datetime_utc')  # setting index again
    df['trafo_id'] = df['trafo_id'].astype('category')
    log_counter = add_debug_trace(
        f'After setting index and adding trafo: {str(df.head().to_string())}',
        logger, endpoint_request, log_counter)

    # Adding school holiday to dataframe
    df = school_holiday(df, path_holiday=holiday_path)
    log_counter = add_debug_trace(
        f'After applying school_holiday : {str(df.head().to_string())}',
        logger, endpoint_request, log_counter)

    df['school_holiday'] = df['school_holiday'].astype(
        'bool')  # casting type from object to boolean
    log_counter = add_debug_trace(
        f'After changing school_holiday dtype: {str(df.head().to_string())}',
        logger, endpoint_request, log_counter)

    # Adding national holiday to dataframe
    df_national_holiday = national_holiday(df, path_holiday=holiday_path)
    df = df.merge(df_national_holiday,
                  left_on=['datetime_utc'],
                  right_on=['datetime_utc'],
                  how='left')

    # Adding Weather data
    start_date = df.index[0].strftime(format='%Y-%m-%d')
    end_date = (df.index[-1] + timedelta(days=1)).strftime(format='%Y-%m-%d')
    df_weather = temperature_hourly(df,
                                    'temperature',
                                    start_date=start_date,
                                    end_date=end_date,
                                    inference=inference,
                                    weather_token_id=token_weather)
    # Reset index to merge dataframes based on index column and trafo column
    df.reset_index(drop=False, inplace=True)
    df = df.merge(df_weather,
                  left_on=['datetime_utc', 'trafo_id'],
                  right_on=['time', 'trafo_id'],
                  how='left')
    df['trafo_id'] = df['trafo_id'].astype('category')
    if inference:
        # Some of the latest hours of the forecast have only 6H resolution,
        # so we linearly interpolate between the 6H points. No extrapolation (limit_area).
        df['temperature'] = df['temperature'].interpolate(
            method='linear',
            limit_area='inside')

    # Sine and cosine transformation
    cyclical_features = [('hourofday', 23), ('dayofweek', 6),
                         ('monthyear', 12)]
    for col in cyclical_features:
        sin_cos_transformation(df, col[0], col[1])
        df.drop([col[0]], axis=1, inplace=True)

    # 
    log_counter = add_debug_trace(f'Shape of the DF before dropping unused columns : {str(df.shape)}', logger,
                                  endpoint_request, log_counter)
    df.drop(['time','substation_id', 'fylkesnavn', 'long', 'lat', 'kommunenavn', 'kommunenummer', 'fylkesnummer'],
            axis=1,
            inplace=True)
    if inference:
        # Drop the 3 cyclical features and other columns because we will not use them in ML model
        df.drop(['trafo_id'],
                axis=1,
                inplace=True)
        log_counter = add_debug_trace(f'Shape of the DF before dropping the NaN in the inference : {str(df.shape)}', logger,
                                  endpoint_request, log_counter)
        #df.dropna(inplace=True)

    # At this stage, we should have no NaN, NaT or similar
    #if df.isna().any():
    #    log_counter = add_debug_trace(f'Some NaN are still in the dataframe before ', logger,
    #                            endpoint_request, log_counter) 

    log_counter = add_debug_trace(f'Final df.shape : {str(df.shape)}', logger,
                                  endpoint_request, log_counter)

    return df


def _cast_type_df(
    df: pd.DataFrame, 
    log_counter: int,
    logger: Optional[Logger] = None,
    endpoint_request: Optional[EndpointRequest] = None
    ):

    '''
    Casting to right variable type columns of the DataFrame

    '''
    # Transform trafo_id column to category if existing, raise if not
    if 'value_wh' in df.columns:
        df['value_wh'] = df['value_wh'].astype(float)
    else:
        log_counter = add_debug_trace(
                'DataNotFound: Could not find column value_wh in hist_cons_df', 
                logger, endpoint_request, log_counter)
        raise DataNotFound 
    
    if 'substation_id' in df.columns:
        df['substation_id'] = df['substation_id'].astype('category')
    else:
        log_counter = add_debug_trace(
                'DataNotFound: Could not find column substation_id in hist_cons_df', 
                logger, endpoint_request, log_counter)
        raise DataNotFound 
    
    if 'fylkesnavn' in df.columns:
        df['fylkesnavn'] = df['fylkesnavn'].astype('category')
    else:
        log_counter = add_debug_trace(
                'DataNotFound: Could not find column fylkesnavn in hist_cons_df', 
                logger, endpoint_request, log_counter)
        raise DataNotFound 
    
    if 'long' in df.columns:
        df['long'] = df['long'].astype(float)
    else:
        log_counter = add_debug_trace(
                'DataNotFound: Could not find column long in hist_cons_df', 
                logger, endpoint_request, log_counter)
        raise DataNotFound 

    if 'lat' in df.columns:
        df['lat'] = df['lat'].astype(float)
    else:
        log_counter = add_debug_trace(
                'DataNotFound: Could not find column lat in hist_cons_df', 
                logger, endpoint_request, log_counter)
        raise DataNotFound 

    return df


def _check_input_data(df: pd.DataFrame,
                      percentage: float = 0.1,
                      value_col: str = 'aggregated_per_mp',
                      trafo_col: str = 'trafo',
                      len_history: int = (365 + 366) * 24):
    '''
    This function checks the zero values ​​of the transformers in the dataset and if the zero values ​​in a transformer are more than one-tenth of the transformer's length, this          transformer is removed from the dataset.

    # Parameters
    --------------
    df            : Azure energy consumption dataset
    percentage    : Percentage that is used to select the appropriate transformers
    column_name   : Name of the column showing energy consumption 
    trafo_column  : Name of the column showing substations' names

    # Returns
    --------------
    A pandas dataframe with the transformers that has less zero values than one-tenth of their length.
    '''

    # Group by
    count_zeros_df = df.groupby(trafo_col).agg(lambda x: x.eq(0).sum())

    # empty_trafo_idx is a CategoricalIndex
    empty_trafo_idx = count_zeros_df.loc[
        count_zeros_df[value_col] > len_history * percentage].index
    #
    if not empty_trafo_idx.empty:
        df.drop(index=df.loc[df[trafo_col].isin(empty_trafo_idx)].index,
                inplace=True)
    #
    return df


def _remove_outliers(hourly_ser: pd.Series,
                     z_tolerance_low: int = -5,
                     z_tolerance_high: int = 5):
    '''
    # Function detects and removes outliers from the dataframe using a rolling window,
    # using a 30D history mean avrage together with z_score to evaluate if a datapoint is an outlier.
    '''

    THIRTY_DAYS_HOURS = 720
    #Rename column for formating purpose

    #Find 30D mean avrage using the previouse 30D history
    MA_30D = hourly_ser.rolling(THIRTY_DAYS_HOURS, center=True).mean()

    #Fill naN values occuring the first 30D of the dataframe using backwards filling
    MA_30D = MA_30D.fillna(method='bfill')

    #Compute z_score for each datapoint, and append in new column
    load_MA_30D_zscore = (hourly_ser - MA_30D) / (hourly_ser.std(ddof=0))

    #Evaluate if a datapoint is to many standard deviations away from the average mean. After tuning the tolerance is chosen
    #to be -2. Only detecting outliers that are too far below the 30D mean, NOT above. Dataframe column for outlier,
    #value either 1/0, TRUE/FALSE.
    outlier_below_idx = (load_MA_30D_zscore < z_tolerance_low).astype(int)
    outlier_above_idx = (load_MA_30D_zscore > z_tolerance_high).astype(int)

    #Find index of the detected outliers above and below mean
    outlier_below = np.where(outlier_below_idx == 1)[0]
    outlier_above = np.where(outlier_above_idx == 1)[0]

    #Give outliers naN value and interoplate using linear method.
    for i in outlier_below:
        hourly_ser.iat[i] = np.nan
    hourly_ser = hourly_ser.interpolate(method='linear')

    for i in outlier_above:
        hourly_ser.iat[i] = np.nan
    hourly_ser = hourly_ser.interpolate(method='linear')

    print("  removed outliers below: ", len(outlier_below), " and above: ",
          len(outlier_above))

    return hourly_ser


def add_debug_trace(message: str,
                    logger: Union[LogEntry, logging.Logger] = None,
                    endpoint_request: Optional[EndpointRequest] = None,
                    log_counter: Optional[int] = None):
    def caller_name() -> str:
        """Return the calling function's name, 2 levels up."""
        # Ref: https://stackoverflow.com/a/57712700/
        return cast(
            FrameType,
            cast(FrameType,
                 cast(FrameType,
                      inspect.currentframe()).f_back).f_back).f_code.co_name

    if log_counter is not None:
        log_counter += 1
        _message = '\n'.join(_ for _ in [
            f'Caller: {str(caller_name())}', f'Step: {str(log_counter)}',
            message
        ])
    else:
        _message = '\n'.join(
            _ for _ in [f'Caller: {str(caller_name())}', message])

    if logger and isinstance(logger, LogEntry) and endpoint_request:
        logger.debug(msg=_message, endpoint_request=endpoint_request)
    elif logger:
        logger.debug(msg=_message)

    return log_counter if log_counter else None
