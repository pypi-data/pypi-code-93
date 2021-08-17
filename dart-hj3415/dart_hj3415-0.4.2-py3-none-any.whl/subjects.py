import time
import random
import pprint
import requests
import re
import math
import pandas as pd
import datetime
from bs4 import BeautifulSoup

from db_hj3415 import mongo
from util_hj3415 import utils
from eval_hj3415 import eval
from . import dart


import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.ERROR)


def 유통주식계산(code: str, date: str) -> float:
    """
    c101에서 date에 해당하는 날짜의 유통주식을 계산하고 만약 그날짜가 없으면 최신날짜로 유통주식을 계산한다.\n
    :param code: ex - 005930
    :param date: ex - 20211011
    :return:
    """
    # c101을 통해서 실제 유통주식의 수를 반환한다.
    logger.info('<<< DartIntro.유통주식계산() >>>')
    c101_db = mongo.C101(code=code)
    c101_dict = c101_db.find(date=date)
    if c101_dict is None:
        c101_dict = c101_db.get_recent()

    logger.info(f"{code} {date}")
    logger.info(f'c101 : {c101_dict}')
    logger.info(f"유통비율 : {c101_dict['유통비율']}")
    logger.info(f"발행주식 : {c101_dict['발행주식']}")
    try:
        return round((float(c101_dict['유통비율']) / 100) * float(c101_dict['발행주식']))
    except ValueError:
        return float('nan')


def make_dart_dict(dart_tuple) -> dict:
    """
    데이터프레임의 함수 itertuple로 부터 받은 namedtuple과 c101을 가공하여 딕셔너리를 만들어 반환한다.\n
    <<dict.keys>>\n
    from namedtuple - 'code', 'name', 'rtitle', 'rno', 'rdt', 'url'\n
    from c101 - 'price', 'per', 'pbr', 'high_52w', 'low_52w'\n
    :rtype: dict
    :param dart_tuple: 데이터프레임의 함수 itertuple로 부터 받은 namedtuple
        Pandas(Index=169,
        corp_code='00113234',
        corp_name='대한제당',
        stock_code='001790',
        corp_cls='Y',
        report_nm='주요사항보고서(무상증자결정)',
        rcept_no='20210323000257',
        flr_nm='대한제당',
        rcept_dt='20210323',
        rm='')
    :return: namedtuple과 c101을 가공하여 만든 딕셔너리
        {'code': '001790',
         'name': '대한제당',
         'rtitle': '주요사항보고서(무상증자결정)',
         'rno': '20210323000257',
         'rdt': '20210323',
         'url': 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo=20210323000257',
         'price': 31500,
         'per': None,
         'pbr': None,
         'high_52w': 33200,
         'low_52w': 15300}
    """
    # structure of namedtuple
    # 0:index, 1:corp_code, 2:corp_name, 3:stock_code, 4:corp_cls
    # 5:report_nm, 6:rcept_no, 7:flr_nm, 8:rcept_dt, 9:rm
    intro_dict = dict()
    intro_dict['code'] = dart_tuple.stock_code
    intro_dict['name'] = dart_tuple.corp_name
    intro_dict['rtitle'] = dart_tuple.report_nm
    intro_dict['rno'] = dart_tuple.rcept_no
    intro_dict['rdt'] = dart_tuple.rcept_dt
    intro_dict['url'] = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo=' + str(dart_tuple.rcept_no)

    try:
        c101 = mongo.C101(code=dart_tuple.stock_code).get_recent()
        intro_dict['price'] = int(c101['주가'])
        intro_dict['per'] = float(c101['PER']) if c101['PER'] is not None else None
        intro_dict['pbr'] = float(c101['PBR']) if c101['PBR'] is not None else None
        intro_dict['high_52w'] = int(c101['최고52주'])
        intro_dict['low_52w'] = int(c101['최저52주'])
    except StopIteration:
        # 해당코드의 c101이 없는 경우
        intro_dict['price'] = None
        intro_dict['per'] = None
        intro_dict['pbr'] = None
        intro_dict['high_52w'] = None
        intro_dict['low_52w'] = None
    return intro_dict


def 할인률(high: float, low: float) -> float:
    logger.info(f'high: {high}, low: {low}')
    try:
        return round((high - low) / high * 100)
    except (ZeroDivisionError, ValueError):
        return float('nan')


class DartSubject:
    최소유통주식기준 = 10000000  # 발행주식총수가 천만이하면 유통물량 작은편

    MAX_POINT = 10  # judge()에서 반환하는 포인트 최대점수
    NOTI_POINT = 2  # 알림을 하는 최소포인트
    MIN_POINT = 0

    subtitles = []

    def __init__(self, intro: dict, echo: bool):
        logger.info('<<< DartPage.__init__() >>>')
        self.echo = echo
        self.intro = intro
        """
        {'code' : 017810
        'name' : 풀무원
        'rtitle' : 주요사항보고서(자기주식취득결정)
        'rdt' : 20201230
        'url' : http://dart.fss.or.kr/dsaf001/main.do?rcpNo=20201230000602
        'price' : 17300
        'per' : None
        'pbr' : None
        'high_52w' : 22650
        'low_52w' : 9000}
        """
        self.sub_urls = self.get_sub_urls()  # self.intro['url']을 이용하여 self.sub_urls를 얻어낸다
        self.data = {}
        self.point = self.MIN_POINT
        self.text = ''

    def scoring_유통주식(self):
        # 유통주식이 너무 적으면 감점
        유통주식 = 유통주식계산(self.intro['code'], self.intro['rdt'])
        if 유통주식 <= DartSubject.최소유통주식기준:
            # 유통주식이 너무 작으면...
            self.point -= 1
            self.text += f"유통주식이 너무 작음 : {utils.to_만(유통주식)}주\n"

    def get_sub_urls(self) -> dict:
        """
        self.intro['url']을 이용하여 self.sub_urls를 얻어낸다.
        :return: sub_url 주소를 값으로 하는 딕셔너리
        """
        if self.echo:
            print('(0) Get sub urls...')
        logger.info('<<< get_sub_urls() >>>')
        logger.info(f"init_url : {self.intro['url']}")
        driver = utils.get_driver()
        driver.get(self.intro['url'])
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        sidebar_pages = soup.findAll("span", {'unselectable': "on"})
        sub_urls = {}
        if len(sidebar_pages) == 0:
            # 사이드바가 없는 문서의 경우
            sub_urls['subtitle'] = driver.find_element_by_css_selector('#ifrm').get_attribute('src')
        else:
            for sidebar_page in sidebar_pages:
                logger.info(sidebar_page.string)
                for subtitle in self.subtitles:
                    sidebar_title = str(sidebar_page.string).replace(' ', '')
                    logger.debug(f"compare {sidebar_title} with {subtitle}")
                    if subtitle in sidebar_title:
                        if self.echo:
                            print('.', end='')
                        logger.info(f"Click the sidebar {sidebar_page.string} button...")
                        driver.find_element_by_link_text(sidebar_page.string).click()
                        time.sleep(1)
                        sub_urls[subtitle] = driver.find_element_by_css_selector('#ifrm').get_attribute('src')
                    else:
                        continue
        driver.close()
        if self.echo:
            pprint.pprint(sub_urls)
        return sub_urls

    @staticmethod
    def random_sleep():
        # 너무 빠른속도로 스크래핑하면 dart가 막는다.
        # 랜덤을 추가하여 기본 interval 에 0.5 - 1.5배의 무작위시간을 추가한다.
        interval = 2.5
        logger.info('Wait a moment...')
        time.sleep(interval * (random.random() + .5))

    @staticmethod
    def _ext_data(html, regex_titles: dict, match=None, title_col=0) -> dict:
        """
        html : 최종페이지의 html
        regex_title : 테이블내에서 찾고자하는 타이틀과 찾은 값에 대해 설정할 제목과 위치값
        match :  None일 경우 페이지에서 테이블이 한개인 경우이며 값이 있는 경우는 여러테이블에서 문자열로 한테이블을 찾아내는 것
        title_col : regex_title이 항상 테이블의 맨처음에 위치 하지 않을 경우 iloc의 위치 (0부터 시작)
        """
        logger.info('<<< _ext_data() >>>')
        if match:
            table_df = pd.read_html(html, match=match)[0]
        else:
            table_df = pd.read_html(html)[0]
        return_dict = {}
        logger.debug(f'****** Table No.1 ******')
        logger.debug(table_df)
        for i, (regex_title, ingredient_of_return_dict) in enumerate(regex_titles.items()):
            logger.debug(f'{i + 1}.Extracting..............{regex_title}')
            # 테이블에서 맨처음열의 문자열을 비교하여 필터된 데이터 프레임을 반환한다.
            filtered_df = table_df[table_df.iloc[:, title_col].str.contains(regex_title)]
            logger.info('\n' + filtered_df.to_string())
            try:
                # 원하는 값을 찾기 위해 로그로 확인한다.
                logger.debug(f'iloc[0,0] : {filtered_df.iloc[0, 0]}')
                logger.debug(f'iloc[0,1] : {filtered_df.iloc[0, 1]}')
                logger.debug(f'iloc[0,2] : {filtered_df.iloc[0, 2]}')
                logger.debug(f'iloc[0,3] : {filtered_df.iloc[0, 3]}')
                logger.debug(f'iloc[0,4] : {filtered_df.iloc[0, 4]}')
                logger.debug(f'iloc[0,5] : {filtered_df.iloc[0, 5]}')
            except IndexError:
                pass
            for key, [value_x, value_y] in ingredient_of_return_dict.items():
                try:
                    return_dict[key] = filtered_df.iloc[value_x, value_y]
                except IndexError:
                    logger.warning(f'IndexError : key - {key}, x - {value_x}, y - {value_y}')
                    return_dict[key] = filtered_df.iloc[value_x, value_y - 1]
        logger.info(return_dict)
        return return_dict

    def extract(self):
        if self.echo:
            print('(1) Extracting data from each sub url pages...')

    def process(self):
        if self.echo:
            print('(2) Processing data...')

    def scoring(self):
        if self.echo:
            print('(3) Scoring data...')

    def correcting(self):
        """
        scoring 함수에서 일차적으로 산출한 점수를 보정하는 함수.
        """
        if self.echo:
            print('(4) Correcting data...')
        # 주가가 바닥이라면 보너스 배율
        LOWER_MARGIN = .8
        UPPER_MARGIN = 1.1

        price = self.intro['price']
        low52 = self.intro['low_52w']
        if price <= low52 * LOWER_MARGIN:  # 최근 주가가 바닥이면....
            self.text += f'\n최근 주가({price}원)이 52주최저({low52}원)보다 {(1-LOWER_MARGIN) * 100}% 저렴.'
            correct_rate = 2
        elif (low52 * LOWER_MARGIN) <= price <= (low52 * UPPER_MARGIN):
            self.text += f'\n최근 주가({price}원)이 52주최저({low52}원)근처.'
            correct_rate = 1.5
        else:
            correct_rate = 1

        self.point = self.point * correct_rate

        # red가 주가보다 낮으면 -1 마이너스면 -2
        red = eval.red(code=self.intro['code'])['red_price']
        if 0 > red:
            self.point -= 2
        elif price > red:
            self.point -= 1

        # 점수를 받아서 최대치 이상이나 최소치 이하의 점수가 나오지 않도록 보정한다.
        if DartSubject.MIN_POINT <= self.point <= DartSubject.MAX_POINT:
            self.point = math.ceil(self.point)
        elif DartSubject.MIN_POINT > self.point:
            self.point = DartSubject.MIN_POINT
        elif DartSubject.MAX_POINT < self.point:
            self.point = DartSubject.MAX_POINT
        self.text = self.text if self.text != '' else '큰 의미 없음.'

    def run(self):
        self.extract()      # sub_url에서 데이터들을 추출함.
        self.process()      # 추출된 데이터를 가공하여 변형 또는 추가한다.
        self.scoring()      # 데이터를 판단해서 point와 text를 만든다.
        self.correcting()   # 보정배수 기준에따라 보정한다.

    def __str__(self):
        """
        텔레그렘으로 노티할때 전달되는 형식
        """
        intro_text, data_text = '', ''
        for k, v in self.intro.items():
            if k == 'rno':
                continue
            intro_text += str(k) + ' : ' + str(v) + '\n'
        for k, v in self.data.items():
            data_text += str(k) + ' : ' + str(v) + '\n'
        return str(f'<< intro >>\n'
                   f'{intro_text}\n'
                   f'<< data >>\n'
                   f'{data_text}\n'
                   f'<< result >>\n'
                   f'point : {self.point}\n'
                   f'{self.text}')


