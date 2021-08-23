from fqsdfqsdfqsdfqsd.wallets import UnderwriterWallet, InvestorWallet, CredixWallet
from fqsdfqsdfqsdfqsd.tokens import UT, RT
from fqsdfqsdfqsdfqsd.contracts import ReserveContract, RepaymentContract, DealContract
from fqsdfqsdfqsdfqsd.config import GlobalSettings
from fqsdfqsdfqsdfqsd.oracles import PricingOracle

import collections
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import pandas as pd

DEFAULT_CONFIG = {
    "underwriters": {
        "amount": 10,
        "USDC_balance": [100000,500000]
    },
    "investors": {
        "amount": 1000,
        "USDC_balance": [4000,5000]
    },
    "deals": [
        {
            "deal_go_live": "2021-02-02",
            "time_to_maturity": 12,
            "principal": 1000000,
            "financing_fee": 0.15,
            "underwriter_fee": 0.2,
            "leverage_ratio": 4,
            "repay_fraction_interest": 1,
            "repay_fraction_principal": 1
        },
        {
            "deal_go_live": "2021-05-05",
            "time_to_maturity": 12,
            "principal": 1000000,
            "financing_fee": 0.15,
            "underwriter_fee": 0.2,
            "leverage_ratio": 4,
            "repay_fraction_interest": 1,
            "repay_fraction_principal": 1
        },
        {
            "deal_go_live": "2021-06-06",
            "time_to_maturity": 12,
            "principal": 1000000,
            "financing_fee": 0.15,
            "underwriter_fee": 0.2,
            "leverage_ratio": 4,
            "repay_fraction_interest": 1,
            "repay_fraction_principal": 1
        }
    ],
    "IT_withdrawals": [
        {
            "withdrawal_date": "2021-03-02",
            "IT_amount": 20000
        }
    ],
    "simulation": {
        "start_date": "2021-01-01",
        "duration_months": 20,
    }
}


