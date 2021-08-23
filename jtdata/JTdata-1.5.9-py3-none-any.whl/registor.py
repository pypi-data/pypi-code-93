import json
import os
function_list = [
    "daily", "daily_blocktrade", "daily_derivative_indi", "daily_dividend_rec",
    "daily_l2indicator", "daily_margintrade", "daily_moneyflow", "daily_tech_indicator",
    "daily_yield", "daily_barra_dly_specret", "daily_barra_dly_prices",
    "daily_barra_ashare_exposure", "daily_barra_dly_data", "daily_shsz_stkholding"
]


def regist_TDP(provider):
    path = os.path.join(
        os.path.split(__file__)[0], "TDP.config"
    )
    p = {}
    kwargs = dict(instruments="000001.SZ", fields=None, start_date="2021-07-29", end_date="2021-07-29")
    for function in function_list:
        try:
            df = getattr(provider, function)(**kwargs)
            assert not df.empty
        except:
            df = getattr(provider, function)(instruments="000001.SZ", fields=None, start_date="2020-07-29",
                                             end_date="2021-07-29")
            assert not df.empty
        fields = df.columns.to_list()
        try:
            fields.remove("trade_dt")
        except:
            fields.remove("ann_date")
        fields.remove("code")
        for field in fields:
            if field in p:
                print(function, field)
            p[field] = function
    with open(path, "w") as f:
        json.dump(p, f)