def analyse_one_item(subject: str, dart_dict: dict) -> DartSubject:
    subject_cls = globals()[subject](dart_dict)
    subject_cls.run()
    return subject_cls


class 공급계약체결(DartSubject):
    subtitles = []

    def __init__(self, intro: dict, echo=True):
        super().__init__(intro, echo=echo)

    def extract(self):
        super().extract()

        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '공급계약': {'공급계약내용': [0, 2]},
                '계약\\s?금액': {'계약금액': [0, 2]},
                '최근\\s?매출액': {'최근매출액': [0, 2]},
                '매출액\\s?대비': {'매출액대비': [0, 2]},
                '시작일': {'시작일': [0, 2]},
                '종료일': {'종료일': [0, 2]},
                '계약\\s?상대': {'계약상대': [0, 2]},
                '주요\\s?계약\\s?조건': {'주요계약조건': [0, 2]},
            }
            self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles, title_col=1))
            DartSubject.random_sleep()
        if self.echo:
            pprint.pprint(self.data)

    def process(self):
        """
        preprocess ex - self.data
        {'계약금액': '64900000000',
         '계약상대': '(주)포스코건설',
         '공급계약내용': '신안산선 복선전철 민간투자사업 3-2공구',
         '매출액대비': '22.36',
         '시작일': '2021-02-24',
         '종료일': '2025-04-09',
         '주요계약조건': '토공 및 구조물공사',
         '최근매출액': '290210341264'}
        """
        super().process()
        # 문자열 데이터를 읽기 쉬운형태로 가공하는 과정
        self.data['계약상대'] = self.data['계약상대'].replace(' ', '')
        self.data['공급계약내용'] = self.data['공급계약내용'].replace(' ', '')
        self.data['계약금액'] = utils.to_float(self.data['계약금액'])
        self.data['최근매출액'] = utils.to_float(self.data['최근매출액'])
        self.data['계약금액'] = utils.to_억(self.data['계약금액'])
        self.data['최근매출액'] = utils.to_억(self.data['최근매출액'])
        self.data['매출액대비'] = utils.to_float(self.data['매출액대비'])
        self.data['시작일'] = utils.str_to_date(self.data['시작일'])
        self.data['종료일'] = utils.str_to_date(self.data['종료일'])
        if isinstance(self.data['시작일'], datetime.datetime) and isinstance(self.data['종료일'], datetime.datetime):
            self.data['기간'] = (self.data['종료일'] - self.data['시작일']).days
        else:
            self.data['기간'] = None

        if self.echo:
            pprint.pprint(self.data)

    def scoring(self):
        """
        {'계약금액': '649.0억',
         '계약상대': '(주)포스코건설',
         '공급계약내용': '신안산선복선전철민간투자사업3-2공구',
         '기간': 1505,
         '매출액대비': 22.36,
         '시작일': datetime.datetime(2021, 2, 24, 0, 0),
         '종료일': datetime.datetime(2025, 4, 9, 0, 0),
         '주요계약조건': '토공 및 구조물공사',
         '최근매출액': '2902.1억'}
        """
        def cal_comparative_point(big: float, small: float) -> (int, float):
            ratio = ((big / small) - 1) * 100
            a = int(ratio / 10)
            return a if a <= DartSubject.MAX_POINT else DartSubject.MAX_POINT, round(ratio)

        def check_past_contract() -> list:
            """
            연간 반복 공급계약체결의 경우를 파악하기 위해서 1년전 동일공급계약이 있는지 확인하고 동일한 계약을 찾은 경우\n
            해당 data 딕셔너리를 반환한다.
            :return: 정기계약임이 확인된 과거의 data 딕셔너리
            """
            # 해당 기업의 1년전 주변의 보고서를 검색하여 분석함
            # 과거 동일거래를 찾을때 너무 많이 찾아지는 경우를 위해 기본 455일 - 275일 간격에서 5개 이상의 거래 내역일 경우 30일씩 간격을 줄여 다시 검색한다.
            sdate = 365 + 90
            edate = 365 - 90
            print(f'\t- Searching previous dart reports for checking repetitive contract...Day {sdate} to {edate}')
            report_date = datetime.datetime.strptime(self.intro['rdt'], '%Y%m%d')
            df = dart.get_df(sdate=(report_date - datetime.timedelta(days=sdate)).strftime('%Y%m%d'),
                             edate=(report_date - datetime.timedelta(days=edate)).strftime('%Y%m%d'),
                             code=self.intro['code'],
                             title='공급계약체결')
            while len(df) > 5 and (sdate != edate):
                # 날짜 간격을 한달씩 줄여감
                sdate = sdate - 15
                edate = edate + 15
                print(f'\t- Narrowing search range...Day {sdate} to {edate}\t len(df) : {len(df)}')
                df = dart.get_df(sdate=(report_date - datetime.timedelta(days=sdate)).strftime('%Y%m%d'),
                                 edate=(report_date - datetime.timedelta(days=edate)).strftime('%Y%m%d'),
                                 code=self.intro['code'],
                                 title='공급계약체결')
            logger.info(df.to_string())
            return_list = []
            for i, namedtuple in enumerate(df.itertuples()):
                past_subject = 공급계약체결(make_dart_dict(dart_tuple=namedtuple), echo=False)
                past_subject.extract()
                past_subject.process()
                if self.echo:
                    print((f"\t- {i + 1}. Date : {namedtuple.rcept_dt}\t"
                           f"계약상대: {past_subject.data['계약상대']}\t"
                           f"계약내용: {past_subject.data['공급계약내용']}"), end='')
                # 과거 계약이 현계약 상대방과 동일하면 past_contract 리스트에 추가한다.
                if (past_subject.data['계약상대'] == self.data['계약상대']
                        and past_subject.data['공급계약내용'] == self.data['공급계약내용']):
                    if past_subject.data['시작일'].year == past_subject.data['종료일'].year:
                        # 정기계약이면 해가 달라지지 않을 것이므로 년도를 비교해본다.
                        if self.echo:
                            print(f"\t{past_subject.intro['url']}\t===> matching !!!")
                        past_subject.data['date'] = namedtuple.rcept_dt
                        return_list.append(past_subject.data)
                else:
                    if self.echo:
                        print()
            logger.info(f'past_contract - {return_list}')
            return return_list

        def days_to_yd(days: int) -> str:
            # 기간을 정수로 입력받아 몇년 몇일의 문자열로 반환하는 함수
            if days is None or math.isnan(days):
                return ''
            y, d = divmod(days, 365)
            if y == 0:
                return f'{d}일'
            else:
                return f'{y}년 {d}일'

        super().scoring()
        self.scoring_유통주식()

        point, text = 0, ''

        if math.isnan(self.data['매출액대비']):
            text += f"유효하지 않은 매출액대비값 - {self.data['매출액대비']}"
            self.point, self.text = point, text
            return

        # 매출액 대비가 아무리 높더라도 장기계약일 경우는 의미가 없기때문에 계약기간을 고려하여 재계산해본다.
        if self.data['기간'] is None:
            text += f"유효하지 않은 날짜(시작일: {self.data['시작일']} 종료일: {self.data['종료일']})"
            self.point, self.text = point, text
            return
        else:
            min_percentage = round((self.data['기간'] / 365) * 100)
            print(f"\t계약 시작일과 종료일 차이:{self.data['기간']}\t계산된 최소 매출액대비:{min_percentage}")

        # 과거 데이터를 검색하여 유효한 정기공시인지 판단해본다.
        valid_past_contracts = check_past_contract()

        if len(valid_past_contracts) > 0:
            # 과거에 동일 계약상대방이 있었던 정기계약공시면....
            if self.echo:
                print('\t- Comparing with past contract...')
                print(f'\t{valid_past_contracts}')
            for past_one in valid_past_contracts:
                if math.isnan(past_one['매출액대비']):
                    continue
                if self.data['매출액대비'] > past_one['매출액대비']:
                    p, how_much_big = cal_comparative_point(self.data['매출액대비'], past_one['매출액대비'])
                    point += p
                    past_one['시작일'] = utils.date_to_str(past_one['시작일'])
                    past_one['종료일'] = utils.date_to_str(past_one['종료일'])
                    text += f"과거 동일 거래처 계약보다 {how_much_big}% 큰 거래임 : {past_one}"
                else:
                    text += f'과거 동일 거래처 계약보다 작은 거래임 : {past_one}'
        else:
            # 스팟성 공시의 경우
            # 시작일과 종료일의 차를 계산하여 1년이상이면 매출액대비 퍼센트에 반영한다.
            if self.echo:
                print('\t- Analysing spot contract...')
            if self.data['매출액대비'] >= min_percentage:
                p, how_much_big = cal_comparative_point(self.data['매출액대비'], min_percentage)
                point += p
                text += f"공급계약이 기준점({min_percentage}%)보다 {how_much_big}% 큼 : {utils.to_int(self.data['매출액대비'])}%"
            else:
                text += f"공급계약이 기준점({min_percentage}%) 미달 : {utils.to_int(self.data['매출액대비'])}%"
        self.point, self.text = point, text

        # 마무리
        self.data['시작일'] = utils.date_to_str(self.data['시작일'], sep='-')
        self.data['종료일'] = utils.date_to_str(self.data['종료일'], sep='-')
        self.data['기간'] = days_to_yd(self.data['기간'])
        self.data['매출액대비'] = str(utils.to_int(self.data['매출액대비'])) + '%'
        return


