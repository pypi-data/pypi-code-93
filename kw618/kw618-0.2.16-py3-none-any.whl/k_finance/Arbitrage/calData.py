"""
导入本模块:
from kw618.k_finance.Arbitrage.calData import *
"""
import multiprocessing
import time
import signal

from kw618._file_path import *
from kw618.k_finance.Arbitrage.binance_gateway import *
from kw618.k_finance.Arbitrage.getData import *

# 自定义信号处理函数 // 很坑, 不用了... (会导致线程管理混乱, 内存溢出等问题...)
# def my_handler(signum, frame):
#     global Ctrl_C_Kill
#     Ctrl_C_Kill = True
#     print("进程被终止")
# signal.signal(signal.SIGINT, my_handler)
# signal.signal(signal.SIGHUP, my_handler)
# signal.signal(signal.SIGTERM, my_handler)
# Ctrl_C_Kill = False # 通过这个全局变量, 让robot捕捉'Ctrl C 的信号' (做好善后工作)

class CalSpreadRobotManager():
    """
    notes:
    """

    def __init__(self):
        """
            notes:
                - 一个程序中, '价差robot'可以有多个, 但是'csrm'最好只有一个, 所有的'价差robot'都放在这一个'csrm'中
            todo:
                - 要实现一键检查所有robot是否还alive的函数
                -
        """
        # 1. 初始化
        self.robots = {} # 存储所有'计算robot'

    def get_spread_symbols(self, assets=[], leftLeg_suffix="USDT_PERP", rightLeg_suffix="USDT"):
        """
            notes:
                - suffix类别:
                    "现货": "USDT"/ "BNB"/ "BUSD"
                    "U本位永续合约": "USDT_PERP"
                    "币本位永续合约": "USD_PERP"
                    "U本位季度合约": "USDT_210625"
                    "币本位季度合约": "USD_210625"

                - 默认的套利对是 "u本位永续价格-现货价格"
        """
        spread_symbols = []
        for asset in assets:
            asset = asset.upper()
            leftLeg_suffix = leftLeg_suffix.upper()
            rightLeg_suffix = rightLeg_suffix.upper()
            leftLeg_name = f"{asset}{leftLeg_suffix}"
            rightLeg_name = f"{asset}{rightLeg_suffix}"
            spread_symbol = f"{leftLeg_name}/{rightLeg_name}"
            spread_symbols.append(spread_symbol)
        return spread_symbols

    def add_robots(self, spread_symbols=["adausd_perp/adausd_210625"], unstoppable_cal=False):
        "添加robot到csrm的同时, 也即刻执行了这个robot"
        for spread_symbol in spread_symbols:
            robot = self.robots.get(spread_symbol, "")
            if robot: # 如果存在该robot, 在原robot上修改
                if robot.alive: # 原robot线程正在运行
                    pass
                    print(f"原本就存在'已经运行的计算robot':{robot}, 无操作...")
                else: # 原robot线程已经停止
                    robot.active()
            else: # 如果不存在该robot, 新建一个robot对象
                robot = CalSpreadRobot(spread_symbol=spread_symbol, unstoppable_cal=unstoppable_cal)
                self.robots.update({spread_symbol:robot})
                robot.active()

    def active_all(self):
        "激活所有价差robot"
        for spread_symbol, robot in self.robots.items():
            robot.active()

    def pause_all(self):
        "暂停所有价差robot"
        for spread_symbol, robot in self.robots.items():
            robot.pause()

    def get_alive_robots(self):
        "获取csrm中活着的robot"
        alive_robots = []
        for spread_symbol, robot in self.robots.items():
            if robot.alive:
                alive_robots.append(robot)
        return alive_robots

    def print(self):
        for spread_symbol, robot in self.robots.items():
            if robot.alive:
                robot.print() # to_print改成了True

    def stop_print(self):
        for spread_symbol, robot in self.robots.items():
            if robot.alive:
                robot.stop_print() # to_print改成了False

    def show_all_threads_is_alive(self):
        "展示所有robot对象的所有子线程是否还活着"
        for spread_symbol, robot in self.robots.items():
            robot.show_all_threads_is_alive()

    def show(self):
        dic = {}
        for spread_symbol, robot in self.robots.items():
            if robot.main_cal_threads:
                main_cal_thread = robot.main_cal_threads[-1]
                main_cal_thread_is_alive = main_cal_thread.is_alive()
            else:
                main_cal_thread_is_alive = None
            if robot.other_cal_threads:
                other_cal_thread = robot.other_cal_threads[-1]
                other_cal_thread_is_alive = other_cal_thread.is_alive()
            else:
                other_cal_thread_is_alive = None
            dic.update({spread_symbol : {'主计算线程':main_cal_thread_is_alive, '周边计算线程':other_cal_thread_is_alive}})
        df = pd.DataFrame(dic)
        return df.T




