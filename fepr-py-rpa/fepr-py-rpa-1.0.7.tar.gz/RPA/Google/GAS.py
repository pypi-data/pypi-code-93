import os.path
import pickle
from googleapiclient.discovery import Resource, build


class AppsScriptAPI(object):
    """GASをAPIで公開し、そのAPIをPythonから操作するためのクラス

    APIで操作するためには、GASをAPI公開しデプロイしたプロジェクトのみ可能。
    """
    def __init__(self, script_id: str):
        """スクリプトIDを入力し、プロジェクトをインスタンス化する

        Args:
            script_id (str): スクリプトID
        
        Note:
            スクリプトIDはGASのエディタから設定で確認してください。
        """
        self.__script_id: str = script_id

        cred = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                cred = pickle.load(token)
        self.service = build('script', 'v1', credentials=cred)
    
    def run_func(self, func_name: str, param=[], devMode=True) -> dict:
        """APIで公開してプロジェクトの関数を実行する

        Args:
            func_name (str): 実行したい関数名
            param (list): 実行したい関数の引数をリストに格納
            devMode (bool): 常に新しいデプロイのバージョンで実行する場合は、True
        """
        script: Resource = self.service.scripts()
        body: dict = {
            "scriptId": self.__script_id,
            "body": {
                "devMode": devMode,
                "function": func_name,
                "parameters":param
            }
        }

        result_json = script.run(**body).execute()

        return result_json