class 무상증자결정(DartSubject):
    subtitles = ['무상증자결정', ]

    def __init__(self, intro: dict, echo=True):
        super().__init__(intro, echo=echo)

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '신주의\\s?종류와\\s?수': {'신주의종류와수': [0, 2]},
                '증자전\\s?발행주식총수': {'증자전발행주식총수': [0, 2]},
                '신주\\s?배정\\s?기준일': {'신주배정기준일': [0, 2]},
                '1주당\\s?신주배정\\s?주식수': {'1주당신주배정주식수': [0, 2]},
            }
            self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles, match='증자전\\s?발행주식총수'))
            DartSubject.random_sleep()
        if self.echo:
            pprint.pprint(self.data)

    def process(self):
        """
        preprocess ex - self.data
        {'1주당신주배정주식수': '0.5',
         '신주배정기준일': '2021년 04월 13일',
         '신주의종류와수': '12335217',
         '증자전발행주식총수': '24670435'}
        """
        super().process()
        if self.echo:
            print('\tCalculating 증자전유통주식, 증자후유통주식...')
        self.data['1주당신주배정주식수'] = utils.to_float(self.data['1주당신주배정주식수'])
        self.data['증자전유통주식'] = 유통주식계산(self.intro['code'], self.intro['rdt'])
        self.data['증자전발행주식총수'] = utils.to_float(self.data['증자전발행주식총수'])
        self.data['신주의종류와수'] = utils.to_float(self.data['신주의종류와수'])
        self.data['비유통주식'] = int(self.data['증자전발행주식총수'] - self.data['증자전유통주식'])
        self.data['증자후유통주식'] = int(self.data['증자전발행주식총수'] - self.data['비유통주식'] + self.data['신주의종류와수'])
        self.data['신주배정기준일'] = utils.str_to_date(self.data['신주배정기준일'])
        if self.echo:
            pprint.pprint(self.data)

    def scoring(self):
        """
        {'1주당신주배정주식수': 0.5,
         '비유통주식': 11511225,
         '신주배정기준일': datetime.datetime(2021, 4, 13, 0, 0),
         '신주의종류와수': 12335217.0,
         '증자전발행주식총수': 24670435.0,
         '증자전유통주식': 13159210,
         '증자후유통주식': 25494427}
        """
        super().scoring()
        # self.scoring_유통주식() 사용안함 - 유통주식은 process에서 따로 계산하였음.

        if self.echo:
            print('\tAnalysing 유통주식수 and 주당배정신주...')

        point, text = 0, ''

        NEW_PER_STOCK = 1  # 주당 신주배정 주식수가 의미 있는 최소 기준 주식수

        try:
            if self.data['1주당신주배정주식수'] >= NEW_PER_STOCK:
                point += int(self.data['1주당신주배정주식수'] * 2) \
                    if self.data['1주당신주배정주식수'] * 2 <= DartSubject.MAX_POINT / 2 else DartSubject.MAX_POINT / 2
                text += f"주당배정 신주 : {self.data['1주당신주배정주식수']}.\n"
            else:
                self.point, self.text = DartSubject.MIN_POINT, f"신주배정부족 : {self.data['1주당신주배정주식수']}"
                return

            if self.data['증자전유통주식'] <= DartSubject.최소유통주식기준 <= self.data['증자후유통주식']:
                point += 1
                text += (f"증자후 유통주식 {utils.to_만(DartSubject.최소유통주식기준)}주 이상임 : "
                         f"{utils.to_만(self.data['증자후유통주식'])}주.\n")
            else:
                point -= 1
                text += f"증자후 유통주식 부족: {utils.to_만(self.data['증자후유통주식'])}주.\n"
        except (TypeError, ValueError) as e:
            point = DartSubject.MIN_POINT
            text = e

            # 신주배정기준일 임박여부 판단
            diff_days = (self.data['신주배정기준일'] - datetime.datetime.strptime(self.intro['rdt'], '%Y%m%d')).days
            try:
                # 신주배정기준일이 현재부터 1달이내인 경우..최대 4 포인트
                point += int(120 / diff_days) if int(120 / diff_days) <= 4 else 4
                text += f'신주배정일 {diff_days}일 남음.'
            except ZeroDivisionError:
                point = DartSubject.MIN_POINT
                text = f'신주배정일이 오늘임.'

        self.data['증자전유통주식'] = utils.to_만(self.data['증자전유통주식'])
        self.data['증자전발행주식총수'] = utils.to_만(self.data['증자전발행주식총수'])
        self.data['신주의종류와수'] = utils.to_만(self.data['신주의종류와수'])
        self.data['비유통주식'] = utils.to_만(self.data['비유통주식'])
        self.data['증자후유통주식'] = utils.to_만(self.data['증자후유통주식'])
        self.data['신주배정기준일'] = utils.date_to_str(self.data['신주배정기준일'])
        self.point, self.text = point, text
        return