class CalSpreadRobot():
    """
    notes:
        - 想要获取任意一个币对的价差率, 都需要实例化一个'计算价差率的机器人'
        - MarketDataReceiver的"数据获取"是24小时不间断运行的, 但是CalSpreadRobot的'价差率计算'是需要开平仓才会启动的
    """

    def __init__(self, spread_symbol="adausd_perp/adausd_210625", unstoppable_cal=False, sleep_time=0.7):
        """
            notes:
                - 一个对象只负责一个'币对'的价差率计算 [专一性]
                - spread_symbol: 大小写不敏感;  且有左右腿的概念(价差为:左腿-右腿)
                - 存储在redis中的symbol, 都是大写的
                - redis数据存储方式:
                    - 开/平仓价差率, 时间差, 时间戳, 平均价差率, 都分别存储在不同key里吗? 还是存在同个symbol的key中?

            todo:
                - 要实现一键检查所有robot是否还alive的函数
                - 计算近一段时间的平均价差率 (可以参考vnpy的arrayManager对象)
                - 收集最小挂单量, 小于阈值就不下单!!  (min(leftLeg_volume, rightLeg_volume))
                - 因为我这里计算的价差率会被所有'下单robot'获取, 他们都是依据同一个数据下单, 不免会造成抢单的情况发生!!!
                    解决方案1:
                        使用原来的代码, 每个账户开一个程序来计算价差率
                    解决方案2:
                        提高计算的频次(如0.3s一次), 每个'下单robot'的循环睡眠时间设置成0.5-1.5s的随机数
                            (错开时间下单, 避免多账号同时抢盘口价差)
                            sleep(0.5+get_random_num()) # 0.5s-1.5s
                - 价差率打印的功能, 不应该在计算中, 而应该放到下单机器人下单前打印 (可自行调整需不需要打印...有专门的show模块啊!!)
                    (放在cal模块, 会显得很乱....因为我想放低打印频次就必须降低cal频次, 我想不打印, 就要calrobot杀死)
                - 对所有价差率/费率的df进行排序 (这个功能好像不应该放在这里, 而是要放在'下单模块'来打印吧? '计算模块'就搞得简单一点)


        """
        # 1. 获取左右腿的symbol
        self.spread_symbol = spread_symbol.upper() # eg: "adausd_perp/adausd_210625"
        self.left_leg_symbol = self.spread_symbol.split("/")[0] # 左腿symbol
        self.right_leg_symbol = self.spread_symbol.split("/")[1] # 右腿symbol

        # 2. 初始化必要的参数
        self.alive = False # 表明这个机器人还活着 (活着表示'正在计算中', False表示'没有在计算中', 可以通过active激活继续计算)
        self.unstoppable_cal = unstoppable_cal # 无法阻挡地计算  (极端行情, 需要它义无反顾的计算...)
        self.open_spread_lst = []
        self.r0 = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True) # 0号数据库(用于获取盘口数据)
        self.r1 = redis.StrictRedis(host="localhost", port=6379, db=1, decode_responses=True) # 1号数据库(用于存储价差率数据)
        self.main_cal_threads = [] # 存储所有"主计算"线程
        self.other_cal_threads = [] # 存储所有"周边计算"线程
        self.sleep_time = sleep_time # 每次计算价差率的间隔时间  (睡眠越短, 计算频次越高)
        self.msg = "" # 用于存储需要打印的内容...
        self.to_print = False


    def __repr__(self):
        txt = f"<价差Robot--{self.spread_symbol}>"
        return txt

    def main_cal(self):
        """
            notes:
                - 主要用于计算'价差率'
        """
        try:
            while self.alive:
                # 1. 获取左右腿的实时'挂单信息' (每个腿有6样数据: 买一/卖一价, 买一/卖一量, 服务/接收端时间戳)
                left_leg_dict = self.r0.hgetall(self.left_leg_symbol)
                right_leg_dict = self.r0.hgetall(self.right_leg_symbol)
                if left_leg_dict == {} or right_leg_dict == {}:
                    msg = f"[{self.spread_symbol}]\n"\
                        f"左腿数据: {left_leg_dict};\n"\
                        f"右腿数据: {right_leg_dict};\n"\
                        f"左右腿数据有缺失, 请检查ws数据是否正常推送...\n\n"
                    raise Exception(msg)
                    # i. 左腿数据
                        # 异常处理: 如果获取不到想要的腿数据, float()会自动报错! (所以只要不报错, 每个数据都能正常获取到)
                left_bid_price = float(left_leg_dict.get("bid_price"))
                left_ask_price = float(left_leg_dict.get("ask_price"))
                left_bid_volume = float(left_leg_dict.get("bid_volume"))
                left_ask_volume = float(left_leg_dict.get("ask_volume"))
                # left_receiver_timestamp = float(left_leg_dict.get("receiver_timestamp"))
                left_server_timestamp = float(left_leg_dict.get("server_timestamp", 0))/1000 # 币安的时间戳单位是毫秒
                # 防止现货没有时间戳报错: 临时替代
                # left_server_timestamp = 0 # 币安的时间戳单位是毫秒
                    # ii. 右腿数据
                right_bid_price = float(right_leg_dict.get("bid_price"))
                right_ask_price = float(right_leg_dict.get("ask_price"))
                right_bid_volume = float(right_leg_dict.get("bid_volume"))
                right_ask_volume = float(right_leg_dict.get("ask_volume"))
                # right_receiver_timestamp = float(right_leg_dict.get("receiver_timestamp"))
                right_server_timestamp = float(right_leg_dict.get("server_timestamp", 0))/1000 # 币安的时间戳单位是毫秒
                # 防止现货没有时间戳报错: 临时替代
                # right_server_timestamp = 0 # 币安的时间戳单位是毫秒

                # 2. 计算'时间差' (也是很关键的数据, 关系到捕捉价差的准确性!)
                msg = f"[{self.spread_symbol}]\n"
                msg += f"{left_server_timestamp}; {right_server_timestamp}\n"
                deltaTime_server = abs(left_server_timestamp - right_server_timestamp) # 左右腿的服务端时间差
                    # 计算robot无论发生多少延迟都先不停止运行... (要停止的是'下单robot', 不是计算'robot')
                # deltaTime_left_server_receiver = abs(left_server_timestamp - left_receiver_timestamp) # 左腿服务端和接受端的时间差
                # deltaTime_right_server_receiver = abs(right_server_timestamp - right_receiver_timestamp) # 右腿服务端和接受端的时间差
                # deltaTime_receiver = (deltaTime_left_server_receiver + deltaTime_right_server_receiver)/2 # 接收端的平均时间差
                # cal_timestamp = get_timestamp(arg="now").timestamp()
                # time_bias = abs(((left_receiver_timestamp + right_receiver_timestamp)/2) - cal_timestamp)
                # msg += f"cal时间偏移:{time_bias}\n"
                # if time_bias > 5:
                #     """
                #     notes:
                #         - 发现网络延迟导致时间差大于5s的情况很常见, 程序一下就被报错停止了...要想想解决办法....
                #     """
                #     # msg = f"[时间偏差: {time_bias}秒]\n"
                #     if self.unstoppable_cal:
                #         msg += "设置了'无法阻挡cal', 仍然计算中....(适用于极端行情)\n"
                #         # logger.log(30, msg)
                #     else:
                #         msg += "'数据获取时间'和'当前计算时间'偏差大于5秒, 暂停计算...\n"
                #         self.pause()
                #         raise Exception(msg)

                # 3. 计算'价差率'
                    # i. 开仓的价差率
                open_spread_rate = (left_bid_price - right_ask_price) / right_ask_price
                    # ii. 平仓的价差率
                close_spread_rate = (left_ask_price - right_bid_price) / right_bid_price
                msg += f"开仓价差率:{open_spread_rate:.2%}, 平仓价差率:{close_spread_rate:.2%}, 左右腿时间差:{deltaTime_server:.3f}\n\n"
                self.msg = msg
                if self.to_print:
                    print(self.msg)

                # 4. 存入redis(内存中)
                self.r1.hset(self.spread_symbol, "open_spread_rate", open_spread_rate)
                self.r1.hset(self.spread_symbol, "close_spread_rate", close_spread_rate)
                self.r1.hset(self.spread_symbol, "left_server_timestamp", left_server_timestamp)
                # self.r1.hset(self.spread_symbol, "left_receiver_timestamp", left_receiver_timestamp)
                self.r1.hset(self.spread_symbol, "right_server_timestamp", right_server_timestamp)
                # self.r1.hset(self.spread_symbol, "right_receiver_timestamp", right_receiver_timestamp)
                self.r1.hset(self.spread_symbol, "deltaTime_server", deltaTime_server)
                # self.r1.hset(self.spread_symbol, "deltaTime_receiver", deltaTime_receiver)
                # self.r1.hset(self.spread_symbol, "cal_timestamp", cal_timestamp)

                # 降低计算价差率的频次
                time.sleep(self.sleep_time) # 默认为0.7s

            # 若意外退出循环: 也要执行该停止函数
            self.pause()
        except Exception as e:
            self.pause()
            raise Exception(e)


    def run(self):
        """
            functions:
                - 异步执行 [多线程]
            notes:
                - 参考 k_vnpy的'下单robot', 这里的run和上面的'main_cal'是绑定的
                    (下单robot中只用一个'run'函数来表示, 内部嵌套一个多线程的函数)
                - run函数: 就是'新建一个子线程'来执行计算任务
            notices:
                - run 和 active 的区别:
                    active: 包含了run
                    run: 只是开始了执行 (一般外部调用函数都是调用active, 不是run)

        """
        # 1. 计算价差的核心函数
        t1 = threading.Thread(target=self.main_cal) # 生成一个子线程去跑, 所以不影响主进程的运行
        t1.start()
        self.main_cal_threads.append(t1)

        # 2. 计算平均价差率, 价差率增幅等周边辅助函数..
        # t2 = threading.Thread(target=self.other_cal) # 生成一个子线程去跑, 所以不影响主进程的运行
        # t2.start()
        # self.other_cal_threads.append(t2)


    def active(self):
        """
        notes:
            - 功能:
                (active激活就是'新建一个子线程'来执行计算任务)
            - 非首次执行'计算任务'

            bug:
                pause后再执行active还是不能激活继续计算....
        """
        # 0. 启动该robot
            # 若已经启动, 先杀死原有的robot的执行线程后, 再重建一个新的线程来run
        if self.alive == True:
            self.alive = False # 这里改成False后, 原robot线程会退出'死循环', 从而线程结束生命周期
            time.sleep(0.5) # 给原本就启动的robot线程有足够的时间死亡
        else:
            self.alive = True

        # 1. 新建一个子线程来执行'计算任务'
        self.run()


    def pause(self):
        """
        notes:
            - 功能: 让robot暂时停止cal... 可以通过active继续执行
                - alive参数改成False后, 意味着原来的'计算子线程'就会结束生命
                    (所有这里的pause实际上就是通过'杀死子线程'来pause这个robot; 而active激活就是'新建一个子线程'来执行计算任务)
        """
        # 暂停本robot的计算任务
        self.alive = False

    def show_all_threads_is_alive(self):
        "展示所有子线程是否还活着"
        print(f"{self}")
        print("=================主计算===============")
        for thread in self.main_cal_threads:
            is_alive = thread.is_alive()
            print(f"{thread}: {is_alive}")
        print("=================周边计算===============")
        for thread in self.other_cal_threads:
            is_alive = thread.is_alive()
            print(f"{thread}: {is_alive}")
        print("\n\n")

    def other_cal(self):
        """
            notes:
                - 周边的计算函数...
        """
        pass

    def cal_avg_spread(self):
        """
            notes:
                - 每分钟计算平均价差率
        """
        pass

    def print(self):
        self.to_print = True

    def stop_print(self):
        self.to_print = False



