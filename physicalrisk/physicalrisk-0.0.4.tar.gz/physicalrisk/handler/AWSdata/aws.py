import platform
from os import path

import boto3



s3 = boto3.resource(
    service_name='s3',
    region_name='eu-west-2',
    aws_access_key_id='AKIAYHM23ZQQ4JOTA34C',
    aws_secret_access_key='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'
)

s3_bucket_path = '/vsis3/bci-physical-risk-model/'

elev_tif = 'WorldClim/Elevation/wc2.1_2.5m_elev.tif'

#future precipitation
CMIP6_ssp126_2021_2040 = 'WorldClim/FuturePrecipitation/wc2.1_2.5m_prec_CNRM-CM6-1_ssp126_2021-2040.tif'
CMIP6_ssp126_2041_2060 = 'WorldClim/FuturePrecipitation/wc2.1_2.5m_prec_CNRM-CM6-1_ssp126_2041-2060.tif'

CMIP6_ssp245_2021_2040 = 'WorldClim/FuturePrecipitation/wc2.1_2.5m_prec_CNRM-CM6-1_ssp245_2021-2040.tif'
CMIP6_ssp245_2041_2060 = 'WorldClim/FuturePrecipitation/wc2.1_2.5m_prec_CNRM-CM6-1_ssp245_2041-2060.tif'
