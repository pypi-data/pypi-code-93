import os
from groclimateclient import GroClimateClient
from groclient import GroClient


API_HOST = 'api.gro-intelligence.com'
ACCESS_TOKEN = os.environ['GROAPI_TOKEN']

def main():
    client = GroClimateClient(API_HOST, ACCESS_TOKEN)
    # client = GroClient(API_HOST, ACCESS_TOKEN)
    selection = {'metric_id': 2540047, 'metric_name': 'Temperature', 'item_id': 2177, 'item_name': 'Temperature (max)', 'region_id': 13052, 'region_name': 'Alaska', 'partner_region_id': 0, 'partner_region_name': 'World', 'frequency_id': 1, 'frequency_name': 'daily', 'source_id': 105, 'source_name': 'NOAA GFS 00Z Forecast', 'start_date': '2019-07-08T00:00:00.000Z', 'end_date': '2021-09-03T00:00:00.000Z', 'data_count_estimate': 789}
    datapoints = client.get_data_points(**selection)
    print(datapoints[0])

if __name__ == "__main__":
    main()