# d1 = r.hgetall("ETCUSDT")
# d2 = r.hgetall("ETCUSDT_PERP")
# spread_symbols = ["rsrUSDT/rsrUSDT_PERP"]
# spread_symbols = ["ankrUSDT/ankrUSDT_PERP", "hntUSDT/hntUSDT_PERP", "1inchUSDT/1inchUSDT_PERP"]
# csrm = CalSpreadRobotManager()
# csrm.add_robots(spread_symbols=spread_symbols, unstoppable_cal=True)


if __name__ == "__main__":

    ba = BinanceAccount(settings=LSH_BINANCE_SETTING)
    mdr = MarketDataReceiver(account_setting=LZC_BINANCE_SETTING)
    csrm = CalSpreadRobotManager()

    assets = KEY_FUTURES_ASSETS
    assets = ["sushi", "cvc", "eth", "lit", "xmr", "alpha", "trx", "dgb", "neo"]
    assets = ["stmx", "mana"]
    assets = ["1inch", "rsr", "etc"]
    assets = ["1inch", "rsr", "etc", "stmx", "mana"]

    # assets = ["1inch"]
    # assets = ["hnt", "storj", "dodo", "chr", "ogn", "blz"]
    assets = ["gtc", "lrc", "icp"]
    assets = ["AXS", "ALICE", "SC"]
    assets = KEY_FUTURES_ASSETS
    assets = ["axs", "bal"]
    assets = ["axs"]
    assets = ["alice"]
    assets = ["avax", "rvn", "iota", "dgb", "zil"]


    # # 现货空, 永续多
    # mdr.connect(assets=assets, connect_types=[1, 2])
    # spread_symbols = csrm.get_spread_symbols(assets=assets, leftLeg_suffix="USDT", rightLeg_suffix="USDT_PERP")
    # csrm.add_robots(spread_symbols=spread_symbols, unstoppable_cal=True)
    # csrm.print()




    # 永续空, 现货多
    mdr.connect(assets=assets, connect_types=[1, 2])
    spread_symbols = csrm.get_spread_symbols(assets=assets, leftLeg_suffix="USDT_PERP", rightLeg_suffix="USDT")
    csrm.add_robots(spread_symbols=spread_symbols, unstoppable_cal=True)
    csrm.print()







    # # 溢价指数
    # assets = KEY_FUTURES_ASSETS
    # mdr.connect(assets=assets, connect_types=[5])
    #
    #
    # for asset in assets:
    #     asset_dict = r0.hgetall(asset+"USDT")
    #     print(f"{asset}\n===\n{asset_dict}")
    #






#
