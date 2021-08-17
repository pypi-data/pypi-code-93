from worlddata.APISections.base import WorldDataBase


class WorldDataTimeSeries(WorldDataBase):

    def time_series(self, sector, sub_sector, super_region, source, trend_ids):
        return self.call_api_post("time-series", sector=sector, sub_sector=sub_sector, super_region=super_region,
                                  source=source, trend_ids=trend_ids)
    
    def time_series_with_bucket(self, bucket, size, offset, trend_ids, **kwargs):
        return self.call_api_post("time-series-with-bucket", bucket=bucket, size=size, offset=offset, trend_ids=trend_ids, kwargs=kwargs)
