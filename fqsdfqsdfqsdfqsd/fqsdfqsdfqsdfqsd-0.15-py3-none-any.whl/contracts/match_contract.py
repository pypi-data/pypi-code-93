from fqsdfqsdfqsdfqsd.contracts import RepaymentContract, ReserveContract
from fqsdfqsdfqsdfqsd.oracles import PricingOracle
from fqsdfqsdfqsdfqsd.tokens import RT


class MatchContract:
    @classmethod
    def withdraw_IT(cls, IT_amount, investor_wallet, reserve):
        if IT_amount > investor_wallet.IT_balance:
            print("-----------------")
            print("you try to withdraw more IT than you have in your wallet")
            print("-----------------")
        else:
            USDC_amount = PricingOracle.IT_to_USDC(IT_amount)
            USDC_amount_to_swap = USDC_amount
            current_IT_price = PricingOracle.IT_price()

            # first swap reserve tokens for IT's
            # update RT holders' wallets IT and USDC balances + burn RT's
            oldest_RTs = reserve.find_oldest_RTs()
            for rt in oldest_RTs:
                RT_USDC_amount = rt.USDC_amount
                if USDC_amount_to_swap - RT_USDC_amount >= 0:
                    print("-----------------")
                    print(f"swapping and burning RT worth {RT_USDC_amount} USDC")
                    print("-----------------")
                    rt.wallet.IT_balance += RT_USDC_amount / current_IT_price
                    investor_wallet.IT_balance -= RT_USDC_amount / current_IT_price
                    RT.del_instance(rt)
                    investor_wallet.USDC_balance += RT_USDC_amount
                    USDC_amount_to_swap -= RT_USDC_amount
                else:
                    print("-----------------")
                    print(f"swapping and not burning RT worth {USDC_amount_to_swap} USDC")
                    print("-----------------")
                    rt.wallet.IT_balance += USDC_amount_to_swap / current_IT_price
                    investor_wallet.IT_balance -= USDC_amount_to_swap / current_IT_price
                    rt.USDC_amount -= USDC_amount_to_swap
                    investor_wallet.USDC_balance += USDC_amount_to_swap
                    USDC_amount_to_swap = 0
                    break

            # then swap from repayment pool
            if USDC_amount_to_swap != 0:
                if USDC_amount_to_swap <= RepaymentContract.USDC_amount:
                    print("-----------------")
                    print(f"enough capital in the repayment pool; swapping {USDC_amount_to_swap / current_IT_price} ITs")
                    print("-----------------")
                    RepaymentContract.USDC_amount -= USDC_amount_to_swap
                    investor_wallet.IT_balance -= USDC_amount_to_swap / current_IT_price
                    investor_wallet.USDC_balance += USDC_amount_to_swap
                else:
                    print("-----------------")
                    print(f"trying to swap {USDC_amount_to_swap / current_IT_price} ITs, "
                          f"but not enough capital in the repayment pool; swapping {RepaymentContract.USDC_amount / current_IT_price} ITs instead")
                    print("-----------------")
                    investor_wallet.IT_balance -= RepaymentContract.USDC_amount / current_IT_price
                    investor_wallet.USDC_balance += RepaymentContract.USDC_amount
                    RepaymentContract.USDC_amount = 0

                    return False

        return True