class 자기주식취득결정(DartSubject):
    subtitles = ['자기주식취득결정', ]

    def __init__(self, intro: dict, echo=True):
        super().__init__(intro, echo=echo)

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '취득\\s?예정\\s?주식\\(주\\)': {'취득예정보통주식': [0, 3], '취득예정기타주식': [1, 3]},
                '취득\\s?목적': {'취득목적': [0, 3]},
                '취득\\s?방법': {'취득방법': [0, 3]},
            }
            self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles, match='취득\\s?예정\\s?주식'))
            DartSubject.random_sleep()
        if self.echo:
            pprint.pprint(self.data)

    def process(self):
        """
        {'취득목적': '주주가치 제고 및 주가안정',
         '취득방법': '코스닥시장을 통한 장내 직접 취득',
         '취득예정기타주식': '-',
         '취득예정보통주식': '400000'}
        """
        super().process()
        self.data['취득예정보통주식'] = utils.to_float(self.data['취득예정보통주식'])
        if math.isnan(self.data['취득예정보통주식']) or math.isnan(self.intro['price']):
            self.data[f'보고일기준취득총액'] = '-'
        else:
            self.data[f'보고일기준취득총액'] = utils.to_억(self.data['취득예정보통주식'] * self.intro['price'])
        유통주식 = 유통주식계산(code=self.intro['code'], date=self.intro['rdt'])
        try:
            self.data['유통주식대비비율'] = round((self.data['취득예정보통주식'] / 유통주식)*100, 2)
        except ZeroDivisionError:
            self.data['유통주식대비비율'] = float('nan')
        if self.echo:
            pprint.pprint(self.data)

    def scoring(self):
        """
        {'보고일기준취득총액': '96.6억',
         '유통주식대비비중': 7,
         '취득목적': '주주가치 제고 및 주가안정',
         '취득방법': '코스닥시장을 통한 장내 직접 취득',
         '취득예정기타주식': '-',
         '취득예정보통주식': 400000.0}
        """
        super().scoring()
        self.scoring_유통주식()
        point, text = 0, ''

        MIN_PCT = 2     # 유통주식의 2% 정도 취득하면 의미있다고 봄

        if math.isnan(self.data['취득예정보통주식']) or '상환전환우선주' in self.data['취득목적']:
            # 상환전환우선주란 우선주 형태로 가지고 있다가 회사에 다시 팔수 있는 권리를 가진 주식
            text += '상환우선주 취득으로 의미없음'
            self.point, self.text = point, text
            return
        if self.data['유통주식대비비율'] >= MIN_PCT:
            point += int(self.data['유통주식대비비율'] - MIN_PCT)
            text += f"유통주식대비비율 의미있음({self.data['유통주식대비비율']}%)(기준:{MIN_PCT}%)"
        else:
            text += f"유통주식대비 너무 적은 취득수량.({self.data['유통주식대비비율']}%)(기준:{MIN_PCT}%)"
        self.point, self.text = point, text
        return


class 주식등의대량보유상황보고서(DartSubject):
    subtitles = ['주식등의대량보유상황보고서', '대량보유자에관한사항', '변동[변경]사유', '변동내역총괄표', '세부변동내역', ]

    def __init__(self, intro: dict, echo=True):
        super().__init__(intro, echo=echo)

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            if '변동[변경]사유' in sidebar_title:
                regex_titles = {
                    '변동\\s?방법': {'변동방법': [0, 1]},
                    '변동\\s?사유': {'변동사유': [0, 1]},
                    '변경\\s?사유': {'변경사유': [0, 1]},
                }
                self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles))
            elif '대량보유상황보고서' in sidebar_title:
                # .* 의미 - 임의의 문자가 0번이상반복
                regex_titles = {
                    '보고\\s?구분': {'보고구분': [0, 1]},
                    '^보유\\s?주식.*보유\\s?비율$': {'직전보고서': [1, 3], '이번보고서': [2, 3]},
                    '보고\\s?사유': {'보고사유': [0, 1]},
                }
                self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles, match='요약\\s?정보'))
            elif '대량보유자에관한사항' in sidebar_title:
                regex_titles = {
                    '보고자\\s?구분': {'보고자구분': [0, 1]},
                    '^성명.*$': {'보고자성명': [0, 2]},
                    '^직업.*$': {'보고자직업': [0, 1]},
                }
                self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles, match='보고자\\s?구분'))
            elif '세부변동내역' in sidebar_title:
                table_df = pd.read_html(html, match='^성명.*$')[0]
                # 추출된 테이블이 하나일 경우
                logger.info(f'****** Table No.1 ******')
                logger.info(table_df)
                try:
                    # 단가가 (1,678) 같은 표시형태일 경우 숫자만 추출
                    self.data['평균단가'] = round(
                        table_df.iloc[:, 8].str.replace(',', '').str.extract('(\\d+)').astype(float).mean(
                            numeric_only=True).iloc[0])
                except AttributeError as e:
                    # 단가가 일반숫자 형태일경우
                    logger.info(f'AttributeError : {e}')
                    self.data['평균단가'] = round(table_df.iloc[:, 8].astype(float).mean())
                except ValueError as e:
                    # 단가가 - 로 표현된 경우
                    logger.info(f'ValueError : {e}')
                    self.data['평균단가'] = '0'
            DartSubject.random_sleep()
        if self.echo:
            pprint.pprint(self.data)

    def process(self):
        """
        {'변경사유': '-',
         '변동방법': '코스닥시장 신규상장',
         '변동사유': '특별관계자 보유주식등 변동(특수관계자 변동 및 주식매수선택권 행사)',
         '보고구분': '변동',
         '보고사유': '특별관계자 보유주식등 변동(특수관계자 변동 및 주식매수선택권 행사)',
         '보고자구분': '개인(국내)',
         '보고자성명': '김효기',
         '보고자직업': '주식회사 셀레믹스 대표이사',
         '이번보고서': '9.84',
         '직전보고서': '11.49',
         '평균단가': 8333}
        """
        super().process()
        self.data['평균단가'] = utils.to_float(self.data['평균단가'])
        self.data['이번보고서'] = utils.to_float(self.data['이번보고서'])
        self.data['직전보고서'] = utils.to_float(self.data['직전보고서'])
        if self.echo:
            pprint.pprint(self.data)

    def scoring(self):
        """
        {'변경사유': '-',
         '변동방법': '코스닥시장 신규상장',
         '변동사유': '특별관계자 보유주식등 변동(특수관계자 변동 및 주식매수선택권 행사)',
         '보고구분': '변동',
         '보고사유': '특별관계자 보유주식등 변동(특수관계자 변동 및 주식매수선택권 행사)',
         '보고자구분': '개인(국내)',
         '보고자성명': '김효기',
         '보고자직업': '주식회사 셀레믹스 대표이사',
         '이번보고서': 9.84,
         '직전보고서': 11.49,
         '평균단가': 8333}
        """
        super().scoring()
        self.scoring_유통주식()

        point, text = 0, ''

        할인율 = 할인률(self.intro['price'], self.data['평균단가'])
        # 할인율이 플러스 -> 주가보다 싸게 샀다. -> 주가가 비싸다

        if self.data['직전보고서'] >= self.data['이번보고서']:
            text += f"주식 보유수량 감소 : {self.data['직전보고서']} -> {self.data['이번보고서']}"
            self.point, self.text = point, text
            return
        elif '전환' in self.data['보고사유'] or '전환' in self.data['변동사유']:
            text += f"전환사채 주식 취득"
            if 할인율 < 0:
                point += int(abs(할인율) / 5) + 1
                text += f"평균단가: {self.data['평균단가']} 주가가 {-할인율}% 저렴"
            self.point, self.text = point, text
            return
        elif '합병신주' in self.data['보고사유'] or '합병신주' in self.data['변동사유']:
            text += f"합병신주 취득"
            if 할인율 < 0:
                point += int(abs(할인율) / 5) + 1
                text += f"평균단가: {self.data['평균단가']} 주가가 {-할인율}% 저렴"
            self.point, self.text = point, text
            return
        elif '상장' in self.data['보고사유'] or '상장' in self.data['변동사유']:
            self.point, self.text = point, text
            return
        elif '유상' in self.data['변동방법'] or '유상' in self.data['변동사유']:
            self.point, self.text = point, text
            return
        elif '잔금지급' in self.data['변동방법'] or '잔금지급' in self.data['변동사유']:
            self.point, self.text = point, text
            return

        if '신규' in self.data['보고구분'] or (self.data['직전보고서'] + 1.0) < self.data['이번보고서']:
            point += 1
            text += f"의미 있는 신규 주식 취득"
            if 할인율 < 0:
                point += int(abs(할인율) / 5) + 1
                text += f", 평균단가: {self.data['평균단가']} 주가가 {-할인율}% 저렴\n"
            if '경영' in self.data['보고사유'] or '경영' in self.data['변동사유']:
                point += DartSubject.MAX_POINT / 2
                text += f", 경영권 위한 주식 취득\n"
        self.point, self.text = point, text
        return


