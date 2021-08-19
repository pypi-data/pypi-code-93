from ....manager.data_tables import StockInfoDataTables
from .reader import (
    read_stock_dividend,
    read_stock_price_sheet,
    read_stock_equity_sheet,
    read_financial_real_publish_date,
    read_balance_sheet,
    read_income_sheet,
    read_income_quarterly_sheet,
    read_cash_flow_sheet,
    read_cash_flow_quarterly_sheet,
)
from .financial_ttm import handle_income_ttm, handle_cash_flow_ttm
from .handle_financial_ratios import compute_ttm_quarterly_ratios
from .handle_prices_ratios import compute_value_ratios
from .compute_ratings import compute_price_ratings, compute_finance_ratings


def init_stock_data(stock_id: str) -> StockInfoDataTables:
    sdt = StockInfoDataTables()
    sdt.balance = read_balance_sheet(stock_id, [])

    sdt.income = read_income_sheet(stock_id, [])
    sdt.income_q = read_income_quarterly_sheet(stock_id, [])
    sdt.income_ttm = handle_income_ttm(sdt.income_q)

    sdt.cash_flow_q = read_cash_flow_quarterly_sheet(stock_id, [])
    sdt.cash_flow_ttm = handle_cash_flow_ttm(sdt.cash_flow_q)

    sdt.dividend = read_stock_dividend(stock_id)
    sdt.prices = read_stock_price_sheet(stock_id)
    sdt.equity = read_stock_equity_sheet(stock_id)
    sdt.real_dates = read_financial_real_publish_date(stock_id)

    return sdt


def clean_up_sdt(sdt: StockInfoDataTables):
    sdt.real_dates = None
    sdt.prices = None
    sdt.dividend = None
    sdt.equity = None


def generate_stock_factor_dict(sdt: StockInfoDataTables):
    sdt.factor_dict = {}

    if len(sdt.values) > 0:
        df = sdt.values
        df = df.sort_index()
        sdt.factor_dict.update(df.iloc[-1].to_dict())
        sdt.factor_dict['评估日期'] = df.index[-1]
    if len(sdt.finance) > 0:
        df = sdt.finance
        df = df.sort_index()
        sdt.factor_dict.update(df.iloc[-1].to_dict())


def compute_stock(param):
    stock_id = param.get('stock_id')
    assert stock_id, 'No stock id'
    try:
        sdt = init_stock_data(stock_id)
        sdt.finance = compute_ttm_quarterly_ratios(sdt)
        sdt.values = compute_value_ratios(sdt)
        sdt.values = compute_price_ratings(sdt.values)
        sdt.finance = compute_finance_ratings(sdt.finance)

        clean_up_sdt(sdt)
        generate_stock_factor_dict(sdt)
        return {stock_id: sdt}
    except Exception:
        import traceback
        print(stock_id)
        print(traceback.format_exc())
        return {}








