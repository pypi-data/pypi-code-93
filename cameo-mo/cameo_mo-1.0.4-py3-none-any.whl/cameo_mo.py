# 2021-08-20 07:58 bowen to molly
# 這是為了 MQTT 持續性在 replit 上傳 .csv files to google drive 所撰寫的「單檔即產品」小程式
# 第一次執行時需要安裝 python3 套件有：
# pip3 install pydrive
# pip3 install oauth2client
# 測試執行的方法： python3 cameo_mo.py
# 整合到自己程式碼的方法： import cameo_mo 然後
# 使用方法可以參考 __main__ 指定檔案名稱與檔案內容即可上傳（例如 .csv 或任意純文字檔案）
# str_json_key_base 這是專屬本專案的 Google Cloud Platform 密鑰，避免外流
# 已經分享 cameo_mo 這個 google drive 雲端共享到 molly gmail 可以隨時用 google drive 看裡面的檔案群

from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime, timezone, timedelta
import base
import time

# service account: cameo-mo-google-drive@cameo-mo.iam.gserviceaccount.com
str_parent_folder_id = '1kIWkZ-FT-Wg3wh1RUH50zeSqfe13ww1z'  # google drive cameo_mo folder
str_json_key_base = '''ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAiY2FtZW8tbW8iLAogICJwcml2YXRlX2tleV9pZCI6ICIzOTFkMjk3MzcyMjU2YTEzMzM2OTk2M2I3ZDM2MzAyZjAwNzFmMTcyIiwKICAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdlFJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLY3dnZ1NqQWdFQUFvSUJBUUNlazZMaW54MHRjL204XG41WkQ2WWlvYlV1czZqeWRtQThwRmUxT3prY0xPZy9TaGJWNnVOT0RkRDFwRmFLeEk5c3gzOVNVQmFKTzhuNGJQXG45RnBjdG41djlaSy83bnMxOHdoajRQTEV4L29jNHoxZmtwNlg5Q0lsVER5S3h0MkZRdjYwNmNEVzVuR25GZTBYXG4zaXVJUWlla0dsRGIvbnU2cVZQS3pOOENLNElVM21lVHdDM05KVVY3RGltS3VOd2ZKTno5NnNUVTl5czAwV1E5XG54S3lPQ0tuZmczNjhvelpzWE1meEZITUxYeGxoRjlXVHRjV3hqWHR3L2p0Snp3NVBnUVFreTJacDNQM09QRWREXG45cXh1ZFk2Z1dMN0F4WW9hMUJjOGoxUkgwSHQxcEhjdmViUkFGZ0FTRDVQTTBoZW0wR3YwczBRNVB6ZkNtcHZPXG5XOE8yRTBPeEFnTUJBQUVDZ2dFQUhrcjJ3Vk1EQ0dWUXpuQ09WdjU4cTdhVjRCeHJ1dFc3aExWd0FtdzBhaTRVXG5BK2g0UDFBenFwY2R1QWVzYmMzVHRwQzZqbi9UUlNPMlpiQjR1S0JXRy80dUdBTXZQMW1iZnpVQU8yNDJUZUZ0XG5IbjVNVkp2YkVBUDF4czhCajAwQ2lqM2pURW8rYU54TDdCVFJmUmlpS1B1citiS3VJVFRxb0dHdHNtVHNWeDd1XG5iMEVpd3RjQ013d3h6U2ZFR3pINDZzM0U5RWNqaU5KdTJNV3ZtTVQ4cGQ2R2ZNOEtRT3VmZy9EUCtZdW9UNU91XG5uNWx5TzdpRkNJb092a3hTNnpraTIxNjhRUm9Xdy9kbC9xNDVrUy8wMWRTd1UwMGw5Z3ZPbkF6dXp5YmR5RGIrXG5QOGg5Q201Z3Y2b091Z1NtNllVT2t5KzBCWWlBaTYrL20wOG1BU1NleVFLQmdRREwzRlU0ZzFIeFZSLzN3OXBvXG5LUDhvMzRzQ0Q0MS9HRmtXSjlLUTBwRVd1N1ZCYi8wdEtDQnRJdlM5ZFpiS21aT3N0U1YvbEMxa3lIK2pkVHErXG5iQ2tQeGRZNkhrdXNieXFsbHFuNE9iSytqcGdZYXV1Z0R0RWczTWZrTm5YSFQxU3hBSTNjeFB0TUhQbVlJaURRXG5IRzA3dWRWTno3Y3BJM0JTaDZuajV5NVpiUUtCZ1FESElsd2txQ3JpL0xyTkhTaVhxaWtZZmlPUkNsZG40RzliXG5BOVA3RVQ3QzYzZXlIMi93Z1RSTXFmeEJDS2c4NGVvMlJ3L3FFdzNaN1JYMjcvMFlDeGZ6VEJwSXBsbW1qcGpkXG5xT3RUTTd6ME5Kc1g5elV0MFhQMGxueXhUa1AvV0l3R2RNdzdpUHJoelJmbHJ2cVdXckZoUjZ3T0FTZFdBeTVaXG5jdzFBR2tETTFRS0JnQ0dmYUdyV3RkZ2cyeEhwT29kOVk0QWhSbk1EajZuTG9UM1hPWkpyT0VUUWxyZUJPZmVOXG5xN04wVlhzOS9xM1JvSnFXa2VXMTBiclNtc0toM2h0MENWMnhtb0NoYUllN0dnU1BrZDcvM1N3eXBvRTRlVDQvXG4wMXdoTGRMRTdLMy90bzh1OFRiZFFqa3VlamdPUU8weUV3NEx1MU9IRThWME05MVl4THR5OEtFTkFvR0FVN2hGXG5adi93citlekhZTVJ5dG0yVjE3STB6UzIxS3hPQk1UU1BXN2RwUk5jQ2w0Zk1NMFJVTjN5ZU9FTDRqVFV4Q2NTXG5NTVg3LzlBbWVPQWkxeFhxNXRYckF2bzFITW84eUl3NUM0em45dithNlBOOHZ4dWRGWXFqTitRQXdIell1ZW9tXG41eXpLMVYzbG15SDZwblhRdDJacmxxT3podnpsWXFQMVFTc0liVlVDZ1lFQXF6MTJ2S0VFTnZldm1wa2VvbjVWXG5VWUNIZmtlR3FLbHBYMXFoZ3AyR0tsdW5Ua2V2YlV1SlNqTDlzdGFrWUcraWY0SlFRWmREZWs2dVY1a041aUJLXG5TL1J2TmVQM0JsVWxIRThCbGxZUDh5KzhNTnlaMlF4Uk41bjk1aUhHdERZeWJERys1ekQxT1N5UmpoV1luNE96XG50ODVFOGZiQk45TjUyMHBXQktaRDVKWT1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJjYW1lby1tby1nb29nbGUtZHJpdmVAY2FtZW8tbW8uaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTEwMjE0OTEyOTM5ODg3NDU2MDkwIiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9jYW1lby1tby1nb29nbGUtZHJpdmUlNDBjYW1lby1tby5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIKfQo='''


def get_time():
    dt = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class GoogleDriveIo:
    def __init__(self):
        gauth = GoogleAuth()
        scope = ["https://www.googleapis.com/auth/drive"]
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_dict(eval(base.decode(str_json_key_base)),
                                                                             scope)
        self.drive = GoogleDrive(gauth)

    def write(self, str_filename, str_content):
        f = self.drive.CreateFile({'parents': [{'id': str_parent_folder_id}], 'title': str_filename})
        f.SetContentString(str_content)
        f.Upload()

    def read(self, str_filename):
        lst = self.drive.ListFile({'q': f"title='{str_filename}' and trashed=false"}).GetList()
        return lst[0].GetContentString()

    def ls(self):
        lst = self.drive.ListFile({'q': f"'{str_parent_folder_id}' in parents and trashed=false"}).GetList()
        print(lst)


def hi():
    print('hi cameo_mo')


if __name__ == "__main__":
    g = GoogleDriveIo()
    str_filename = f'file_{get_time()}.csv'
    str_csv_content = 'col1,col2,col3\n1,2,3\n'
    t = time.time()
    print(f'Write file to Google Drive:{str_filename}')
    g.write(str_filename, str_csv_content)
    print(time.time() - t)
