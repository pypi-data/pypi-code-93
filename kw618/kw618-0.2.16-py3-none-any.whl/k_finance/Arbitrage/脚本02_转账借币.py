from kw618 import *


def transfer_and_loan(asset, transfer_quote_qty, loan_base_qty, loan_times=10, sleep_time=1, account_type="fullMargin"):
    asset = asset.upper()
    symbol = f"{asset}USDT"

    # 1. 转账到杠杆账户
    if transfer_quote_qty:
        if account_type == "fullMargin":
            resp_dict = ba.transfer(account_type="spot", t_type="MAIN_MARGIN", asset="USDT", amount=transfer_quote_qty, symbol=symbol) # 逐仓账户划转
        elif account_type == "isoMargin":
            resp_dict = ba.transfer(account_type="spot", t_type="MAIN_ISOMARGIN", asset="USDT", amount=transfer_quote_qty, symbol=symbol) # 逐仓账户划转
        tranId = resp_dict.get("tranId")
        if tranId:
            msg = f"[转入成功] tranId:{tranId}"
            print(msg)
        elif not tranId:
            msg = f"[转入失败] {transfer_quote_qty}U转入杠杆账户失败; resp_dict:{resp_dict}"
            raise Exception(msg)
    else:
        print("[不需要转入到杠杆账户]")

    # 2. 循环借款
    for _ in range(loan_times):
        print(f"\n尝试第 {_+1} 次借币...")
        resp_dict = ba.loan(account_type=account_type, asset=asset, amount=loan_base_qty, symbol=symbol) # 全仓账户借款
        tranId = resp_dict.get("tranId")
        if tranId:
            # 若借款成功: 退出函数
            print(f"[借币成功] tranId:{tranId}")
            return None # 一旦借到币, 则结束函数
        time.sleep(sleep_time)


    # 3. 若借款失败: 转账回现货账户
    if transfer_quote_qty:
        if account_type == "fullMargin":
            resp_dict = ba.transfer(account_type="spot", t_type="MARGIN_MAIN", asset="USDT", amount=transfer_quote_qty, symbol=symbol) # 逐仓账户划转
        elif account_type == "isoMargin":
            resp_dict = ba.transfer(account_type="spot", t_type="ISOMARGIN_MAIN", asset="USDT", amount=transfer_quote_qty, symbol=symbol) # 逐仓账户划转
        tranId = resp_dict.get("tranId")
        if tranId:
            msg = f"[转出成功] tranId:{tranId}"
            print(msg)
        elif not tranId:
            msg = f"[转出失败] {transfer_quote_qty}U转出现货账户失败; resp_dict:{resp_dict}"
            raise Exception(msg)
    else:
        print("[不需要转出到现货账户]")





def task(asset, transfer_quote_qty, loan_base_qty, account_type, loan_times, sleep_time):
    # 1. 首次立即执行
    transfer_and_loan(
        asset=asset, transfer_quote_qty=transfer_quote_qty, loan_base_qty=loan_base_qty,
        loan_times=loan_times, sleep_time=sleep_time, account_type=account_type,
    )

    # 2. 定时任务
    while True:
        this_time = get_time()

        # 每整分钟打印一次时间
        if this_time[-2:] == "00":
            print(f"\ntime:{this_time}")

        # 每整点执行一遍借币, 看看什么时候能借出来
        if this_time[3:] == "00:00":
            transfer_and_loan(
                asset=asset, transfer_quote_qty=transfer_quote_qty, loan_base_qty=loan_base_qty,
                loan_times=loan_times, sleep_time=sleep_time, account_type=account_type,
            )

        # 睡眠
        time.sleep(1)




if __name__ == "__main__":
    ba = BinanceAccount(settings=LSH_BINANCE_SETTING)


    asset = "axs"
    transfer_quote_qty = 0  # 需要转入逐仓杠杆账户的usdt数量
    loan_base_qty = 200 # 借币数量
    account_type = "isoMargin"
    loan_times = 50
    sleep_time = 5

    # 单次执行
    transfer_and_loan(
        asset=asset, transfer_quote_qty=transfer_quote_qty, loan_base_qty=loan_base_qty,
        loan_times=loan_times, sleep_time=sleep_time, account_type=account_type,
    )

    # # 定时任务
    # task(
    #     asset=asset, transfer_quote_qty=transfer_quote_qty, loan_base_qty=loan_base_qty,
    #     loan_times=loan_times, sleep_time=sleep_time, account_type=account_type,
    # )





#
