"""

"""
import zipfile

from notecoin.huobi.history.utils import *
from notetool.log import log
from tqdm import tqdm

_SWAP = "swap"
_SPOT = "spot"
_FUTURE = "future"
_OPTION = "option"
_LINEARSWAP = "linear-swap"
ALL_TYPES = ["spot", "swap", "future", "option", "", "linear-swap"]
ALL_DATA_TYPES = ['klines', 'trades']
ALL_PERIODS = ['1min', '5min', '15min', '30min', '60min', '4hour', '1day']
ALL_FREQ = ["daily"]
PRE_URL = "https://futures.huobi.com/data"

logger = log()


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
    def __init__(self,
                 pre_url=None,
                 data_type: str = None,
                 all_periods: list = None,
                 _type: str = None,
                 freq: str = None,
                 start_date=None,
                 end_date=None,
                 all_symbols=None,
                 download_dir=None
                 ):
        self.freq = freq or ALL_FREQ[0]
        self.type = _type or ALL_TYPES[0]
        self.pre_url = pre_url or PRE_URL
        self.data_type = data_type or ALL_DATA_TYPES[0]

        self.all_symbols = all_symbols
        self.download_dir = download_dir or "./data"
        self.all_periods = all_periods or ALL_PERIODS
        self.start_date = start_date or datetime(2017, 10, 27)
        self.end_date = end_date or datetime(2021, 7, 27)

    @staticmethod
    def _file_unzip(file_path) -> Response:
        """unzip zip file"""
        response = Response(True)
        zip_file = zipfile.ZipFile(file_path)
        file_dir = os.path.split(file_path)[0]
        for name in zip_file.namelist():
            zip_file.extract(name, path=file_dir)
            response.put('file_path', os.path.join(file_dir, name))
        zip_file.close()

        return response

    @staticmethod
    def _http_download(url: str, download_dir) -> Response:
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

    def init_parameters(self):
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

    def download_symbol_period_day(self, path_url, symbol, period, current,
                                   delete_zip=True,
                                   delete_check=True,
                                   *args, **kwargs) -> Response:
        url = f'{path_url}/{symbol.upper()}-{period}-{current.year}-{current.month:02}-{current.day:02}'
        download_dir = os.path.join(self.download_dir, symbol, self.data_type, self.type, period)

        zip_file = f'{url}.zip'
        check_file = f'{url}.CHECKSUM'
        response1 = self._http_download(zip_file, download_dir)
        response2 = self._http_download(check_file, download_dir)
        response = Response(response1.status)

        response.extend({
            "zip_url": zip_file,
            "zip_file": response1.get('file_path'),
            "check_url": check_file,
            "check_file": response2.get('file_path')
        })

        if response1.status:
            response3 = self._file_unzip(response1.get('file_path'))
            response3.put("file", response3.get('file_path'))
            if delete_zip:
                os.remove(response.get('zip_file'))
            if delete_check:
                os.remove(response.get('check_file'))

        return response

    def download_symbol_period(self, symbol, period, start_date=None, end_date=None, *args, **kwargs) -> tuple:
        if period in ['trades', ]:
            path_url = f'{self.pre_url}/{self.data_type}/{self.type}/{self.freq}/{symbol}'
        else:
            path_url = f'{self.pre_url}/{self.data_type}/{self.type}/{self.freq}/{symbol}/{period}'
        start_date = start_date or self.start_date
        end_date = end_date or self.end_date
        all_res = []
        interval = end_date - start_date
        for index in tqdm(range(interval.days)):
            current = start_date + timedelta(days=index)
            all_res.append(self.download_symbol_period_day(path_url, symbol, period, current, *args, **kwargs))
        all_oks = [response for response in all_res if response.status]
        all_errs = [response for response in all_res if not response.status]
        return all_oks, all_errs

    def download_symbols(self, all_symbols=None, all_periods=None, start_date=None, end_date=None, *args, **kwargs):
        """return date is: [start, end)"""
        self.init_parameters()
        all_symbols = all_symbols or self.all_symbols
        all_periods = all_periods or self.all_periods
        for symbol in all_symbols:
            for period in all_periods:
                all_oks, all_errs = self.download_symbol_period(symbol, period, start_date, end_date, *args, **kwargs)
                logger.warning(f'success:{all_oks}')
                logger.warning(f'failed:{all_errs}')
        logger.info('done')

    def download_klines(self, _type=None, *args, **kwargs):
        """return date is: [start, end)"""
        self.data_type = ALL_DATA_TYPES[0]
        self.type = _type or ALL_TYPES[0]
        self.download_symbols(*args, **kwargs)

    def download_trades(self, _type=None, *args, **kwargs):
        self.type = _type or ALL_TYPES[0]
        self.data_type = ALL_DATA_TYPES[1]
        self.all_periods = ['trades']
        self.download_symbols(*args, **kwargs)


class SymbolManage:
    def __init__(self):
        pass


if __name__ == "__main__":
    history = HistoryDownload(all_symbols=['SHIBUSDT'],
                              all_periods=['1min'],
                              start_date=datetime(2021, 5, 1),
                              end_date=datetime(2021, 5, 23),
                              download_dir='/root/workspace/tmp/data')
    history.download_klines()

    # download_daily_future()
    # download_daily_swap()
    # download_daily_linearswap()
    # download_daily_option(all_period=['1min'])
