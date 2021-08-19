import os
import time
import ctypes
import platform
import win32com.client
from pywinauto import application

from .data import CurrentPriceData, AccountData

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class Connector:
    """

    Cybos 서버에 연결하거나 종료하는 명령을 내리는 클래스
    """
    CYBOS_PATH = os.path.join(r'C:\Daishin', 'Starter', 'ncStarter.exe')
    ID = 'HJ3415'
    PASS = 'piyrw421'
    PASSCERT = 'ljgda6421~'

    #  CpUtil.CpCybos - CYBOS의 각종 상태를 확인 할 수 있음.
    CP_CYBOS = win32com.client.Dispatch('CpUtil.CpCybos')

    def __init__(self):
        if not ctypes.windll.shell32.IsUserAnAdmin():
            raise Exception('오류: 일반권한으로 실행됨. 관리자 권한으로 실행해 주세요')
        if not os.path.isfile(self.CYBOS_PATH):
            raise Exception(f'Invalid cybos program path: {self.CYBOS_PATH}')
        if platform.architecture()[0] == '64bit':
            raise Exception('Cybos only support 32bit python..')

    @staticmethod
    def kill_client():
        print("########## 기존 CYBOS 프로세스 강제 종료")
        os.system('taskkill /IM ncStarter* /F /T')
        os.system('taskkill /IM CpStart* /F /T')
        os.system('taskkill /IM DibServer* /F /T')
        os.system('wmic process where "name like \'%ncStarter%\'" call terminate')
        os.system('wmic process where "name like \'%CpStart%\'" call terminate')
        os.system('wmic process where "name like \'%DibServer%\'" call terminate')

    def connect(self):
        if not self.is_connected():
            # 이전에 연결되어 있지 않았다면 아이디 비밀번호를 통해 연결한다.
            self.disconnect()
            self.kill_client()
            print("########## CYBOS 프로세스 자동 접속")
            app = application.Application()
            cybos_args = f' /prj:cp /id:{self.ID} /pwd:{self.PASS} /pwdcert:{self.PASSCERT} /autostart'
            app.start(self.CYBOS_PATH + cybos_args)
            while not self.is_connected():
                # 연결이 완료될 때까지 기다려준다.
                time.sleep(2)
        else:
            logger.info('Cybos is connected already.')

    def disconnect(self):
        if self.is_connected():
            # PlusDisconnect() - Plus 종료.단 종료 API 호출 하더라도 사용하는 응용프로그램을 종료하지 않으면 PLUS 연결 서비스가 유지됩니다.
            self.CP_CYBOS.PlusDisconnect()

    @staticmethod
    def is_connected() -> bool:
        srv_type = {'0': '연결끊김', '1': 'Cybos Plus 서버', '2': 'HTS 보통서버'}
        is_connected = Connector.CP_CYBOS.IsConnect
        if is_connected == 0:
            logger.info("Cybos is not connected..")
            return False
        else:
            logger.info('Cybos is connected..')
            logger.info(f'ServerType : {srv_type[str(Connector.CP_CYBOS.ServerType)]}')
            return True


class PrepareOrder:
    # CpTdUtil - 주문 오브젝트를 사용하기 위해 필요한 초기화 과정들을 수행한다
    CP_TDUTIL = win32com.client.Dispatch('CpTrade.CpTdUtil')

    def __init__(self):
        if self.init_trade():
            if len(self.CP_TDUTIL.AccountNumber) == 1:
                # 사용자의 U-CYBOS로 사인온한 복수계좌목록들을 스트링 배열로 받아온다
                self.acc = self.CP_TDUTIL.AccountNumber[0]
                # 주식상품 구분 - 종합투자상품계좌
                self.acc_flag = self.CP_TDUTIL.GoodsList(self.acc, 1)[0]
                logger.info(f'계좌번호 : {self.acc}, 계좌상품번호 : {self.acc_flag}')
            else:
                raise Exception('Not support multiple account yet.')
        else:
            raise Exception('거래초기화 실패..TradeInit() error')

    @staticmethod
    def init_trade() -> bool:
        # 주문 관련 초기화
        ret_value = {'-1': '오류', '0': '정상', '1': 'OTP/보안카드 키 입력 잘못됨', '3': '취소'}
        r = PrepareOrder.CP_TDUTIL.TradeInit(0)
        if r != 0:
            logger.info(f'Trade initiation error : {ret_value[str(r)]}')
            return False
        else:
            return True


