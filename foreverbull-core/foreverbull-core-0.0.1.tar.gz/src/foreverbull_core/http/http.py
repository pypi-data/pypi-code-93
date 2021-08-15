from foreverbull_core.http import backtest, service


class HTTPClient:
    def __init__(self, host) -> None:
        self.backtest = backtest.Backtest(host)
        self.service = service.Service(host)