class 특정증권등소유상황보고서(DartSubject):
    subtitles = ['보고자에관한사항', '특정증권등의소유상황', ]

    def __init__(self, intro: dict, echo=True):
        super().__init__(intro, echo=echo)

    def extract(self):
        def refine_합계단가():
            """
            이상한 단가의 예들
            '4,999,998,600( 1주당 1,800'
            '34,813( 주1)'
            '754,000(75,400)'
            '13.01'
            '취득(1,147)'
            """
            s = str(self.data['단가']).replace(' ', '').replace(',', '').replace('1주당', '').replace('주1', '')
            r = r'\d+'
            num_list = re.findall(r, s)
            if len(num_list) == 0:
                # 숫자형식을 추출하지 못했다면...
                num = float('nan')
            elif len(num_list) == 2:
                if (int(num_list[0]) % int(num_list[1])) == 0:
                    # '754,000(75,400)' 의 경우
                    num = float(num_list[1])
                else:
                    # '13.01' 의 소수점의 경우
                    num = float('.'.join(re.findall(r, s)))
            elif len(num_list) == 1:
                num = float(num_list[0])
            else:
                # 기타 - 리스트 아이템 개수가 3개 이상인 경우등...
                num = float('nan')
            self.data['단가'] = num

        def cal_평균단가_manually(html):
            """
            일반적인 방식(합계행에서 단가를 찾는 방식)으로 단가가 계산되지 않는 경우
            각 행의 증감과 단가를 이용하여 계산해 평균단가를 찾아낸다.
            """
            logger.info('<<< _ext_data() >>>')
            table_df = pd.read_html(html, match='^보고사유$')[0]
            logger.info(table_df)
            # 증감(4열)과 단가(6열)의 시리즈
            # 마지막 합계행을 빼기 위해 :-1을 사용하고 에러시 NaN을 반환하기 위해 coerce사용
            증감_s = pd.to_numeric(table_df.iloc[:-1, 4], errors='coerce')
            단가_s = pd.to_numeric(table_df.iloc[:-1, 6], errors='coerce')
            # 각행별로 증감과 단가의 곱셈을한 각각을 전체 더한다.여기에 전체 증감합으로 나누면 평균단가가 계산된다.
            증감_mul_단가 = 증감_s * 단가_s
            logger.info(f'각 행별 증감*단가\n{증감_mul_단가.to_string()}')
            증감합 = 증감_s.sum()
            증감_mul_단가합 = 증감_mul_단가.sum()
            logger.info(f'증감열의 전체합: {증감합}')
            logger.info(f'증감*단가의 전체합: {증감_mul_단가합}')
            try:
                평균단가 = int(증감_mul_단가합/증감합)
            except:
                평균단가 = 0
            logger.info(f"평균단가 : {평균단가}")
            if 평균단가 == 0:
                self.data['단가'] = float('nan')
            else:
                self.data['단가'] = int(증감_mul_단가합/증감합)

        def ext_보고사유(html):
            # 보고사유 항목은 일반적인 방법으로 찾을수 없어서 수동으로 추출한다.
            logger.info('<<< _ext_data() >>>')
            table_df = pd.read_html(html, match='^보고사유$')[0]
            logger.info(table_df)
            # 중복되는 보고사유를 제하기 위해서 unique함수와 집합을 사용한다.
            self.data['보고사유'] = set(table_df.iloc[:-1, 0].unique())

        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            source = requests.get(sub_url).text
            if '보고자에관한사항' in sidebar_title:
                regex_titles = {
                    '임원\\s?\\(등기여부\\)': {'임원': [0, 2]},
                    '주요주주': {'주요주주': [0, 2]},
                }
                self.data.update(DartSubject._ext_data(source, regex_titles=regex_titles, title_col=1))
                regex_titles = {
                    '직위명': {'직위명': [0, 4]},
                }
                self.data.update(DartSubject._ext_data(source, regex_titles=regex_titles, title_col=3))
            elif '특정증권등의소유상황' in sidebar_title:
                regex_titles = {
                    '합\\s?계': {'증감': [0, 4], '단가': [0, 6]},
                }
                self.data.update(DartSubject._ext_data(source, regex_titles=regex_titles, match='^보고사유$'))
                # 보고사유는 위의 일반적인 방법으로 추출할수 없어 개별함수로 제작했다.
                ext_보고사유(source)
                # 찾아낸 합계행의 단가를 숫자형으로 바꿔본다. 만약 숫자형으로 바꿀수 없으면 NAN으로 세팅된다.
                refine_합계단가()
                if math.isnan(self.data['단가']):
                    # 합계행에서 단가를 구할수 없으면 수동으로 각행의 증감과 단가를 계산하여 평균단가를 산출해본다.
                    cal_평균단가_manually(source)
            DartSubject.random_sleep()
        if self.echo:
            pprint.pprint(self.data)

    def process(self):
        """
        {'단가': nan,
         '보고사유': {'신규상장(+)'},
         '임원': '등기임원',
         '주요주주': '사실상지배주주',
         '증감': 871860,
         '직위명': '대표이사'}
        """
        super().process()

        # 단가를 숫자로 업데이트하고 취득처분총액을 계산하여 데이터에 추가한다.

        logger.debug(f"pre to_float - 증감 type: {type(self.data['증감'])}\t value:{self.data['증감']}")
        self.data['증감'] = utils.to_float(self.data['증감'])
        logger.info(f"단가: {self.data['단가']}, 증감: {self.data['증감']}")

        if math.isnan(self.data['단가']):
            # 숫자가 아닌경우 - '-','-(-)'등..
            if self.echo:
                print(f"\tTrying to set 단가... {self.intro['price']}원")
            self.data['취득처분총액'] = round(self.data['증감'] * self.intro['price'], 1)
            # 단가가 숫자가 아닌경우 최근주가를 기반으로 계산하기 때문에 **를 붙여준다.
            self.data['단가'] = str(self.intro['price']) + '**'
        else:
            self.data['취득처분총액'] = utils.to_int(self.data['증감'] * self.data['단가'])

        if self.echo:
            print(f"\t취득처분총액 is calculated: {self.data['취득처분총액']}")
            pprint.pprint(self.data)

    def scoring(self):
        """
        {'단가': '18100**',
         '보고사유': {'신규상장(+)'},
         '임원': '등기임원',
         '주요주주': '사실상지배주주',
         '증감': 871860.0,
         '직위명': '대표이사',
         '취득처분총액': 15780666000.0}
         """

        def check_past_dart() -> list:
            report_date = datetime.datetime.strptime(self.intro['rdt'], '%Y%m%d')
            df = dart.get_df(sdate=(report_date - datetime.timedelta(days=DAYS_AGO)).strftime('%Y%m%d'),
                             edate=(report_date - datetime.timedelta(days=1)).strftime('%Y%m%d'),
                             code=self.intro['code'],
                             title='특정증권등소유상황보고서')
            if self.echo:
                print('\tSearching previous dart reports...')
                print(f'\t최근 {DAYS_AGO}일내 임원공시 수: {len(df)}')
            logger.info(df.to_string())
            return_list = []
            for a, namedtuple in enumerate(df.itertuples()):
                past_subject = 특정증권등소유상황보고서(make_dart_dict(dart_tuple=namedtuple), echo=False)
                past_subject.extract()
                past_subject.process()
                if self.echo:
                    print((f"\t- {a + 1}. Date : {namedtuple.rcept_dt}\t"
                           f"계약상대: {past_subject.data['임원']}\t"
                           f"계약내용: {past_subject.data['취득처분총액']}"), end='')
                if past_subject.data['취득처분총액'] >= MIN_BUYING_COST and past_subject.data['임원'] == '등기임원':
                    past_subject.data['date'] = namedtuple.rcept_dt
                    return_list.append(past_subject.data)
                    if self.echo:
                        print(f"\t{past_subject.intro['url']}\t===> matching !!!", flush=True)
                else:
                    if self.echo:
                        print()
            logger.info(f'past_contract - {return_list}')
            return return_list

        super().scoring()

        self.scoring_유통주식()

        DAYS_AGO = 60  # 등기임원이 1억이상 취득한 케이스 검색 범위 날수
        MIN_BUYING_COST = 100000000  # 등기임원의 최소 주식취득금액 1억

        point, text = 0, ''

        for i in self.data['보고사유']:
            if ('신규상장' in i) or ('주식배당' in i):
                self.point = 0
                self.text = f"보고사유가 {i}임."
                return

        if self.data['취득처분총액'] >= MIN_BUYING_COST and self.data['임원'] == '등기임원':
            # 과거 데이터를 검색하여 유효한 공시인지 판단해본다.
            valid_past_dart = check_past_dart()
            noticeable_case = len(valid_past_dart)

            if noticeable_case > 0:
                point += noticeable_case
                text += f'{DAYS_AGO}일내 {noticeable_case}건 등기임원이 {int(MIN_BUYING_COST / 100000000)}억 이상 취득함\n'
                for past_one in valid_past_dart:
                    text += str(past_one)
            else:
                point += 1
                text += f'등기임원이 {utils.to_억(MIN_BUYING_COST)}이상 취득했으나 최근 {DAYS_AGO}일내 유사 케이스 없음.'
        else:
            text += f"등기임원이 {utils.to_억(MIN_BUYING_COST)} 이상 구매하지 않음."

        self.point, self.text = point, text

        # 마무리
        if math.isnan(self.data['취득처분총액']) or self.data['취득처분총액'] is None:
            pass
        elif self.data['취득처분총액'] == 0:
            self.data['취득처분총액'] = 0
        elif self.data['취득처분총액'] > 0:
            self.data['취득처분총액'] = '취득 ' + utils.to_억(abs(self.data['취득처분총액']))
        else:
            self.data['취득처분총액'] = '처분 ' + utils.to_억(abs(self.data['취득처분총액']))
        self.data['증감'] = str(utils.deco_num(self.data['증감'])) + '주'
        return


