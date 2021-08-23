from fqsdfqsdfqsdfqsd.tokens import RT
from fqsdfqsdfqsdfqsd.oracles import PricingOracle


class ReserveContract:
    def __init__(self, USDC_max = 10_000_000, compound_apy=0.018):
        self.USDC_max = USDC_max
        self.compound_apy = compound_apy

    def swap_RT_for_IT(self, USDC_amount_needed, deal):
        oldest_RTs = self.find_oldest_RTs()
        for rt in oldest_RTs:
            rt_USDC_amount = rt.USDC_amount
            USDC_amount_needed -= rt_USDC_amount
            if USDC_amount_needed > 0:
                rt.wallet.IT_balance += PricingOracle.USDC_to_IT(rt_USDC_amount)
                deal.senior_tranche_current += rt_USDC_amount
                deal.USDC_balance += rt_USDC_amount
                rt.wallet.RT_balance.remove(rt)
                RT.del_instance(rt)
            else:
                rt.wallet.IT_balance += PricingOracle.USDC_to_IT(USDC_amount_needed + rt_USDC_amount)
                deal.senior_tranche_current += USDC_amount_needed + rt_USDC_amount
                deal.USDC_balance += USDC_amount_needed + rt_USDC_amount
                rt.USDC_amount -= USDC_amount_needed + rt_USDC_amount
                if rt.USDC_amount == 0:
                    RT.del_instance(rt)
                break

    @classmethod
    def get_TV_reserve_pool(cls):
        TV = 0
        RTs = list(RT.get_instances())
        for rt in RTs:
            TV += rt.USDC_amount

        return TV

    @staticmethod
    def fund(USDC_amount, investor_wallet):
        if investor_wallet.USDC_balance < USDC_amount:
            pass
        else:
            # print(f"Investor received RTs for {USDC_amount} USDC")
            reserve_token = RT(USDC_amount, investor_wallet)
            investor_wallet.RT_balance.append(reserve_token)
            investor_wallet.USDC_balance -= USDC_amount

    @staticmethod
    def withdraw(rt, investor_wallet):
        USDC_amount = rt.USDC_amount
        investor_wallet.USDC_balance += USDC_amount
        investor_wallet.RT_balance.remove(rt)

    @staticmethod
    def find_oldest_RTs():
        all_RTs = list(RT.get_instances())

        return sorted(all_RTs, key=lambda x: x.issuance_date)

    # TODO implement compound interest model
    @staticmethod
    def return_daily_interest(self):
        daily_apy = self.compound_apy / 365
        for rt in RT.get_instances():
            accrued_interest = rt.USDC_amount * daily_apy
            rt.wallet.USDC_balance += accrued_interest