###########################################################################
#
#  Copyright 2020 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################
#
#  This code generated (see starthinker/scripts for possible source):
#    - Command: "python starthinker_ui/manage.py airflow"
#
###########################################################################

'''
--------------------------------------------------------------

Before running this Airflow module...

  Install StarThinker in cloud composer ( recommended ):

    From Release: pip install starthinker
    From Open Source: pip install git+https://github.com/google/starthinker

  Or push local code to the cloud composer plugins directory ( if pushing local code changes ):

    source install/deploy.sh
    4) Composer Menu
    l) Install All

--------------------------------------------------------------

  If any recipe task has "auth" set to "user" add user credentials:

    1. Ensure an RECIPE['setup']['auth']['user'] = [User Credentials JSON]

  OR

    1. Visit Airflow UI > Admin > Connections.
    2. Add an Entry called "starthinker_user", fill in the following fields. Last step paste JSON from authentication.
      - Conn Type: Google Cloud Platform
      - Project: Get from https://github.com/google/starthinker/blob/master/tutorials/cloud_project.md
      - Keyfile JSON: Get from: https://github.com/google/starthinker/blob/master/tutorials/deploy_commandline.md#optional-setup-user-credentials

--------------------------------------------------------------

  If any recipe task has "auth" set to "service" add service credentials:

    1. Ensure an RECIPE['setup']['auth']['service'] = [Service Credentials JSON]

  OR

    1. Visit Airflow UI > Admin > Connections.
    2. Add an Entry called "starthinker_service", fill in the following fields. Last step paste JSON from authentication.
      - Conn Type: Google Cloud Platform
      - Project: Get from https://github.com/google/starthinker/blob/master/tutorials/cloud_project.md
      - Keyfile JSON: Get from: https://github.com/google/starthinker/blob/master/tutorials/cloud_service.md

--------------------------------------------------------------

CM360 Campaign Comparison

.

  - When prompted choose the new data sources you just created.
  - Or give these intructions to the client.

--------------------------------------------------------------

This StarThinker DAG can be extended with any additional tasks from the following sources:
  - https://google.github.io/starthinker/
  - https://github.com/google/starthinker/tree/master/dags

'''

from starthinker.airflow.factory import DAG_Factory

INPUTS = {
  'auth_cm': 'user',  # Credentials used for reading data.
  'auth_bq': 'user',  # Credentials used for reading data.
  'recipe_slug': '',  # Name of dataset.
  'account': 12345,  # Campaign Manager Account ID
  'recipe_name': '',  # Name of report.
  'advertiser': [],  # Optional comma delimited list of ids.
}

