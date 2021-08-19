bucket_name = 'tl-fund-dm'
_s3_bucket_uri: str = f's3://{bucket_name}/dm'
name = 'mng_indicator_score'
mng_s3_uri = f'{_s3_bucket_uri}/{name}.parquet'

name = 'fund_indicator_score'
fund_s3_uri = f'{_s3_bucket_uri}/{name}.parquet'

name = 'mng_best_fund'
mng_best_uri = f'{_s3_bucket_uri}/{name}.parquet'