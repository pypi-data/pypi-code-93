import numpy as np
import fqsdfqsdfqsdfqsd.contracts as contracts
import fqsdfqsdfqsdfqsd.wallets as wallets


class PricingOracle:
    probability_of_default = 0.04
    loss_given_default = 0.5
    discount_rate = 0.05
    n_seconds_year = 31536000

    @classmethod
    def IT_price(cls):
        USDC_repayed = contracts.RepaymentContract.USDC_amount
        credit_outstanding_senior = cls.get_credit_outstanding_senior()
        USDC_deals_senior = cls.get_USDC_deals_senior()
        IT_in_circulation = cls.get_IT_in_circulation()

        if IT_in_circulation == 0:
            price = 1
        else:
            price = (USDC_repayed + USDC_deals_senior + credit_outstanding_senior) / IT_in_circulation

        return price

    @classmethod
    def TVL(cls):
        USDC_repayed = contracts.RepaymentContract.USDC_amount
        credit_outstanding_senior = cls.get_credit_outstanding_senior()
        return USDC_repayed + credit_outstanding_senior

    @classmethod
    def calculate_trailing_APY(cls, price_df):
        price_df['apy'] = ((price_df['IT price'] - price_df.shift(30)['IT price']) / 30) * 365
        price_df["apy"] = cls.hampel(price_df["apy"], 10, 0.3)

        return price_df['apy']

    @staticmethod
    def hampel(vals_orig, k=7, t0=3.0):
        '''
        vals: pandas series of values from which to remove outliers
        k: size of window (including the sample; 7 is equal to 3 on either side of value)
        '''

        # Make copy so original not edited
        vals = vals_orig.copy()

        # Hampel Filter
        L = 1.4826
        rolling_median = vals.rolling(window=k, center=True).median()
        MAD = lambda x: np.median(np.abs(x - np.median(x)))
        rolling_MAD = vals.rolling(window=k, center=True).apply(MAD)
        threshold = t0 * L * rolling_MAD
        difference = np.abs(vals - rolling_median)

        '''
        Perhaps a condition should be added here in the case that the threshold value
        is 0.0; maybe do not mark as outlier. MAD may be 0.0 without the original values
        being equal. See differences between MAD vs SDV.
        '''

        outlier_idx = difference > threshold
        vals[outlier_idx] = rolling_median[outlier_idx]
        return (vals)

    @classmethod
    def get_USDC_deals_senior(cls):
        USDC_deals_senior = 0
        deals = contracts.DealContract.get_instances()
        for deal in deals:
            USDC_deals_senior += deal.senior_tranche_current

        return USDC_deals_senior

    @classmethod
    def get_credit_outstanding(cls):
        credit_outstanding = 0
        deals = contracts.DealContract.get_instances()
        for deal in deals:
            credit_outstanding += deal.credit_outstanding

        return credit_outstanding

    @classmethod
    def get_credit_outstanding_senior(cls):
        credit_outstanding_senior = 0
        deals = contracts.DealContract.get_instances()
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
        investor_wallets = wallets.InvestorWallet.get_instances()
        for investor_wallet in investor_wallets:
            IT_in_circulation += investor_wallet.IT_balance

        return IT_in_circulation
