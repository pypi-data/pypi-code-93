###########################################################################
# 
#  Copyright 2020 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the 'License');
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an 'AS IS' BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

from starthinker.util.google_api import API_DV360
from starthinker.util.google_api.discovery_to_bigquery import Discovery_To_BigQuery

class DV360_Targeting:

  def __init__(self):
    self.schema = Discovery_To_BigQuery(
      'displayvideo',
      'v1'
    )

  def get_schema(self, name, resource):
    return [
      { 'name': 'partnerId', 'type': 'INTEGER', 'mode': 'NULLABLE' },
      { 'name': 'advertiserId', 'type': 'INTEGER', 'mode': 'NULLABLE' },
      { 'name': 'lineItemId', 'type': 'INTEGER', 'mode': 'NULLABLE' },
      { 'name': 'name', 'type': 'STRING', 'mode': 'REQUIRED' },
      { 'name': 'assignedTargetingOptionId', 'type': 'STRING', 'mode': 'REQUIRED' },
      { 'name': 'targetingType', 'type': 'STRING', 'mode': 'REQUIRED' },
      { 'name': 'inheritance', 'type': 'STRING', 'mode': 'REQUIRED' },
      { 'name': name, 'type':'RECORD', 'mode':'REQUIRED', 'fields':self.schema.resource_schema(resource) }
    ]

  def get_partner(self, auth, partners, targeting_type):
    for partner in partners:
      for row in API_DV360(
        auth,
        iterate=True
      ).partners().targetingTypes().assignedTargetingOptions().list(
        partnerId=str(partner),
        targetingType=targeting_type
      ).execute():
        row['partnerId'] = partner
        row['advertiserId'] = None
        row['lineItemId'] = None
        yield row


  def get_advertiser(self, auth, advertisers, targeting_type):
    for advertiser in advertisers:
      for row in API_DV360(
        auth,
        iterate=True
      ).advertisers().targetingTypes().assignedTargetingOptions().list(
        advertiserId=str(advertiser),
        targetingType=targeting_type
      ).execute():
        row['partnerId'] = None
        row['advertiserId'] = advertiser
        row['lineItemId'] = None
        yield row


  def get_line_item(self, auth, parameters, targeting_type):
    for parameter in parameters:
      for row in API_DV360(
        auth,
        iterate=True
      ).advertisers().lineItems().targetingTypes().assignedTargetingOptions().list(
        advertiserId=str(parameter['advertiserId']),
        lineItemId=str(parameter['lineItemId']),
        targetingType=targeting_type
      ).execute():
        row['partnerId'] = None
        row['advertiserId'] = parameter['lineItemId']
        row['lineItemId'] = None
        print(row)
        yield row


TARGETING_TYPES = {
  'TARGETING_TYPE_CHANNEL':{
    'name':'channelDetails',
    'resource':'ChannelAssignedTargetingOptionDetails',
    'partner':True,
    'advertiser':True,
    'lineitem':True,
  },
  'TARGETING_TYPE_APP_CATEGORY':{
    'name':'appCategoryDetails',
    'resource':'AppCategoryAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_APP':{
    'name':'appDetails',
    'resource':'AppAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_URL':{
    'name':'urlDetails',
    'resource':'UrlAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_DAY_AND_TIME':{
    'name':'dayAndTimeDetails',
    'resource':'DayAndTimeAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_AGE_RANGE':{
    'name':'ageRangeDetails',
    'resource':'AgeRangeAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_REGIONAL_LOCATION_LIST':{
    'name':'regionalLocationListDetails',
    'resource':'RegionalLocationListAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_PROXIMITY_LOCATION_LIST':{
    'name':'proximityLocationListDetails',
    'resource':'ProximityLocationListAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_GENDER':{
    'name':'genderDetails',
    'resource':'GenderAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_VIDEO_PLAYER_SIZE':{
    'name':'videoPlayerSizeDetails',
    'resource':'VideoPlayerSizeAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_USER_REWARDED_CONTENT':{
    'name':'userRewardedContentDetails',
    'resource':'UserRewardedContentAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_PARENTAL_STATUS':{
    'name':'parentalStatusDetails',
    'resource':'ParentalStatusAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_CONTENT_INSTREAM_POSITION':{
    'name':'contentInstreamPositionDetails',
    'resource':'ContentInstreamPositionAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_CONTENT_OUTSTREAM_POSITION':{
    'name':'contentOutstreamPositionDetails',
    'resource':'ContentOutstreamPositionAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_DEVICE_TYPE':{
    'name':'deviceTypeDetails',
    'resource':'DeviceTypeAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_AUDIENCE_GROUP':{
    'name':'audienceGroupDetails',
    'resource':'AudienceGroupAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_BROWSER':{
    'name':'browserDetails',
    'resource':'BrowserAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_HOUSEHOLD_INCOME':{
    'name':'householdIncomeDetails',
    'resource':'HouseholdIncomeAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_ON_SCREEN_POSITION':{
    'name':'onScreenPositionDetails',
    'resource':'OnScreenPositionAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_CARRIER_AND_ISP':{
    'name':'carrierAndIspDetails',
    'resource':'CarrierAndIspAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_KEYWORD':{
    'name':'keywordDetails',
    'resource':'KeywordAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_NEGATIVE_KEYWORD_LIST':{
    'name':'negativeKeywordListDetails',
    'resource':'NegativeKeywordListAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_OPERATING_SYSTEM':{
    'name':'operatingSystemDetails',
    'resource':'OperatingSystemAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_DEVICE_MAKE_MODEL':{
    'name':'deviceMakeModelDetails',
    'resource':'DeviceMakeModelAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_ENVIRONMENT':{
    'name':'environmentDetails',
    'resource':'EnvironmentAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_INVENTORY_SOURCE':{
    'name':'inventorySourceDetails',
    'resource':'InventorySourceAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_CATEGORY':{
    'name':'categoryDetails',
    'resource':'CategoryAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_VIEWABILITY':{
    'name':'viewabilityDetails',
    'resource':'ViewabilityAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_AUTHORIZED_SELLER_STATUS':{
    'name':'authorizedSellerStatusDetails',
    'resource':'AuthorizedSellerStatusAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_LANGUAGE':{
    'name':'languageDetails',
    'resource':'LanguageAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_GEO_REGION':{
    'name':'geoRegionDetails',
    'resource':'GeoRegionAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_INVENTORY_SOURCE_GROUP':{
    'name':'inventorySourceGroupDetails',
    'resource':'InventorySourceGroupAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_DIGITAL_CONTENT_LABEL_EXCLUSION':{
    'name':'digitalContentLabelExclusionDetails',
    'resource':'DigitalContentLabelAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':True,
    'lineitem':True,
  },
  'TARGETING_TYPE_SENSITIVE_CATEGORY_EXCLUSION':{
    'name':'sensitiveCategoryExclusionDetails',
    'resource':'SensitiveCategoryAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':True,
    'lineitem':True,
  },
  'TARGETING_TYPE_EXCHANGE':{
    'name':'exchangeDetails',
    'resource':'ExchangeAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_SUB_EXCHANGE':{
    'name':'subExchangeDetails',
    'resource':'SubExchangeAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
  'TARGETING_TYPE_THIRD_PARTY_VERIFIER':{
    'name':'thirdPartyVerifierDetails',
    'resource':'ThirdPartyVerifierAssignedTargetingOptionDetails',
    'partner':False,
    'advertiser':False,
    'lineitem':True,
  },
}
