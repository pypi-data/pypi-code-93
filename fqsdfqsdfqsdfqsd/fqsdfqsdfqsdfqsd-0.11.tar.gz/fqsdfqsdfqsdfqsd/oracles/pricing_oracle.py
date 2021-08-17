from fqsdfqsdfqsdfqsd.contracts import RepaymentContract
from fqsdfqsdfqsdfqsd.wallets import InvestorWallet
from fqsdfqsdfqsdfqsd.contracts import DealContract

class PricingOracle:
    probability_of_default = 0.04
    loss_given_default = 0.5
    discount_rate = 0.05
    n_seconds_year = 31536000

    @classmethod
    def IT_price(cls):
        USDC_repayed = RepaymentContract.USDC_amount
        credit_outstanding_senior = cls.get_credit_outstanding_senior()
        USDC_deals_senior = cls.get_USDC_deals_senior()
        IT_in_circulation = cls.get_IT_in_circulation()

        if IT_in_circulation == 0:
            price = 1
        else:
            price = (USDC_repayed + USDC_deals_senior + credit_outstanding_senior) / IT_in_circulation
            # print("----")
            # print(f"USDC_repayed: {USDC_repayed}")
            # print(f"USDC_deals_senior: {USDC_deals_senior}")
            # print(f"credit_outstanding_senior: {credit_outstanding_senior}")
            # print(f"IT_in_circulation: {IT_in_circulation}")
            # print(f"price: {price}")
            # print("---")

        return price

    @classmethod
    def get_USDC_deals_senior(cls):
        USDC_deals_senior = 0
        deals = DealContract.get_instances()
        for deal in deals:
            USDC_deals_senior += deal.senior_tranche_current

        return USDC_deals_senior

    @classmethod
    def get_credit_outstanding_senior(cls):
        credit_outstanding_senior = 0
        deals = DealContract.get_instances()
        for deal in deals:
            credit_outstanding_senior += deal.credit_outstanding * (deal.leverage_ratio / (deal.leverage_ratio + 1))

        return credit_outstanding_senior

    @classmethod
    def USDC_to_IT(cls, USDC_amount):
        return USDC_amount / cls.IT_price()

    @classmethod
    def IT_to_USDC(cls, IT_amount):
        return IT_amount * cls.IT_price()

    @classmethod
    def get_IT_in_circulation(cls):
        IT_in_circulation = 0
        investor_wallets = InvestorWallet.get_instances()
        for investor_wallet in investor_wallets:
            IT_in_circulation += investor_wallet.IT_balance

        return IT_in_circulation

    # @classmethod
    # def PV_all_deals(cls):
    #     PV_all_deals = 0
    #     deals = DealContract.get_instances()
    #     for deal in deals:
    #         if deal.live:
    #             PV_all_deals += cls.PV_one_deal(deal)
    #
    #     return PV_all_deals
    #
    # @classmethod
    # def PV_one_deal(cls, deal):
    #     n_months_till_maturity = cls.diff_month((deal.go_live_date + relativedelta(months=deal.time_to_maturity)), GlobalSettings.CLOCK)
    #     n_seconds_till_maturity = ((deal.go_live_date + relativedelta(months=deal.time_to_maturity)) - GlobalSettings.CLOCK).total_seconds()
    #     payment_for_period = deal.financing_fee * deal.principal / deal.time_to_maturity
    #     future_CF = deal.principal + payment_for_period * n_months_till_maturity
    #     expected_loss = future_CF * (n_months_till_maturity / deal.time_to_maturity) * cls.probability_of_default * cls.loss_given_default
    #     risk_adjusted_future_CF = future_CF - expected_loss
    #     PV = risk_adjusted_future_CF / (1 + cls.discount_rate) ** (n_seconds_till_maturity / cls.n_seconds_year)
    #
    #     if PV < 0:
    #         return 0
    #     else:
    #         return PV
    #
    # @staticmethod
    # def diff_month(d1, d2):
    #     return (d1.year - d2.year) * 12 + d1.month - d2.month