class CurrentPrice:
    """
    CpRPCurrentPrice : 주식 현재가 및 10차 호가 조회
    """
    # DsCbo1.StockMst - 주식 종목의 현재가에 관련된 데이터(10차 호가 포함)
    STOCK_MST = win32com.client.Dispatch("DsCbo1.StockMst")
    # DsCbo1.StockJpBid2 - 주식 종목에 대해 매도,매수에 관한 1차~10차 호가,호가 잔량
    STOCK_JP_BID2 = win32com.client.Dispatch("DsCbo1.StockJpBid2")

    def __init__(self, code):
        self.code = code
        if not Connector.is_connected():
            raise Exception("PLUS가 정상적으로 연결되지 않음.")

    def request(self):
        """
        리턴값이 None 이면 통신에러, 아니면 CurPriceData를 리턴함.
        """
        code = 'A' + self.code
        reply_msg = CurrentPriceData()

        # 현재가 통신
        self.STOCK_MST.SetInputValue(0, code)
        self.STOCK_MST.BlockRequest()

        # 10차 호가 통신
        self.STOCK_JP_BID2.SetInputValue(0, code)
        self.STOCK_JP_BID2.BlockRequest()

        if self.STOCK_MST.GetDibStatus() != 0:
            logger.info(f"통신상태 : {self.STOCK_MST.GetDibStatus()} {self.STOCK_MST.GetDibMsg1()}")
            return None
        if self.STOCK_JP_BID2.GetDibStatus() != 0:
            logger.info(f"통신상태 : {self.STOCK_JP_BID2.GetDibStatus()} {self.STOCK_JP_BID2.GetDibMsg1()}")
            return None

        # 수신 받은 현재가 정보를 rtMst 에 저장
        reply_msg.cur = self.STOCK_MST.GetHeaderValue(11)  # 현재가
        # 10차 호가
        for i in range(10):
            reply_msg.offer.append(self.STOCK_JP_BID2.GetDataValue(0, i))  # 매도호가
            reply_msg.bid.append(self.STOCK_JP_BID2.GetDataValue(1, i))  # 매수호가
        return reply_msg


class AccountInfo:
    # CpTd6033 - 계좌별 잔고 및 주문체결 평가현황 데이터를 요청하고 수신한다.
    CP_TD6033 = win32com.client.Dispatch("CpTrade.CpTd6033")

    def __init__(self):
        if not Connector.is_connected():
            raise Exception("PLUS가 정상적으로 연결되지 않음.")

    def request(self) -> AccountData:
        # 보유 종목 조회
        if not PrepareOrder.init_trade():
            raise Exception("주문 초기화 실패")

        p = PrepareOrder()

        self.CP_TD6033.SetInputValue(0, p.acc)  # 계좌번호
        self.CP_TD6033.SetInputValue(1, p.acc_flag)  # 상품구분 - 주식 상품 중 첫번째
        self.CP_TD6033.SetInputValue(2, 50)  # 요청 건수(최대 50)
        self.CP_TD6033.BlockRequest()

        if self.CP_TD6033.GetDibStatus() != 0:
            logger.info(f"통신상태 : {self.CP_TD6033.GetDibStatus()} {self.CP_TD6033.GetDibMsg1()}")
            return None

        acc_data = AccountData()
        acc_data.acc['계좌명'] = self.CP_TD6033.GetHeaderValue(0)    # 계좌명
        acc_data.acc['결제잔고수량'] = self.CP_TD6033.GetHeaderValue(1)    # 결제잔고수량
        acc_data.acc['체결잔고수량'] = self.CP_TD6033.GetHeaderValue(2)    # 체결잔고수량
        acc_data.acc['총평가금액'] = self.CP_TD6033.GetHeaderValue(3)    # 총평가금액
        acc_data.acc['평가손익'] = self.CP_TD6033.GetHeaderValue(4)    # 평가손익
        acc_data.acc['수익률'] = round(self.CP_TD6033.GetHeaderValue(8),2)    # 수익률
        acc_data.acc['예상예수금'] = self.CP_TD6033.GetHeaderValue(9)    # D+2예상예수금
        cnt = self.CP_TD6033.GetHeaderValue(7)  # 수신개수

        logger.info(f'계좌정보: {acc_data.acc}')
        logger.info(f"투자종목 수신개수: {cnt}")

        if cnt == 0:
            return acc_data
        else:
            for i in range(cnt):
                stock_dict = {
                    '종목코드': self.CP_TD6033.GetDataValue(12, i),
                    '종목명': self.CP_TD6033.GetDataValue(0, i),
                    '체결잔고수량': self.CP_TD6033.GetDataValue(7, i),
                    '매도가능수량': self.CP_TD6033.GetDataValue(15, i),
                    '체결장부단가': self.CP_TD6033.GetDataValue(17, i),
                    '평가금액': self.CP_TD6033.GetDataValue(9, i),
                    '평가손익': self.CP_TD6033.GetDataValue(10, i),
                    '수익률': round(self.CP_TD6033.GetDataValue(11, i), 2),
                }
                acc_data.stocks.append(stock_dict)
            return acc_data