RECIPE = {
  'setup': {
    'day': [
      'Mon', 
      'Tue', 
      'Wed', 
      'Thu', 
      'Fri', 
      'Sat', 
      'Sun'
    ], 
    'hour': [
      4
    ]
  }, 
  'tasks': [
    {
      'dataset': {
        'description': 'Create a dataset for bigquery tables.', 
        'auth': 'service', 
        'dataset': {
          'field': {
            'name': 'recipe_slug', 
            'kind': 'string', 
            'order': 1, 
            'prefix': 'Campaign_Comparison_', 
            'default': '', 
            'description': 'Name of dataset.'
          }
        }
      }
    }, 
    {
      'dcm': {
        'hour': [
          1
        ], 
        'description': 'Create KPI report.', 
        'auth': {
          'field': {
            'name': 'auth_cm', 
            'kind': 'authentication', 
            'order': 0, 
            'default': 'user', 
            'description': 'Credentials used for reading data.'
          }
        }, 
        'report': {
          'account': {
            'field': {
              'name': 'account', 
              'kind': 'integer', 
              'order': 1, 
              'default': 12345, 
              'description': 'Campaign Manager Account ID'
            }
          }, 
          'name': {
            'field': {
              'name': 'recipe_name', 
              'kind': 'string', 
              'order': 3, 
              'prefix': 'Campaign Comparison ', 
              'default': '', 
              'description': 'Name of report.'
            }
          }, 
          'body': {
            'kind': 'dfareporting#report', 
            'format': 'CSV', 
            'type': 'STANDARD', 
            'criteria': {
              'dateRange': {
                'kind': 'dfareporting#dateRange', 
                'relativeDateRange': 'LAST_90_DAYS'
              }, 
              'dimensions': [
                {
                  'kind': 'dfareporting#sortedDimension', 
                  'name': 'date'
                }, 
                {
                  'kind': 'dfareporting#sortedDimension', 
                  'name': 'advertiserId'
                }, 
                {
                  'kind': 'dfareporting#sortedDimension', 
                  'name': 'campaignId'
                }, 
                {
                  'kind': 'dfareporting#sortedDimension', 
                  'name': 'adId'
                }, 
                {
                  'kind': 'dfareporting#sortedDimension', 
                  'name': 'placementId'
                }, 
                {
                  'kind': 'dfareporting#sortedDimension', 
                  'name': 'platformType'
                }, 
                {
                  'kind': 'dfareporting#sortedDimension', 
                  'name': 'zipCode'
                }
              ], 
              'metricNames': [
                'impressions', 
                'clicks', 
                'totalConversions', 
                'mediaCost'
              ]
            }, 
            'schedule': {
              'active': True, 
              'repeats': 'WEEKLY', 
              'repeatsOnWeekDays': 'MONDAY', 
              'every': 1
            }, 
            'delivery': {
              'emailOwner': False
            }
          }, 
          'filters': {
            'advertiser': {
              'values': {
                'field': {
                  'name': 'advertiser', 
                  'kind': 'integer_list', 
                  'order': 3, 
                  'default': [
                  ], 
                  'description': 'Optional comma delimited list of ids.'
                }
              }
            }
          }
        }
      }
    }, 
    {
      'dcm': {
        'description': 'Download KPI report.', 
        'auth': 'user', 
        'report': {
          'account': {
            'field': {
              'name': 'account', 
              'kind': 'integer', 
              'order': 1, 
              'default': 12345, 
              'description': 'Campaign Manager Account ID'
            }
          }, 
          'name': {
            'field': {
              'name': 'recipe_name', 
              'kind': 'string', 
              'order': 3, 
              'prefix': 'Campaign Comparison ', 
              'default': '', 
              'description': 'Name of report.'
            }
          }
        }, 
        'out': {
          'bigquery': {
            'auth': {
              'field': {
                'name': 'auth_bq', 
                'kind': 'authentication', 
                'order': 0, 
                'default': 'service', 
                'description': 'Authorization used for writing data.'
              }
            }, 
            'dataset': {
              'field': {
                'name': 'recipe_slug', 
                'kind': 'string', 
                'order': 1, 
                'prefix': 'Campaign_Comparison_', 
                'default': '', 
                'description': 'Name of dataset.'
              }
            }, 
            'table': 'CM_Report', 
            'header': True
          }
        }
      }
    }, 
    {
      'google_api': {
        'hour': [
          1
        ], 
        'auth': 'user', 
        'api': 'dfareporting', 
        'version': 'v3.4', 
        'function': 'advertisers.list', 
        'iterate': True, 
        'kwargs': {
          'accountId': 6543
        }, 
        'results': {
          'bigquery': {
            'dataset': {
              'field': {
                'name': 'recipe_slug', 
                'kind': 'string', 
                'order': 1, 
                'prefix': 'Campaign_Comparison_', 
                'default': '', 
                'description': 'Name of dataset.'
              }
            }, 
            'table': 'CM_Advertisers'
          }
        }
      }
    }, 
    {
      'google_api': {
        'hour': [
          1
        ], 
        'auth': 'user', 
        'api': 'dfareporting', 
        'version': 'v3.4', 
        'function': 'campaigns.list', 
        'iterate': True, 
        'kwargs': {
          'accountId': 6543
        }, 
        'results': {
          'bigquery': {
            'dataset': {
              'field': {
                'name': 'recipe_slug', 
                'kind': 'string', 
                'order': 1, 
                'prefix': 'Campaign_Comparison_', 
                'default': '', 
                'description': 'Name of dataset.'
              }
            }, 
            'table': 'CM_Campaigns'
          }
        }
      }
    }, 
    {
      'google_api': {
        'hour': [
          1
        ], 
        'auth': 'user', 
        'api': 'dfareporting', 
        'version': 'v3.4', 
        'function': 'ads.list', 
        'iterate': True, 
        'kwargs': {
          'accountId': 6543
        }, 
        'results': {
          'bigquery': {
            'dataset': {
              'field': {
                'name': 'recipe_slug', 
                'kind': 'string', 
                'order': 1, 
                'prefix': 'Campaign_Comparison_', 
                'default': '', 
                'description': 'Name of dataset.'
              }
            }, 
            'table': 'CM_Ads'
          }
        }
      }
    }, 
    {
      'google_api': {
        'hour': [
          1
        ], 
        'auth': 'user', 
        'api': 'dfareporting', 
        'version': 'v3.4', 
        'function': 'placements.list', 
        'iterate': True, 
        'kwargs': {
          'accountId': 6543
        }, 
        'results': {
          'bigquery': {
            'dataset': {
              'field': {
                'name': 'recipe_slug', 
                'kind': 'string', 
                'order': 1, 
                'prefix': 'Campaign_Comparison_', 
                'default': '', 
                'description': 'Name of dataset.'
              }
            }, 
            'table': 'CM_Placements'
          }
        }
      }
    }, 
    {
      'bigquery': {
        'auth': {
          'field': {
            'name': 'auth_bq', 
            'kind': 'authentication', 
            'order': 0, 
            'default': 'user', 
            'description': 'Credentials used for reading data.'
          }
        }, 
        'from': {
          'query': "WITH CC_REPORT AS (           SELECT              Report_Day,             CONCAT(CA.name, ' - ', CA.id) AS Advertiser,             CONCAT(CC.name, ' - ', CC.id) AS Campaign,             CONCAT(CD.name, ' - ', CD.id) AS Ad,             CONCAT(CP.name, ' - ', CP.id) AS Placement,             CR.Platform_Type AS Platform_Type,             CD.type AS Ad_Type,             Zip_Postal_Code AS Zip_Code,             CR.Impressions AS Impressions,             CR.Clicks AS Clicks,             CAST(CR.Total_conversions AS INT64) AS Conversions,             CR.Media_Cost AS Costs           FROM `{dataset}.CM_Report` AS CR           LEFT JOIN `{dataset}.CM_Advertisers` AS CA           ON CR.Advertiser_Id=CA.id           LEFT JOIN `{dataset}.CM_Campaigns` AS CC           ON CR.Campaign_Id=CC.id           LEFT JOIN `{dataset}.CM_Ads` AS CD           ON CR.Ad_Id=CD.id           LEFT JOIN `{dataset}.CM_Placements` AS CP           ON CR.Placement_Id=CP.id           ORDER BY Report_Day DESC         ),                  CC_REPORT_ZIP AS (           SELECT             R.*,             Z.city,             Z.county,             Z.state_code,             Z.area_land_meters,             Z.zip_code_geom           FROM CC_REPORT AS R           LEFT JOIN `bigquery-public-data.geo_us_boundaries.zip_codes` AS Z           ON Z.zip_code=R.Zip_Code         ),                  CC_REPORT_POPULATION AS (           SELECT             R.*,             C.pop_16_over AS Population           FROM CC_REPORT_ZIP AS R           LEFT JOIN `bigquery-public-data.census_bureau_acs.zip_codes_2018_5yr` AS C           ON R.Zip_Code=C.geo_id         ),                  CC_REPORT_DMA AS (           SELECT             R.* EXCEPT(Zip_Code),             STRUCT (               R.Zip_Code,               city,               county,               STRUCT(D.dma_id AS Id, D.dma_name AS Name) AS DMA,               state_code,               area_land_meters             ) AS Location           FROM CC_REPORT_POPULATION AS R           CROSS JOIN `bigquery-public-data.geo_us_boundaries.designated_market_area` AS D           WHERE ST_DWithin(R.zip_code_geom, D.dma_geom, 0)         ),                  CC_REPORT_MAX AS (           SELECT             MAX(Population) AS Population,             MAX(SAFE_DIVIDE(Population, Location.area_land_meters)) AS Density,             MAX(Impressions) AS Impression,             MAX(SAFE_DIVIDE(Impressions, Population)) AS Impression_Rate,             MAX(SAFE_DIVIDE(Impressions, Costs)) AS Impression_Cost,             MAX(Clicks) AS Click,             MAX(SAFE_DIVIDE(Clicks, Impressions)) AS Click_Rate,             MAX(SAFE_DIVIDE(Clicks, Costs)) AS Click_Cost,             MAX(Conversions) AS Conversion,             MAX(SAFE_DIVIDE(Conversions, Clicks)) AS Conversion_Rate,             MAX(SAFE_DIVIDE(Conversions, Costs)) AS Conversion_Cost,             MAX(Costs) AS Costs               FROM CC_REPORT_DMA         ),                  CC_REPORT_RANKS AS (           SELECT             R.*,             STRUCT (               SAFE_DIVIDE(R.Population, M.Population) AS Population,               SAFE_DIVIDE(SAFE_DIVIDE(R.Population, Location.area_land_meters), M.Density) AS Density,               SAFE_DIVIDE(R.Impressions, M.Impression) AS Impression,               SAFE_DIVIDE(SAFE_DIVIDE(R.Impressions,R.Population), M.Impression_Rate) AS Impression_Rate,               SAFE_DIVIDE(SAFE_DIVIDE(R.Impressions,R.Costs), M.Impression_Cost) AS Impression_Cost,               SAFE_DIVIDE(R.Clicks, M.Click) AS Click,               SAFE_DIVIDE(SAFE_DIVIDE(R.Clicks,R.Impressions),M.Click_Rate) AS Click_Rate,               SAFE_DIVIDE(SAFE_DIVIDE(R.Clicks, R.Costs), M.Click_Cost) AS Click_Cost,               SAFE_DIVIDE(R.Conversions, M.Conversion) AS Conversion,               SAFE_DIVIDE(SAFE_DIVIDE(R.Conversions, R.Clicks), M.Conversion_Rate) AS Conversion_Rate,               SAFE_DIVIDE(SAFE_DIVIDE(R.Conversions, R.Costs), M.Conversion_Cost) AS Conversion_Cost,               SAFE_DIVIDE(R.Costs, M.Costs) AS Costs             ) AS Location_Ranking           FROM CC_REPORT_DMA AS R           CROSS JOIN CC_REPORT_MAX AS M         )                  SELECT           'COHORT-A' AS Cohort,           Report_Day,           Advertiser,           Campaign,           Ad,           Placement,           Ad_Type,           Platform_Type,           Location,           Location_Ranking,           STRUCT(             Advertiser,             Campaign,             Ad,             Placement,             Population,             Impressions,             Clicks,             Conversions,             Costs           ) AS Cohort_A,           STRUCT(             '!COHORT-B' AS Advertiser,             '!COHORT-B' AS Campaign,             '!COHORT-B' AS Ad,             '!COHORT-B' AS Placement,             0 AS Population,             0 AS Impressions,             0 AS Clicks,             0 AS Conversions,             0 AS Costs             ) AS Cohort_B         FROM CC_REPORT_RANKS         UNION ALL         SELECT           'COHORT-B' AS Cohort,           Report_Day,           Advertiser,           Campaign,           Ad,           Placement,           Ad_Type,           Platform_Type,           Location,           Location_Ranking,           STRUCT(             '!COHORT-A' AS Advertiser,             '!COHORT-A' AS Campaign,             '!COHORT-A' AS Ad,             '!COHORT-A' AS Placement,             0 AS Population,             0 AS Impressions,             0 AS Clicks,             0 AS Conversions,             0 AS Costs             ) AS Cohort_A,           STRUCT(             Advertiser,             Campaign,             Ad,             Placement,             Population,             Impressions,             Clicks,             Conversions,             Costs           ) AS Cohort_B,         FROM CC_REPORT_RANKS", 
          'parameters': {
            'dataset': {
              'field': {
                'name': 'recipe_slug', 
                'kind': 'string', 
                'order': 1, 
                'prefix': 'Campaign_Comparison_', 
                'default': '', 
                'description': 'Name of dataset.'
              }
            }
          }, 
          'legacy': False
        }, 
        'to': {
          'dataset': {
            'field': {
              'name': 'recipe_slug', 
              'kind': 'string', 
              'order': 1, 
              'prefix': 'Campaign_Comparison_', 
              'default': '', 
              'description': 'Name of dataset.'
            }
          }, 
          'view': 'Comprison_View'
        }
      }
    }
  ]
}

dag_maker = DAG_Factory('cm360_campaign_comparison', RECIPE, INPUTS)
dag = dag_maker.generate()

if __name__ == "__main__":
  dag_maker.print_commandline()
