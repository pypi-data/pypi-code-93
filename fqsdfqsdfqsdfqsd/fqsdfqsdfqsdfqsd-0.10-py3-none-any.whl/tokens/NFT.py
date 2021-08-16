from fqsdfqsdfqsdfqsd.config import GlobalSettings

class NFT:
    def __init__(self, USDC_amount, wallet):
        self.USDC_amount = USDC_amount
        self.issuance_date = GlobalSettings.CLOCK
        self.wallet = wallet