class TradeOrder:
    """
    CpTd0311 - 장내주식/코스닥주식/ELW주문(현금주문) 데이터를 요청하고 수신한다.
    주문에 대한 체결 내역은 CpDib에 있는 CpConclusion object 를 통하여 얻을 수 있습니다.
    """
    CP_TD0311 = win32com.client.Dispatch("CpTrade.CpTd0311")

    def __init__(self, code: str, amount: int, price=None):
        self.code = code
        self.amount = amount
        self.price = price

        if not Connector.is_connected():
            raise Exception("PLUS가 정상적으로 연결되지 않음.")

    def buy(self):
        return self._request('2')

    def sell(self):
        return self._request('1')

    def _request(self, t) -> bool:
        if not PrepareOrder.init_trade():
            raise Exception("주문 초기화 실패")

        p = PrepareOrder()

        # 주식 매수 주문
        self.CP_TD0311.SetInputValue(0, t)  # 2: 매수
        self.CP_TD0311.SetInputValue(1, p.acc)  # 계좌번호
        self.CP_TD0311.SetInputValue(2, p.acc_flag)  # 상품구분 - 주식 상품 중 첫번째
        self.CP_TD0311.SetInputValue(3, 'A' + self.code)  # 종목코드 - A003540
        self.CP_TD0311.SetInputValue(4, self.amount)  # 매수수량
        self.CP_TD0311.SetInputValue(7, "0")  # 주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK

        if self.price is None:
            self.CP_TD0311.SetInputValue(8, '03')  # 주문호가 구분코드 - 01: 보통 03: 시장가
        else:
            self.CP_TD0311.SetInputValue(5, self.price)  # 주문단가
            self.CP_TD0311.SetInputValue(8, '01')  # 주문호가 구분코드 - 01: 보통 03: 시장가

        self.CP_TD0311.BlockRequest()

        if self.CP_TD0311.GetDibStatus() != 0:
            logger.info(f"통신상태 : {self.CP_TD0311.GetDibStatus()} {self.CP_TD0311.GetDibMsg1()}")
            return False

        print("주문종류코드 계좌번호 상품관리구분코드 종목코드 주문수량 주문단가 주문번호 계좌명 종목명 주문조건구분코드 주문호가구분코드")
        h0 = self.CP_TD0311.GetHeaderValue(0)  # 주문종류코드
        h1 = self.CP_TD0311.GetHeaderValue(1)  # 계좌번호
        h2 = self.CP_TD0311.GetHeaderValue(2)  # 상품관리구분코드
        h3 = self.CP_TD0311.GetHeaderValue(3)  # 종목코드
        h4 = self.CP_TD0311.GetHeaderValue(4)  # 주문수량
        h5 = self.CP_TD0311.GetHeaderValue(5)  # 주문단가
        h8 = self.CP_TD0311.GetHeaderValue(8)  # 주문번호
        h9 = self.CP_TD0311.GetHeaderValue(9)  # 계좌명
        h10 = self.CP_TD0311.GetHeaderValue(10)  # 종목명
        h12 = self.CP_TD0311.GetHeaderValue(12)  # 주문조건구분코드
        h13 = self.CP_TD0311.GetHeaderValue(13)  # 주문호가구분코드
        print(h0, h1, h2, h3, h4, h5, h8, h9, h10, h12, h13)
        return True