class 주식소각결정(DartSubject):
    subtitles = []

    def __init__(self, intro: dict, echo=True):
        super().__init__(intro, echo=echo)

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '소각할\\s?주식의\\s?종류와\\s?수': {'소각할보통주식': [0, 2]},
                '발행주식\\s?총수': {'발행보통주식총수': [0, 2]},
                '소각\\s?예정\\s?금액\\s?\\(원\\)': {'소각예정금액': [0, 2]},
                '소각할\\s?주식의\\s?취득방법': {'소각할주식의취득방법': [0, 2]},
            }
            self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles))
            DartSubject.random_sleep()
        if self.echo:
            pprint.pprint(self.data)

    def process(self):
        """
        {'발행보통주식총수': '117401592',
         '소각예정금액': '4998510065',
         '소각할보통주식': '1895607',
         '소각할주식의취득방법': '기취득 자기주식'}
        """
        super().process()

        self.data['소각할보통주식'] = utils.to_int(self.data['소각할보통주식'])
        self.data['소각예정금액'] = utils.to_float(self.data['소각예정금액'])
        유통주식 = 유통주식계산(code=self.intro['code'], date=self.intro['rdt'])
        self.data['유통주식총수'] = 유통주식
        try:
            self.data['유통주식대비소각비율'] = round((self.data['소각할보통주식'] / 유통주식) * 100, 2)
        except ZeroDivisionError:
            self.data['유통주식대비비율'] = float('nan')
        if math.isnan(self.data['소각예정금액']):
            self.data[f'소각예정금액'] = '-'
        else:
            self.data[f'소각예정금액'] = utils.to_억(self.data[f'소각예정금액'])
        if self.echo:
            pprint.pprint(self.data)

    def scoring(self) -> (int, str):
        """
        {'발행보통주식총수': '117401592',
         '소각예정금액': '50.0억',
         '소각할보통주식': 1895607,
         '소각할주식의취득방법': '기취득 자기주식',
         '유통주식대비소각비율': 5.08,
         '유통주식총수': 37296883}
        """
        super().scoring()

        self.scoring_유통주식()

        point, text = 0, ''

        MIN_PCT = 3  # 유통주식의 3% 정도 소각하면 의미있다고 봄

        if math.isnan(self.data['소각할보통주식']):
            self.point, self.text = DartSubject.MIN_POINT, '주가 제고에 영향 없음'
            return
        elif self.data['소각할보통주식'] > 0:
            point += 1

        if self.data['유통주식대비소각비율'] >= MIN_PCT:
            point += int(self.data['유통주식대비소각비율']) - MIN_PCT
            text += f"유통주식대비 소각비율 의미있음({self.data['유통주식대비소각비율']}%)."
        else:
            text += '소각양 미미함'
        self.point, self.text = point, text

        # 숫자 정리작업
        self.data['발행보통주식총수'] = utils.deco_num(self.data['발행보통주식총수'])
        self.data['소각할보통주식'] = utils.deco_num(self.data['소각할보통주식'])
        self.data['유통주식총수'] = utils.deco_num(self.data['유통주식총수'])
        return


class 현물배당결정(DartSubject):
    subtitles = []

    def __init__(self, intro: dict, echo=True):
        super().__init__(intro, echo=echo)

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '1주당\\s?배당금': {'보통주배당금': [0, 2], '우선주배당금': [1, 2]},
                '배당기준일': {'배당기준일': [0, 2]},
            }
            self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles, match='1주당\\s?배당금'))
            DartSubject.random_sleep()
        if self.echo:
            pprint.pprint(self.data)

    def process(self):
        """
        {'배당기준일': '2020-12-31', '보통주배당금': '300', '우선주배당금': '305'}
        """
        super().process()

        self.data['배당성향'] = mongo.C104(code=self.intro['code'], page='c104y').find(title='현금배당성향(%)')
        self.data['배당기준일'] = utils.str_to_date(self.data['배당기준일'])
        self.data['보통주배당금'] = utils.to_float(self.data['보통주배당금'])
        try:
            self.data['보통주배당률'] = round((self.data['보통주배당금'] / self.intro['price']) * 100, 2)
        except ZeroDivisionError:
            self.data['보통주배당률'] = float('nan')

        if self.echo:
            pprint.pprint(self.data)

    def scoring(self) -> (int, str):
        """
        {'배당기준일': datetime.datetime(2020, 12, 31, 0, 0),
         '보통주배당금': 300.0,
         '보통주배당률': 2.09,
         '우선주배당금': '305'}
         """
        super().scoring()

        self.scoring_유통주식()

        point, text = 0, ''

        MIN_DIV_RATE = 2  # 최하 배당률, 금리에 연동
        MEAN_DIV = 20  # 연평균배당성향
        STD_DIV = 15  # 배당성향표준편차

        logger.info(self.data['배당성향'])
        if self.data['보통주배당률'] >= MIN_DIV_RATE:
            point += math.ceil(self.data['보통주배당률'])
            text += f'배당률 기준({MIN_DIV_RATE}%) 이상.\n'

            # 배당기준일 임박여부 판단
            time_delta = self.data['배당기준일'] - utils.str_to_date(self.intro['rdt'])
            if 0 < int(time_delta.days) <= 30:
                point += 1
                text += f'신주배정일 {int(time_delta.days)}일 남음.\n'

        배당성향_s = pd.Series(self.data['배당성향'])
        if 배당성향_s.mean() >= MEAN_DIV and 배당성향_s.std() <= STD_DIV:
            point += 1
            text += f'과거 일관된 배당성향(평균:{round(배당성향_s.mean())}, 표준편차:{round(배당성향_s.std())})\n'

        self.point, self.text = point, text
        return


