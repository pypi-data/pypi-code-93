from datetime import datetime, timedelta

from notecoin.huobi.history.core import load_daily_all
from notedrive.lanzou import LanZouCloud

downer = LanZouCloud()
downer.ignore_limits()
downer.login_by_cookie()

start_date = datetime(2021, 5, 24)
end_date = datetime(2021, 8, 24)
duration = end_date - start_date
for i in range(duration.days + 1):
    day = end_date - timedelta(days=i)
    file_path = load_daily_all(period='1min', date=day)
    downer.upload_file(file_path, folder_id='3359096')
