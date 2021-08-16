"""

"""
import zipfile

from notecoin.huobi.history.utils import *
from notetool.log import log
from tqdm import tqdm

ALL_PERIODS = ['1min', '5min', '15min', '30min', '60min', '4hour', '1day']
pre_url = "https://futures.huobi.com/data"
logger = log()

_SWAP = "swap"
_SPOT = "spot"
_FUTURE = "future"
_OPTION = "option"
_LINEARSWAP = "linear-swap"


class Response:
    def __init__(self, status: bool = True, data: dict = None):
        self.status = status or True
        self.data = data or {}

    def success(self):
        self.status = True

    def error(self):
        self.status = False

    def put(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def extend(self, data: dict = None):
        if isinstance(data, dict):
            self.data.update(data)


class HistoryDownload:
    def __init__(self, _pre_url=None,
                 data_type: str = None,
                 all_period: list = None,
                 _type: str = 'spot',
                 freq: str = None,
                 start_date=None,
                 end_date=None,
                 all_symbols=None,
                 download_dir=None
                 ):
        self.freq = freq or "daily"
        self.type = _type or 'spot'
        self.data_type = data_type or 'klines'
        self.pre_url = _pre_url or "https://futures.huobi.com/data"
        self.all_period = all_period or ALL_PERIODS
        self.start_date = start_date or datetime(2017, 10, 27)
        self.end_date = end_date or datetime(2021, 7, 27)
        self.all_symbols = all_symbols
        self.download_dir = download_dir or "./data"

    def init(self):
        print(self.type)
        if self.all_symbols is None:
            ok, all_symbols = False, []
            if self.type == _SPOT:
                ok, all_symbols = get_all_spot_symbols()
            elif self.type == _FUTURE:
                ok, all_symbols = get_all_future_symbols()
            elif self.type == _SWAP:
                ok, all_symbols = get_all_swap_symbols()
            elif self.type == _OPTION:
                ok, all_symbols = get_all_option_symbols()
            elif self.type == _LINEARSWAP:
                ok, all_symbols = get_all_linearswap_symbols()

            if not ok:
                logger.warning(all_symbols)

                return
            self.all_symbols = all_symbols

    def un_zip(self, file_path) -> Response:
        """unzip zip file"""
        response = Response(True)
        zip_file = zipfile.ZipFile(file_path)
        file_dir = os.path.split(file_path)[0]
        for name in zip_file.namelist():
            zip_file.extract(name, path=file_dir)
            response.put('file_path', os.path.join(file_dir, name))
        zip_file.close()

        return response

    def http_download(self, url: str, download_dir) -> Response:
        response = Response()
        try:
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            if url is None:
                return Response(False, {"msg": 'url is null'})
            data = requests.get(url, allow_redirects=True)
            file_name = os.path.basename(url)
            file_path = os.path.join(download_dir, file_name)
            if len(data.content) > 30:
                with open(file_path, 'wb') as f:
                    f.write(data.content)
                response.put("file_path", file_path)
            else:
                response.error()
                response.put("file_path", "File not exists.")

        except Exception as e:
            response.put("download error", str(e))

        return response

    def _download_daily(self, path_url, symbol, period) -> tuple:
        all_res = []
        interval = self.end_date - self.start_date
        for index in tqdm(range(interval.days)):
            current = self.start_date + timedelta(days=index)
            url = f'{path_url}/{symbol.upper()}-{period}-{current.year}-{current.month:02}-{current.day:02}'
            download_dir = os.path.join(self.download_dir, symbol, period)

            zip_file = f'{url}.zip'
            check_file = f'{url}.CHECKSUM'
            response1 = self.http_download(zip_file, download_dir)
            response2 = self.http_download(check_file, download_dir)
            response = Response(response1.status)

            response.extend({
                "zip_url": zip_file,
                "zip_file": response1.get('file_path'),
                "check_url": check_file,
                "check_file": response2.get('file_path')
            })
            if response1.status:
                response3 = self.un_zip(response1.get('file_path'))
                response3.put("file", response3.get('file_path'))

            all_res.append(response)
        all_oks = [response for response in all_res if response.status]
        all_errs = [response for response in all_res if not response.status]
        return all_oks, all_errs

    def b_download(self):
        """return date is: [start, end)"""
        self.init()
        for symbol in self.all_symbols:
            for period in self.all_period:
                if period in ['trades', ]:
                    path_url = f'{self.pre_url}/{self.data_type}/{self.type}/{self.freq}/{symbol}'
                else:
                    path_url = f'{self.pre_url}/{self.data_type}/{self.type}/{self.freq}/{symbol}/{period}'
                all_oks, all_errs = self._download_daily(path_url, symbol, period)
                logger.warning(f'success:{all_oks}')
                logger.warning(f'failed:{all_errs}')
        logger.info('done')

    def b_download_daily_spot(self):
        """return date is: [start, end)"""
        self.type = _SPOT
        self.b_download()

    def b_download_daily_future(self):
        """return date is: [start, end)"""
        self.type = _FUTURE
        self.b_download()

    def b_download_daily_swap(self):
        """return date is: [start, end)"""
        self.type = _SWAP
        self.b_download()

    def b_download_daily_linearswap(self):
        """return date is: [start, end)"""
        self.type = _LINEARSWAP
        self.b_download()

    def b_download_daily_option(self):
        """return date is: [start, end)"""
        self.type = _OPTION
        self.b_download()


if __name__ == "__main__":
    history = HistoryDownload(data_type="klines",
                              start_date=datetime(2021, 5, 21),
                              end_date=datetime(2021, 5, 23),
                              all_period=['1min', '15min'],
                              all_symbols=['SHIBUSDT'],
                              download_dir='/root/workspace/tmp/data'
                              )
    history.b_download()
    # download_daily_future()
    # download_daily_swap()
    # download_daily_linearswap()
    # download_daily_option(all_period=['1min'])