class 자산재평가실시결정(DartSubject):
    subtitles = []

    def __init__(self, intro: dict, echo=True):
        super().__init__(intro, echo=echo)

    def extract(self):
        super().extract()
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '재평가\\s?목적물': {'재평가목적물': [0, 1]},
                '재평가\\s?기준일': {'재평가기준일': [0, 1]},
                '장부가액': {'장부가액': [0, 1]},
                '기타\\s?투자판단': {'기타': [0, 1]},
            }
            self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles))
            DartSubject.random_sleep()
        if self.echo:
            pprint.pprint(self.data)

    def process(self):
        super().process()
        # {'재평가목적물': '토지', '재평가기준일': '2020-11-30', '장부가액': '3496760000',
        # '기타': '1. 자산 재평가 목적  -K-IFRS(한국채택국제회계기준)에 의거 자산의 실질가치반영 -자산 및 자본증대 효과를 통한 재무구조 개선  2. 상기 장부가액은 2020년 06월 30일 기준임'}
        self.data['장부가액'] = utils.to_float(self.data['장부가액'])
        c103_자본총계y = mongo.C103(code=self.intro['code'], page='c103재무상태표y').find(title='자본총계')
        if self.echo:
            pprint.pprint(self.data)

    def scoring(self) -> (int, str):
        super().scoring()

        self.scoring_유통주식()

        point, text = 0, ''

        # {'소각할보통주식': '1895607', '소각할종류주식': '-', '발행보통주식총수': '117401592', '발행종류주식총수': '-',
        # '소각예정금액': '4998510065', '소각할주식의취득방법': '기취득 자기주식'}
        return point, text







class 유상증자결정(DartSubject):
    subtitles = ['유상증자결정', ]

    def __init__(self, intro: dict, echo=True):
        super().__init__(intro, echo=echo)

    def extract(self):
        if self.echo:
            print('(1) Extracting data from each sub url pages...')
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            if sidebar_title is None or '유상증자결정' in sidebar_title:
                regex_titles = {
                    '증자\s?방식': {'증자방식': [0, 2]},
                    '신주의\s?종류와\s?수': {'신주보통주식': [0, 3], '신주기타주식': [1, 3]},
                    '증자전\s?발행주식\s?총수\s?\(주\)': {'증자전보통주식총수': [0, 2]},
                }
                self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles, match='신주의\s?종류와\s?수'))

                regex_titles = {
                    '시설\s?자금': {'시설자금': [0, 2]},
                    '운영\s?자금': {'운영자금': [0, 2]},
                    '채무상환자금': {'채무상환자금': [0, 2]},
                    '타법인\s?증권\s?취득\s?자금': {'타법인증권취득자금': [0, 2]},
                }
                self.data.update(
                    DartSubject._ext_data(html, regex_titles=regex_titles, match='신주의\s?종류와\s?수', title_col=1))

                regex_titles = {
                    '신주\s?발행가액': {'신주보통주식발행가': [0, 3], '신주기타주식발행가': [1, 3]},
                }
                self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles, match='신주\s?발행가액'))

                if '3자' in self.data['증자방식']:
                    table_df = pd.read_html(html, match='최대주주\s?와의\s?관계')[0]
                    logger.info(f'****** Table No.1 ******')
                    logger.info(table_df)
                    logger.info(table_df.to_dict('records'))
                    self.data[f'제3자배정대상자'] = table_df.to_dict('records')
            DartSubject.random_sleep()
        if self.echo:
            pprint.pprint(self.data)

    def process(self):
        if self.echo:
            print('(2) Processing data...')
        """
        {'증자방식': '제3자배정증자', 
        '신주보통주식': '-', 
        '신주기타주식': '1325380', 
        '증자전보통주식총수': '30385009', 
        '증자전기타주식총수': '-', 
        '시설자금': '-', 
        '운영자금': '9999992100', 
        '채무상환자금': '-', 
        '타법인증권취득자금': '-', 
        '신주보통주식발행가': '-', 
        '신주기타주식발행가': '7545', 
        '제3자배정대상자': [{'제3자배정 대상자': '(주)뉴그린', 
                            '회사 또는최대주주와의 관계': '-', 
                            '선정경위': '투자자의 의향 및 납입능력, 시기 등을 고려하여 배정 대상자를 선정함', 
                            '증자결정 전후 6월이내 거래내역 및 계획': '-', 
                            '배정주식수 (주)': 662690, 
                            '비 고': '주권교부일로부터 1년간 전량 의무보유예탁할 예정임.'}, 
                        {'제3자배정 대상자': '김형순', 
                            '회사 또는최대주주와의 관계': '-', 
                            '선정경위': '〃', 
                            '증자결정 전후 6월이내 거래내역 및 계획': '-', 
                            '배정주식수 (주)': 662690, 
                            '비 고': '〃'}]}
        """
        self.data['신주보통주식발행가'] = utils.to_float(self.data['신주보통주식발행가'])
        self.data['신주기타주식발행가'] = utils.to_float(self.data['신주기타주식발행가'])
        if math.isnan(self.data['신주보통주식발행가']) and not math.isnan(self.data['신주기타주식발행가']):
            price = self.data['신주기타주식발행가']
        else:
            price = self.data['신주보통주식발행가']
        self.data['할인율'] = 할인률(self.intro['price'], price)
        if self.echo:
            pprint.pprint(self.data)

    def scoring(self) -> (int, str):
        if self.echo:
            print('(3) Judging data...')
        point, text = 0, ''
        """
        {'증자방식': '제3자배정증자', 
        '신주보통주식': '-', 
        '신주기타주식': '1325380', 
        '증자전보통주식총수': '30385009', 
        '증자전기타주식총수': '-', 
        '시설자금': '-', 
        '운영자금': '9999992100', 
        '채무상환자금': '-', 
        '타법인증권취득자금': '-', 
        '신주보통주식발행가': '-', 
        '신주기타주식발행가': '7545', 
        '제3자배정대상자': [{'제3자배정 대상자': '(주)뉴그린', 
                            '회사 또는최대주주와의 관계': '-', 
                            '선정경위': '투자자의 의향 및 납입능력, 시기 등을 고려하여 배정 대상자를 선정함', 
                            '증자결정 전후 6월이내 거래내역 및 계획': '-', 
                            '배정주식수 (주)': 662690, 
                            '비 고': '주권교부일로부터 1년간 전량 의무보유예탁할 예정임.'}, 
                        {'제3자배정 대상자': '김형순', 
                            '회사 또는최대주주와의 관계': '-', 
                            '선정경위': '〃', 
                            '증자결정 전후 6월이내 거래내역 및 계획': '-', 
                            '배정주식수 (주)': 662690, 
                            '비 고': '〃'}]}
        """

        유통주식 = 유통주식계산(self.intro['code'], self.intro['rdt'])
        if 유통주식 <= DartSubject.최소유통주식기준:
            # 유통주식이 너무 작으면...
            point -= 1
            text += f"유통주식이 너무 작음 : {utils.to_만(유통주식)}주\n"

        if '3자' in self.data['증자방식']:
            for target in self.data['제3자배정대상자']:
                # 제3자배정대상자의 키와 밸류의 스페이스를 없애준다.
                target = {k.replace(' ', ''): v for (k, v) in target.items()}
                if '사업제휴' in target['선정경위']:
                    point += 2
                    text += '투자자와 사업제휴.\n'
                    break
                if '투자' in target['제3자배정대상자'] or '자산운용' in target['제3자배정대상자'] or '캐피탈' in target['제3자배정대상자']:
                    point += 1
                    text += '투자를 위한 증자.\n'
                    break
        if self.data['할인율'] < 0:
            point += int(abs(self.data['할인율']) / 5) + 1
            text += f"신주보통주식발행가: {self.data['신주보통주식발행가']} 주가가 {-self.data['할인율']}% 저렴\n"
        try:
            del self.data['제3자배정대상자']
        except KeyError:
            pass
        return DartSubject.final_judge(point, text)