class MainSimulation:
    def __init__(self, config=DEFAULT_CONFIG):
        self.config = self.update_config(config)
        self.credix_wallet = CredixWallet()
        self.reserve = ReserveContract()

    def run(self):
        self.reset_clock()
        self.reset_instances()
        self.initialize_actors()

        dates = []
        IT_prices = []
        RT_in_circulation = []
        IT_in_circulation = []
        UT_in_circulation = []
        deal_go_live_and_maturity = []
        withdrawal_dates = []
        repayment_pool = []
        TVL = []
        credit_outstanding = []
        credix_fees = []

        total_seconds = ((GlobalSettings.CLOCK + relativedelta(months=int(self.config["simulation"]["duration_months"]))) - GlobalSettings.CLOCK).total_seconds()
        total_days = int(total_seconds/(3600*24))
        date_str_old = "abc"
        for i in range(0, total_days):
            date_str = GlobalSettings.CLOCK.strftime("%Y-%m-%d")
            if date_str != date_str_old:
                # make repayments for deals
                for deal in DealContract.get_instances():
                    if deal.live:
                        self.make_repayment(deal, date_str)

                # launch and fund deal
                for deal_config in self.config["deals"]:
                    if deal_config["deal_go_live"] == date_str:
                        print("-----------------")
                        print("Initializing deal")
                        print("-----------------")
                        deal = self.initialize_deal(deal_config)
                        if deal.live:
                            go_live_date = GlobalSettings.CLOCK.strftime("%Y-%m-%d")
                            maturity_date = (GlobalSettings.CLOCK + relativedelta(months=int(deal.time_to_maturity))).strftime("%Y-%m-%d")
                            deal_go_live_and_maturity.append([go_live_date, maturity_date])

                # check if withdrawal needs to take place
                for withdrawal_config in self.config["IT_withdrawals"]:
                    if withdrawal_config["withdrawal_date"] == date_str:
                        print("-----------------")
                        print("withdrawing")
                        print("-----------------")
                        InvestorWallet.withdraw_IT(withdrawal_config["IT_amount"], self.reserve)
                        withdrawal_dates.append(withdrawal_config["withdrawal_date"])

                date_str_old = date_str

            # if GlobalSettings.CLOCK.month != current_month:
            dates.append(GlobalSettings.CLOCK.strftime("%Y-%m-%d"))
            IT_prices.append(PricingOracle.IT_price())
            RT_in_circulation.append(RT.get_RT_in_circulation())
            IT_in_circulation.append(PricingOracle.get_IT_in_circulation())
            UT_in_circulation.append(UT.get_UT_in_circulation())
            repayment_pool.append(RepaymentContract.USDC_amount)
            TVL.append(PricingOracle.TVL())
            credit_outstanding.append(PricingOracle.get_credit_outstanding())
            credix_fees.append(self.credix_wallet.USDC_balance)

            GlobalSettings.CLOCK += timedelta(seconds=3600 * 24)

        simulation_df = pd.DataFrame.from_dict({"date": dates, "IT price": IT_prices, "RT": RT_in_circulation, "IT": IT_in_circulation,
                                "UT": UT_in_circulation, "repayment pool": repayment_pool, "TVL": TVL, "credit outstanding": credit_outstanding,
                                                "credix fees": credix_fees})

        simulation_df["APY 30d trailing"] = PricingOracle.calculate_trailing_APY(simulation_df[["IT price"]])

        return simulation_df, deal_go_live_and_maturity, withdrawal_dates

    def reset_clock(self):
        GlobalSettings.CLOCK = datetime.strptime(self.config["simulation"]["start_date"], "%Y-%m-%d")


    @staticmethod
    def reset_instances():
        for deal in DealContract.get_instances().copy():
            DealContract.del_instance(deal)
        for wallet in InvestorWallet.get_instances().copy():
            InvestorWallet.del_instance(wallet)
        for wallet in UnderwriterWallet.get_instances().copy():
            UnderwriterWallet.del_instance(wallet)
        for wallet in CredixWallet.get_instances().copy():
            CredixWallet.del_instance(wallet)
        for rt in RT.get_instances().copy():
            RT.del_instance(rt)
        for ut in UT.get_instances().copy():
            UT.del_instance(ut)
        RepaymentContract.USDC_amount = 0


    @staticmethod
    def make_repayment(deal, date_str):
        if date_str in deal.repayment_schedule:
            interest_amount = deal.principal * deal.financing_fee / deal.time_to_maturity
            if not deal.repayment_schedule[date_str]["repaid"] and not deal.repayment_schedule[date_str]["principal"]:
                deal.repayment_schedule[date_str]["repaid"] = True
                deal.repay_interest(interest_amount * deal.repay_fraction_interest)
            elif not deal.repayment_schedule[date_str]["repaid"] and deal.repayment_schedule[date_str]["principal"]:
                deal.repayment_schedule[date_str]["repaid"] = True
                deal.repay_interest(interest_amount * deal.repay_fraction_interest)
                deal.repay_principal(deal.principal * deal.repay_fraction_principal)
        else:
            pass

    def initialize_actors(self):
        random.seed(123)
        self.initialize_investors()
        self.initialize_underwriters()

    def initialize_investors(self):
        for i in range(0, self.config["investors"]["amount"]):
            min_USDC_balance = self.config["investors"]["USDC_balance"][0]
            max_USDC_balance = self.config["investors"]["USDC_balance"][1]
            InvestorWallet(USDC_balance=random.randint(min_USDC_balance, max_USDC_balance))

        for investor_wallet in InvestorWallet.get_instances():
            self.reserve.fund(USDC_amount=investor_wallet.USDC_balance, investor_wallet=investor_wallet)

    def initialize_underwriters(self):
        for i in range(0, self.config["underwriters"]["amount"]):
            min_USDC_balance = self.config["underwriters"]["USDC_balance"][0]
            max_USDC_balance = self.config["underwriters"]["USDC_balance"][1]
            UnderwriterWallet(USDC_balance=random.randint(min_USDC_balance, max_USDC_balance))

    def initialize_deal(self, deal_config):
            deal_config_new = deal_config.copy()
            deal_config_new.pop("deal_go_live")
            deal = DealContract(**deal_config_new, reserve_contract=self.reserve, credix_wallet=self.credix_wallet)
            for underwriter_wallet in UnderwriterWallet.get_instances():
                if not deal.senior_tranche_open:
                    deal.fund_junior_tranche(underwriter_wallet=underwriter_wallet, USDC_amount=int(deal.principal/4))
            return deal

    def update_config(self, config):
        return self.update_dict(DEFAULT_CONFIG, config)

    def update_dict(self, d, u):
        for k, v in u.items():
            if isinstance(d, collections.Mapping):
                if isinstance(v, collections.Mapping):
                    r = self.update_dict(d.get(k, {}), v)
                    d[k] = r
                else:
                    d[k] = u[k]
            else:
                d = {k: u[k]}
        return d
