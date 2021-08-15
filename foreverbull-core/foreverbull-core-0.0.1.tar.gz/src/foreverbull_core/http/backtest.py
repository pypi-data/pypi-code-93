import requests
from foreverbull_core.http import RequestError


class Backtest:
    def __init__(self, host, session=None) -> None:
        self.host = host
        if session is None:
            session = requests.Session()
        self.session = session

    def list_backtests(self):
        rsp = self.session.get(f"http://{self.host}/backtests")
        if not rsp.ok:
            raise RequestError(f"get call /backtests gave bad return code: {rsp.status_code}")
        return rsp.json()

    def create_backtest(self, backtest):
        rsp = self.session.post(f"http://{self.host}/backtests", json=backtest)
        if not rsp.ok:
            raise RequestError(f"post call /backtests gave bad return code: {rsp.status_code}")
        return rsp.json()

    def get_backtest(self, backtest_id):
        rsp = self.session.get(f"http://{self.host}/backtests/{backtest_id}")
        if not rsp.ok:
            raise RequestError(f"get call /backtests/{backtest_id} gave bad return code: {rsp.status_code}")
        return rsp.json()

    def update_backtest():
        pass

    def delete_backtest(self, backtest_id):
        rsp = self.session.delete(f"http://{self.host}/backtests/{backtest_id}")
        if not rsp.ok:
            raise RequestError(f"delete call /backtests/{backtest_id} gave bad return code: {rsp.status_code}")
        return True

    def list_backtest_services(self, backtest_id):
        rsp = self.session.get(f"http://{self.host}/backtests/{backtest_id}/services")
        if not rsp.ok:
            raise RequestError(f"get call /backtests/{backtest_id}/services gave bad return code: {rsp.status_code}")
        return rsp.json()

    def add_backtest_service(self, backtest_id, service):
        rsp = self.session.put(f"http://{self.host}/backtests/{backtest_id}/service", json=service)
        if not rsp.ok:
            raise RequestError(f"post call /backtests/{backtest_id}/services gave bad return code: {rsp.status_code}")
        # return rsp.json

    def list_sessions(self, backtest_id):
        rsp = self.session.get(f"http://{self.host}/backtests/{backtest_id}/sessions")
        if not rsp.ok:
            raise RequestError(f"get call /backtests/{backtest_id}/sessions gave bad return code: {rsp.status_code}")
        return rsp.json()

    def create_session(self, backtest_id):
        rsp = self.session.post(f"http://{self.host}/backtests/{backtest_id}/sessions")
        if not rsp.ok:
            raise RequestError(f"post call /backtests/{backtest_id}/sessions gave bad return code: {rsp.status_code}")
        return rsp.json()

    def get_session(self, backtest_id, session_id):
        rsp = self.session.get(f"http://{self.host}/backtests/{backtest_id}/sessions/{session_id}")
        if not rsp.ok:
            raise RequestError(
                f"get call /backtests/{backtest_id}/sessions/{session_id} gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def update_session():
        pass

    def delete_session(self, backtest_id, session_id):
        rsp = self.session.delete(f"http://{self.host}/backtests/{backtest_id}/sessions/{session_id}")
        if not rsp.ok:
            raise RequestError(
                f"delete call /backtests/{backtest_id}/sessions/{session_id} gave bad return code: {rsp.status_code}"
            )
        return True

    def run_session(self, backtest_id, session_id, run_workers):
        rsp = self.session.post(
            f"http://{self.host}/backtests/{backtest_id}/sessions/{session_id}/run",
            json=run_workers,
        )
        if not rsp.ok:
            raise RequestError(
                f"post call /backtests/{backtest_id}/sessions/{session_id}/run gave bad return code: {rsp.status_code}"
            )
        return rsp.json()
