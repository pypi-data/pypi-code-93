from fqsdfqsdfqsdfqsd.config import GlobalSettings
from fqsdfqsdfqsdfqsd.tokens import UT
from fqsdfqsdfqsdfqsd.contracts.repayment_contract import RepaymentContract
from fqsdfqsdfqsdfqsd.contracts.reserve_contract import ReserveContract
from dateutil.relativedelta import *

class DealContract:
    _instances = set()

    def __init__(self, reserve_contract, credix_wallet, principal=1_000_000, time_to_maturity=12,
                 financing_fee=0.15, underwriter_fee=0.2, leverage_ratio=4, repay_fraction_interest=1, repay_fraction_principal=1):
        self.reserve_contract = reserve_contract
        self.credix_wallet = credix_wallet
        self.principal = int(principal)
        self.time_to_maturity = int(time_to_maturity) # in months
        self.financing_fee = financing_fee
        self.underwriter_fee = underwriter_fee
        self.leverage_ratio = int(leverage_ratio)
        self.repay_fraction_interest = repay_fraction_interest
        self.repay_fraction_principal = repay_fraction_principal

        self.go_live_date = None
        self.live = False
        self.junior_tranche_current = 0
        self.senior_tranche_open = False
        self.senior_tranche_current = 0
        self.USDC_balance = 0
        self.credit_outstanding = 0
        self.USDC_payout_investors = 0
        self.USDC_payout_underwriters = 0
        self.repayment_schedule = {}

        self._instances.add(self)

    @classmethod
    def get_instances(cls):
        return cls._instances

    @classmethod
    def del_instance(cls, instance):
        cls._instances.remove(instance)

    def set_repayment_schedule(self):
        for i in range(1, self.time_to_maturity + 1):
            repayment_date = GlobalSettings.CLOCK + relativedelta(months=+i)
            self.repayment_schedule[repayment_date.strftime("%Y-%m-%d")] = {
                "repaid": False,
                "principal": False
            }
            if i == self.time_to_maturity:
                self.repayment_schedule[repayment_date.strftime("%Y-%m-%d")] = {
                    "repaid": False,
                    "principal": True
                }

    def investor_interest(self):
        return self.financing_fee * (1 - self.underwriter_fee - GlobalSettings.BRIDGE_FINANCE_FEE)

    def underwriter_interest(self):
        return self.financing_fee * (1 - GlobalSettings.BRIDGE_FINANCE_FEE + self.leverage_ratio * self.underwriter_fee)

    def expected_yield_investors(self):
        return self.investor_interest() * self.senior_tranche_max()

    def expected_yield_underwriters(self):
        return self.underwriter_interest() * self.junior_tranche_max()

    def expected_yield_credix(self):
        return self.principal * self.financing_fee * GlobalSettings.BRIDGE_FINANCE_FEE

    def junior_tranche_max(self):
        return self.principal / (self.leverage_ratio + 1)

    def senior_tranche_max(self):
        return self.principal - self.junior_tranche_max()

    def expected_monthly_interest(self):
        return (self.principal * self.financing_fee) / self.time_to_maturity

    def fund_junior_tranche(self, underwriter_wallet, USDC_amount):
        junior_tranche_max = self.junior_tranche_max()
        if underwriter_wallet.USDC_balance < USDC_amount:
            print('not enough USDC in the underwriter wallet')
        elif self.junior_tranche_current >= junior_tranche_max:
            print("Junior tranche is fully funded")
        elif self.live:
            print("Deal is already live")
        else:
            if USDC_amount >= junior_tranche_max - self.junior_tranche_current:
                amount_to_fund = junior_tranche_max - self.junior_tranche_current
                self.senior_tranche_open = True
                print("Senior tranche is now open")
                print("Filling senior tranche")
                self.fund_senior_tranche()
            else:
                amount_to_fund = USDC_amount
            self.USDC_balance += amount_to_fund
            underwriter_wallet.USDC_balance -= amount_to_fund
            ut = UT(USDC_amount=amount_to_fund, wallet=underwriter_wallet, deal=self)
            underwriter_wallet.UT_balance.append(ut)
            self.junior_tranche_current += amount_to_fund

    def fund_senior_tranche(self):
        # first take funds from repayment pool
        amount_in_repayment_pool = RepaymentContract.USDC_amount
        amount_in_reserve_pool = ReserveContract.get_TV_reserve_pool()

        if self.senior_tranche_max() <= amount_in_repayment_pool + amount_in_reserve_pool:
            if amount_in_repayment_pool >= self.senior_tranche_max():
                RepaymentContract.USDC_amount -= self.senior_tranche_max()
            else:
                self.reserve_contract.swap_RT_for_IT(USDC_amount_needed=self.senior_tranche_max() - amount_in_repayment_pool,
                                                 deal=self)
                RepaymentContract.USDC_amount = 0

            self.go_live_date = GlobalSettings.CLOCK
            self.set_repayment_schedule()
            self.credit_outstanding = self.principal
            self.senior_tranche_current = 0
            self.junior_tranche_current = 0
            self.live = True
            print("The deal is now live")
        else:
            print("Not enough capital in reserve pool")

    def borrow_principal(self):
        self.USDC_balance = 0

    def repay_interest(self, interest_USDC_amount):
        print("-------------")
        print("Incoming interest")
        print(interest_USDC_amount)
        print("-------------")

        # pay out credix first
        expected_credix_interest = interest_USDC_amount * GlobalSettings.BRIDGE_FINANCE_FEE
        if interest_USDC_amount >= expected_credix_interest:
            credix_interest = expected_credix_interest
        else:
            credix_interest = interest_USDC_amount
        self.credix_wallet.USDC_balance += credix_interest
        print(f"payout credix interest: {credix_interest} USDC")

        # pay out investors
        expected_investor_interest = self.financing_fee * self.senior_tranche_max() * (1 - GlobalSettings.BRIDGE_FINANCE_FEE - self.underwriter_fee) / self.time_to_maturity
        if interest_USDC_amount - credix_interest >= expected_investor_interest:
            investor_interest = expected_investor_interest
        else:
            investor_interest = interest_USDC_amount - credix_interest
        RepaymentContract.USDC_amount += investor_interest
        self.USDC_payout_investors += investor_interest
        print(f"payout investors interest: {investor_interest} USDC")

        # pay out underwriters
        underwriters_interest = interest_USDC_amount - credix_interest - investor_interest
        self.USDC_payout_underwriters += underwriters_interest
        for ut in UT.get_instances().copy():
            if ut.deal == self:
                ut.wallet.USDC_balance += ut.USDC_amount / self.junior_tranche_max() * underwriters_interest

        print(f"payout underwriters interest: {underwriters_interest} USDC")
        print("-------------")

    def repay_principal(self, principal_USDC_amount):
        print("-------------")
        print("Incoming principal")
        print(principal_USDC_amount)
        print("-------------")

        # pay out investors first
        expected_payout_investors = self.senior_tranche_max() + self.expected_yield_investors() - self.USDC_payout_investors
        if principal_USDC_amount >= expected_payout_investors:
            payout_investors = expected_payout_investors
        else:
            payout_investors = principal_USDC_amount

        RepaymentContract.USDC_amount += payout_investors
        print("-------------")
        print("payout investors principal")
        print(payout_investors)
        print("-------------")
        # pay out underwriters second
        expected_payout_underwriters = self.junior_tranche_max() + self.expected_yield_underwriters() - self.USDC_payout_underwriters
        actual_payout_underwriters = 0
        if principal_USDC_amount - payout_investors >= expected_payout_underwriters:
            payout_underwriters_percentage = 1
        else:
            payout_underwriters_percentage = max(0, (principal_USDC_amount - payout_investors)/expected_payout_underwriters)

        for ut in UT.get_instances().copy():
            if ut.deal == self:
                USDC_yield = ut.USDC_amount * (1 + self.underwriter_interest()) * payout_underwriters_percentage
                ut.wallet.USDC_balance += USDC_yield
                actual_payout_underwriters += USDC_yield
                ut.wallet.del_UT(ut)
        print("-------------")
        self.credit_outstanding = 0
        self.live = False


