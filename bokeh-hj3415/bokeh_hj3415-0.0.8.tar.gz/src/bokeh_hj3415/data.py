import datetime
from db_hj3415 import setting, mongo

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class ForReport:
    """
    c101 구조
    {'date': '2021.05.07',
    '코드': '005930',
    '종목명': '삼성전자',
    '업종': '반도체와반도체장비',
    '주가': '81900',
    '거래량': '14154900',
    'EPS': 0,
    'BPS': 0,
    'PER': None,
    '업종PER': '18.79',
    'PBR': None,
    '배당수익률': '3.66',
    '최고52주': '96800',
    '최저52주': '47200',
    '거래대금': '1158700000000',
    '시가총액': '488925200000000',
    '베타52주': '0.96',
    '발행주식': '5969782550',
    '유통비율': '74.63',
    'intro': '...'}
    """
    def __init__(self, code):
        self.code = code
        logger.debug(setting.load())
        self.c101_list = mongo.C101(code=self.code).get_all()
        logger.info(f'len c101_list: {len(self.c101_list)}')

    def make_x(self) -> list:
        # c101 날짜 데이터로 x축을 만든다.
        date_list = []
        for c101 in self.c101_list:
            c101_date = datetime.datetime.strptime(c101['date'], '%Y.%m.%d')
            date_list.append(c101_date)
        logger.info(f'len date_list: {len(date_list)}')
        return date_list

    def make_y_price(self):
        price_list = []
        for c101 in self.c101_list:
            c101_date = datetime.datetime.strptime(c101['date'], '%Y.%m.%d')
            c101_price = c101['주가']
            price_list.append(float('nan') if c101_price is None else float(c101_price))
        logger.info(f'len price_list: {len(price_list)}')
        logger.info(f'price_list: {price_list}')
        return price_list

    def make_y_dart(self):
        # x축(날짜) 데이터에 맞춰서 dart y축을 만든다.
        dart_list = []
        try:
            darts = mongo.DartByCode(code=self.code).get_data().to_dict('records')
        except KeyError:
            # df 에 내용이 없는 경우
            darts = []
        logger.info(f'len darts:{len(darts)}')

        for c101 in self.c101_list:
            c101_date = datetime.datetime.strptime(c101['date'], '%Y.%m.%d')
            c101_price = c101['주가']
            logger.debug(f'c101_date: {c101_date}, c101_price: {c101_price}')
            is_dart = False

            for dart in darts:
                # c101날짜에 노티한 dart가 있는 경우는 price를 추가한다.
                logger.debug(f'dart: {dart}')
                if datetime.datetime.strptime(dart['rcept_dt'], '%Y%m%d') == c101_date and dart['is_noti'] == 1:
                    dart_list.append(float('nan') if c101_price is None else int(c101_price))
                    is_dart = True
                    break
            if not is_dart:
                # dart가 없는 날에는 nan을 추가한다.
                dart_list.append(float('nan'))

        # dart_list 에는 c101 날짜의 갯수에 맞춰서 nan 또는 당일 주가가 들어감
        logger.info(f'len dart_list: {len(dart_list)}')
        logger.info(f'dart_list: {dart_list}')
        return dart_list

    def make_y_per(self):
        per_list = []
        for c101 in self.c101_list:
            c101_date = datetime.datetime.strptime(c101['date'], '%Y.%m.%d')
            c101_per = c101['PER']
            per_list.append(float('nan') if c101_per is None else float(c101_per))
        logger.info(f'len per_list: {len(per_list)}')
        logger.info(f'per_list: {per_list}')
        return per_list

    def make_y_pbr(self):
        pbr_list = []
        for c101 in self.c101_list:
            c101_date = datetime.datetime.strptime(c101['date'], '%Y.%m.%d')
            c101_pbr = c101['PBR']
            pbr_list.append(float('nan') if c101_pbr is None else float(c101_pbr))
        logger.info(f'len pbr_list: {len(pbr_list)}')
        logger.info(f'pbr_list: {pbr_list}')
        return pbr_list


class ForMarket:
    # col_list = ('aud', 'chf', 'gbond3y', 'gold', 'kosdaq', 'kospi', 'sp500', 'usdkrw', 'wti', 'avgper', 'yieldgap', 'silver')
    def __init__(self):
        logger.debug(setting.load())
        self.mi = mongo.MI()
        self.cols = self.mi.COL_TITLE

    def _make_data(self, col: str) -> tuple:
        """
        리턴값 - 날짜, 값 형식의 튜플
        """
        if col not in self.cols:
            raise ValueError(f'Invalid col : {col}({self.cols})')
        x = []
        y = []
        for d, v in self.mi.get_all_item(index=col):
            logger.info(f'{d} , {v}')
            x.append(datetime.datetime.strptime(d, '%Y.%m.%d'))
            y.append(float('nan') if v is None else float(v))
        return x, y

    def make_kospi(self):
        return self._make_data(col='kospi')

    def make_kosdaq(self):
        return self._make_data(col='kosdaq')

    def make_sp500(self):
        return self._make_data(col='sp500')

    def make_usdkrw(self):
        return self._make_data(col='usdkrw')

    def make_wti(self):
        return self._make_data(col='wti')

    def make_avgper(self):
        return self._make_data(col='avgper')

    def make_yieldgap(self):
        return self._make_data(col='yieldgap')

    def make_gbond3y(self):
        return self._make_data(col='gbond3y')

    def make_gold(self):
        return self._make_data(col='gold')

    def make_silver(self):
        return self._make_data(col='silver')

    def make_gold_silver_ratio(self):
        # 날짜를 key로 하고 금, 은의 값을 리스트 value로 가지는 딕셔너리를 생성한다.
        gold_silver_dict = {}
        for d, v in self.mi.get_all_item(index='gold'):
            gold_silver_dict[d] = [v, ]
        logger.debug(gold_silver_dict)
        for d, v in self.mi.get_all_item(index='silver'):
            gold_silver_dict[d].append(v)
        logger.debug(gold_silver_dict)

        # gold/silver ratio 를 계산하여 날짜, 값 형식의 튜플로 반환한다.
        x = []
        y = []
        for d, v in gold_silver_dict.items():
            if len(v) == 2:
                x.append(datetime.datetime.strptime(d, '%Y.%m.%d'))
                y.append(round(float(v[0]) / float(v[1]), 2))
            else:
                continue
        logger.debug(f'{len(x)} {x}')
        logger.debug(f'{len(y)} {y}')
        return x, y

    def make_aud_chf_ratio(self):
        # 날짜를 key로 하고 chf, aud 값을 리스트 value로 가지는 딕셔너리를 생성한다.
        aud_chf_dict = {}
        for d, v in self.mi.get_all_item(index='chf'):
            aud_chf_dict[d] = [v, ]
        logger.debug(aud_chf_dict)
        for d, v in self.mi.get_all_item(index='aud'):
            aud_chf_dict[d].append(v)
        logger.debug(aud_chf_dict)

        # aud/chf ratio 를 계산하여 날짜, 값 형식의 튜플로 반환한다.
        x = []
        y = []
        for d, v in aud_chf_dict.items():
            if len(v) == 2:
                x.append(datetime.datetime.strptime(d, '%Y.%m.%d'))
                y.append(round(float(v[0]) / float(v[1]), 2))
            else:
                continue
        logger.debug(f'{len(x)} {x}')
        logger.debug(f'{len(y)} {y}')
        return x, y

    def make_dollar_index(self):
        return self._make_data(col='usdidx')
