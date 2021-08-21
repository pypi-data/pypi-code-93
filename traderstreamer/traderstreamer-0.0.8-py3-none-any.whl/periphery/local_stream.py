from scripts.services import (
    bybit_mkt_svc,
    bybit_acc_svc,
    bybit_bar_svc,
    binance_mkt_svc_1,
    binance_mkt_svc_2,
    bybit_sec_svc,
    binance_sec_svc
)


class LocalStreamer:

    def __init__(self,
                 source: str,
                 bybit_public_key: str = None,
                 bybit_private_key: str = None,
                 binance_public_key: str = None,
                 binance_private_key: str = None):

        self.source = source
        self.bybit_public_key = bybit_public_key
        self.bybit_private_key = bybit_private_key
        self.binance_public_key = binance_public_key
        self.binance_private_key = binance_private_key

    def start(self,
              mkt_port: int = 2000,
              acc_port: int = 2001,
              bar_port: int = 2002,
              sec_port: int = 2003):

        if self.source == 'bybit':
            mkt_svc = bybit_mkt_svc(pub_port=mkt_port)

            acc_svc = bybit_acc_svc(public_key=self.bybit_public_key,
                                    private_key=self.bybit_private_key,
                                    pub_port=acc_port)

            bar_svc = bybit_bar_svc(public_key=self.bybit_public_key,
                                    private_key=self.bybit_private_key,
                                    pub_port=bar_port)

            sec_svc = bybit_sec_svc(mkt_ports=[mkt_port],
                                    push_port=sec_port)

            mkt_svc.start()
            acc_svc.start()
            bar_svc.start()
            sec_svc.start()


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv(override=True)

    BYBIT_PUBLIC_KEY = os.getenv('PP_BYBIT_PUBLIC_KEY')
    BYBIT_PRIVATE_KEY = os.getenv('PP_BYBIT_PRIVATE_KEY')

    streamer = LocalStreamer('bybit', BYBIT_PUBLIC_KEY, BYBIT_PRIVATE_KEY)
    streamer.start()