class InquireOrder:
    """
    CpTd5339 - 계좌별 미체결 잔량 데이터를 요청하고 수신한다. Request/Reply
    """
    CP_TD5339 = win32com.client.Dispatch("CpTrade.CpTd5339")

    def __init__(self):
        if not Connector.is_connected():
            raise Exception("PLUS가 정상적으로 연결되지 않음.")

    def request(self):
        order_datas = []

        if not PrepareOrder.init_trade():
            raise Exception("주문 초기화 실패")

        p = PrepareOrder()

        self.CP_TD5339.SetInputValue(0, p.acc)
        self.CP_TD5339.SetInputValue(1, p.acc_flag)
        self.CP_TD5339.SetInputValue(4, "0")  # 전체
        self.CP_TD5339.SetInputValue(5, "1")  # 정렬 기준 - 역순
        self.CP_TD5339.SetInputValue(6, "0")  # 전체
        self.CP_TD5339.SetInputValue(7, 20)  # 요청 개수 - 최대 20개

        print("[Cp5339] 미체결 데이터 조회 시작")
        # 미체결 연속 조회를 위해 while 문 사용
        while True:
            ret = self.CP_TD5339.BlockRequest()

            if self.CP_TD5339.GetDibStatus() != 0:
                logger.info(f"통신상태 : {self.CP_TD5339.GetDibStatus()} {self.CP_TD5339.GetDibMsg1()}")
                return None

            # 통신 초과 요청 방지에 의한 요류 인 경우
            while ret == 4:  # 연속 주문 오류 임. 이 경우는 남은 시간동안 반드시 대기해야 함.
                remainTime = Connector.CP_CYBOS.LimitRequestRemainTime
                print("연속 통신 초과에 의해 재 통신처리 : ", remainTime / 1000, "초 대기")
                time.sleep(remainTime / 1000)
                ret = self.CP_TD5339.BlockRequest()

            # 수신 개수
            cnt = self.CP_TD5339.GetHeaderValue(5)
            print("[Cp5339] 수신 개수 ", cnt)
            if cnt == 0:
                break

            for i in range(cnt):
                data_one = dict()
                data_one['주문번호'] = self.CP_TD5339.GetDataValue(1, i)
                data_one['원주문번호'] = self.CP_TD5339.GetDataValue(2, i)
                data_one['종목코드'] = self.CP_TD5339.GetDataValue(3, i)
                data_one['종목명'] = self.CP_TD5339.GetDataValue(4, i)
                data_one['주문구분내용'] = self.CP_TD5339.GetDataValue(5, i)
                data_one['주문수량'] = self.CP_TD5339.GetDataValue(6, i)
                data_one['주문단가'] = self.CP_TD5339.GetDataValue(7, i)
                data_one['체결수량'] = self.CP_TD5339.GetDataValue(8, i)
                data_one['신용구분'] = self.CP_TD5339.GetDataValue(9, i)
                data_one['정정취소가능수량'] = self.CP_TD5339.GetDataValue(11, i)
                data_one['매매구분코드'] = self.CP_TD5339.GetDataValue(13, i)
                data_one['대출일'] = self.CP_TD5339.GetDataValue(17, i)
                data_one['주문호가구분코드내용'] = self.CP_TD5339.GetDataValue(19, i)
                data_one['주문호가구분코드'] = self.CP_TD5339.GetDataValue(21, i)

                order_datas.append(data_one)

            # 연속 처리 체크 - 다음 데이터가 없으면 중지
            if not self.CP_TD5339.Continue:
                print("[Cp5339] 연속 조회 여부: 다음 데이터가 없음")
                break
        return order_datas


class CancleOrder:
    """
    CpTd0314 - 취소주문 데이터를 요청하고 수신한다.
    """
    CP_TD0314 = win32com.client.Dispatch("CpTrade.CpTd0314")

    def __init__(self):
        if not Connector.is_connected():
            raise Exception("PLUS가 정상적으로 연결되지 않음.")
        self.order_datas = InquireOrder().request()

    def all(self, code: str):
        acode = 'A' + code
        for order_one in self.order_datas:
            if acode == order_one['종목코드']:
                self._request(order_one['주문번호'], acode)

    def one(self, ordernum: str):
        for order_one in self.order_datas:
            if int(ordernum) == order_one['주문번호']:
                self._request(order_one['주문번호'], order_one['종목코드'])
                break

    def _request(self, ordernum, acode, amount=0):
        # 주식 취소 주문
        p = PrepareOrder()

        print("[CancleOrder]취소주문", ordernum, acode, amount)
        self.CP_TD0314.SetInputValue(1, ordernum)  # 주문 번호 - 정정을 하려는 주문 번호
        self.CP_TD0314.SetInputValue(2, p.acc)  # 상품구분 - 주식 상품 중 첫번째
        self.CP_TD0314.SetInputValue(3, p.acc_flag)  # 상품구분 - 주식 상품 중 첫번째
        self.CP_TD0314.SetInputValue(4, acode)  # 종목코드
        self.CP_TD0314.SetInputValue(5, amount)  # 정정 수량, 0 이면 잔량 취소임

        # 취소주문 요청
        while True:
            ret = self.CP_TD0314.BlockRequest()
            if ret == 0:
                break
            print("[CancleOrder] 주문 요청 실패 ret : ", ret)
            if ret == 4:
                remainTime = Connector.CP_CYBOS.LimitRequestRemainTime
                print("연속 통신 초과에 의해 재 통신처리 : ", remainTime / 1000, "초 대기")
                time.sleep(remainTime / 1000)
                continue
            else:  # 1 통신 요청 실패 3 그 외의 오류 4: 주문요청제한 개수 초과
                return False

        print("[CancleOrder] 주문결과", self.CP_TD0314.GetDibStatus(),
              self.CP_TD0314.GetDibMsg1())
        if self.CP_TD0314.GetDibStatus() != 0:
            return False
        return True