class 매출액또는손익구조(DartSubject):
    subtitles = []

    def __init__(self, intro: dict, echo=True):
        super().__init__(intro, echo=echo)

    def extract(self):
        if self.echo:
            print('(1) Extracting data from each sub url pages...')
        for sidebar_title, sub_url in self.sub_urls.items():
            html = requests.get(sub_url).text
            regex_titles = {
                '매출액\s?\(': {'당해매출액': [0, 2], '직전매출액': [0, 3], '매출액증감액': [0, 4], '매출액증감비율': [0, 5]},
                '영업이익': {'당해영업이익': [0, 2], '직전영업이익': [0, 3], '영업이익증감액': [0, 4], '영업이익증감비율': [0, 5]},
                '당기순이익': {'당해당기순이익': [0, 2], '직전당기순이익': [0, 3], '당기순이익증감액': [0, 4], '당기순이익증감비율': [0, 5]},
                '자본총계': {'당해자본총계': [0, 2], '직전자본총계': [0, 5]},
                '자본금': {'당해자본금': [0, 2], '직전자본금': [0, 5]},
                '이사회\s?\결': {'이사회결의일': [0, 2]},
                '(단위:\s?\w+\s?)': {'단위': [0, 1]},
            }
            self.data.update(DartSubject._ext_data(html, regex_titles=regex_titles, match='변동\s?주요원인'))
            DartSubject.random_sleep()
        if self.echo:
            pprint.pprint(self.data)

    def process(self):
        if self.echo:
            print('(2) Processing data...')
        # {'당해매출액': '26357171', '직전매출액': '23086429', '매출액증감액': '3270742', '매출액증감비율': '14.2',
        # '당해영업이익': '13350363', '직전영업이익': '13968000', '영업이익증감액': '-617637', '영업이익증감비율': '-4.4',
        # '당해당기순이익': '2526240', '직전당기순이익': '5722268', '당기순이익증감액': '-3196028', '당기순이익증감비율': '-55.9',
        # '당해자본총계': '356902452', '직전자본총계': '277959213', '당해자본금': '56330123', '직전자본금': '51630123',
        # '이사회결의일': '2020-12-03', '단위': '2. 매출액 또는 손익구조 변동내용(단위:천원)'}
        for k, v in self.data.items():
            if k == '이사회결의일' or k == '단위' or '증감비율' in k:
                continue
            else:
                self.data[k] = utils.to_float(str(v).replace(' ', ''))
        self.data['직전자본잠식비율'] = round(self.data['직전자본총계'] / self.data['직전자본금'] * 100, 1)
        self.data['당해자본잠식비율'] = round(self.data['당해자본총계'] / self.data['당해자본금'] * 100, 1)
        self.data['단위'] = re.search('단위:(\w?)', self.data['단위'].replace(' ', '')).group().replace('단위:', '')
        if '천' in self.data['단위']:
            self.data['단위'] = 1000
        elif '만' in self.data['단위']:
            self.data['단위'] = 10000
        elif '억' in self.data['단위']:
            self.data['단위'] = 100000000
        elif '원' == self.data['단위']:
            self.data['단위'] = 1
        if self.echo:
            pprint.pprint(self.data)

    def scoring(self) -> (int, str):
        if self.echo:
            print('(3) Judging data...')
        point, text = 0, ''

        유통주식 = 유통주식계산(self.intro['code'], self.intro['rdt'])
        if 유통주식 <= DartSubject.최소유통주식기준:
            # 유통주식이 너무 작으면...
            point -= 1
            text += f"유통주식이 너무 작음 : {utils.to_만(유통주식)}주\n"

        # {'당해매출액': '26357171', '직전매출액': '23086429', '매출액증감액': '3270742', '매출액증감비율': '14.2',
        # '당해영업이익': '13350363', '직전영업이익': '13968000', '영업이익증감액': '-617637', '영업이익증감비율': '-4.4',
        # '당해당기순이익': '2526240', '직전당기순이익': '5722268', '당기순이익증감액': '-3196028', '당기순이익증감비율': '-55.9',
        # '당해자본총계': 356902452.0, '직전자본총계': 277959213.0, '당해자본금': 56330123.0, '직전자본금': 51630123.0,
        # '이사회결의일': '2020-12-03', '직전자본잠식비율': 538, '당해자본잠식비율': 634}

        def 미결정분계산(c103q: dict, this_y_total: float):
            # 보고서 날짜를 기준으로 당해와 직전해의 연도를 찾아낸다.
            c103q = pd.Series(c103q)
            기준일 = datetime.datetime.strptime(self.intro['rdt'], '%Y%m%d')
            올해 = str(기준일.year)
            작년 = str((기준일 - datetime.timedelta(days=365)).year)

            # 올해 결정된 분기만 추려서 합을 낸다.
            올해결정분기_series = c103q[c103q.index.str.contains(str(올해))]
            올해결정치합 = round(올해결정분기_series.sum(), 1)
            # 올해 총합에서 결정된 분기합을 빼서 추정치를 계산한다.
            올해4분기총합 = round(this_y_total * self.data['단위'] / 100000000, 1)
            올해추정치합 = round(올해4분기총합 - 올해결정치합, 1)
            logger.info(f'올해: {올해}, 작년: {작년}, 올해4분기총합: {올해4분기총합}')
            logger.info(c103q.to_dict())
            logger.info(f"올해추정치합({올해추정치합}) = 올해4분기총합({올해4분기총합}) - 올해결정치합({올해결정치합})")

            미결정분기수 = 4 - len(올해결정분기_series)
            작년결정분기_series = c103q[c103q.index.str.contains(str(작년))]
            작년추정치합 = round(작년결정분기_series[-미결정분기수:].sum(), 1)
            logger.info(f"작년추정치합({작년추정치합})")
            try:
                ratio = round(((올해추정치합 - 작년추정치합) / abs(작년추정치합)) * 100, 1)
                logger.info(f"{round(ratio, 1)} = 올해추정치합({올해추정치합}) - 작년추정치합({작년추정치합}) / 작년추정치합({작년추정치합}) * 100")
            except ZeroDivisionError:
                ratio = float('nan')
            return 작년추정치합, 올해추정치합, ratio

        if self.data['직전자본잠식비율'] < 50 <= self.data['당해자본잠식비율']:
            point += 2
            text += '관리종목탈피 요건성립(자본잠식비율 50%이상).'

        # 전체 순이익을 판단하기 보다 직전 분기 또는 미발표 분기를 분석하기 위한 코드

        c103손익계산서q = mongo.C103(code=self.intro['code'], page='c103손익계산서q')

        try:
            c103_매출액q = c103손익계산서q.find(title='매출액(수익)')
            c103_영업이익q = c103손익계산서q.find(title='영업이익')
            c103_당기순이익q = c103손익계산서q.find(title='당기순이익')
        except AttributeError:
            return DartSubject.final_judge(point, text)

        매출액작년추정치합, 매출액올해추정치합, 매출액ratio = 미결정분계산(c103_매출액q, self.data['당해매출액'])
        영업이익작년추정치합, 영업이익올해추정치합, 영업이익ratio = 미결정분계산(c103_영업이익q, self.data['당해영업이익'])
        당기순이익작년추정치합, 당기순이익올해추정치합, 당기순이익ratio = 미결정분계산(c103_당기순이익q, self.data['당해당기순이익'])
        logger.info(f'매출액 : {매출액작년추정치합} {매출액올해추정치합} {매출액ratio}')
        logger.info(f'영업이익 : {영업이익작년추정치합} {영업이익올해추정치합} {영업이익ratio}')
        logger.info(f'당기순이익 : {당기순이익작년추정치합} {당기순이익올해추정치합} {당기순이익ratio}')

        ratios = []
        if not math.isnan(매출액ratio) and not math.isinf(매출액ratio):
            ratios.append(매출액ratio)
        if not math.isnan(영업이익ratio) and not math.isinf(영업이익ratio):
            ratios.append(영업이익ratio)
        if not math.isnan(당기순이익ratio) and not math.isinf(당기순이익ratio):
            ratios.append(당기순이익ratio)
        logger.info(ratios)
        self.data['미발표분증감율'] = ratios

        # 노티하기 불필요한 데이터 정리
        del self.data['당해매출액']
        del self.data['직전매출액']
        del self.data['당해영업이익']
        del self.data['직전영업이익']
        del self.data['당해당기순이익']
        del self.data['직전당기순이익']
        del self.data['당해자본총계']
        del self.data['직전자본총계']
        del self.data['당해자본금']
        del self.data['직전자본금']
        del self.data['단위']

        try:
            avg = round(sum(ratios) / len(ratios), 1)
        except ZeroDivisionError:
            return DartSubject.final_judge(point, text)

        if avg >= 15:
            point += int(avg / 15)
            # 15%이상 변동이 의미 있어서 15로 결정
            text += f'미발표 분기의 평균 {avg}% 재무구조의 개선 있음.'

            temp_1 = utils.to_float(self.data['매출액증감비율'])
            temp_2 = utils.to_float(self.data['영업이익증감비율'])
            temp_3 = utils.to_float(self.data['당기순이익증감비율'])

            tpoint = 0
            if not math.isnan(매출액ratio) and not math.isnan(temp_1):
                if 매출액ratio > temp_1:
                    tpoint += 1
            if not math.isnan(영업이익ratio) and not math.isnan(temp_2):
                if 영업이익ratio > temp_2:
                    tpoint += 1
            if not math.isnan(당기순이익ratio) and not math.isnan(temp_3):
                if 당기순이익ratio > temp_3:
                    tpoint += 1
            if tpoint > 0:
                text += f'미발표 분기 증가율이 발표분보다 높다.'
            point += tpoint
        return DartSubject.final_judge(point, text)


