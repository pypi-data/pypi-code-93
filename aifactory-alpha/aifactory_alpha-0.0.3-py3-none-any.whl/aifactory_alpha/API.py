from datetime import datetime
from constants import *
import logging
import os


class Contest:
    _summary_ = None
    logger = None
    auth_method = None
    user_token = None
    user_id = None
    user_email = None
    task_id = None
    model_name_prefix = None
    def __init__(self, auth_method=AUTH_METHOD.USERINFO, user_token=None,
                 user_id=None, user_email=None, model_name_prefix=None, task_id=None,
                 log_dir="./log/", debug=True, submit_url=SUBMISSION_DEFAULT_URL):
        self.set_log_dir(log_dir)
        self.auth_method = auth_method
        if auth_method==AUTH_METHOD.TOKEN:
            if debug: user_token = DEBUGGING_PARAMETERS.TOKEN
            self.set_token(user_token)
        elif auth_method==AUTH_METHOD.USERINFO:
            self.set_user_id(user_id)
            self.set_user_email(user_email)
            self.set_task_id(task_id)
            self.set_model_name_prefix(model_name_prefix)
        else:
            raise(WrongAuthMethodError)

    def set_log_dir(self, log_dir: str):
        self.log_dir = os.path.abspath(log_dir)
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)
        if not os.path.isdir(self.log_dir):
            raise AssertionError("{} is not a directory.".format(self.log_dir))
        self.logger = logging.getLogger(__name__)
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(module)s:%(levelname)s:%(message)s')
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def set_token(self, token=None, yes=False):
        token_in_env_var = os.getenv('AIF_TOKEN')
        if token_in_env_var is not None:
            if token is not None and (token_in_env_var != token):
                if not yes:
                    print("It will replace your token in the environment variable `AIF_TOKEN`.")
                    res = input("Do you want to proceed? [Y/N] - default: Y")
                    if res == 'N':
                        print("Using token from the environment variable `AIF_TOKEN`.")
                        token = token_in_env_var
                else:
                    token = token_in_env_var
        self.user_token = user_token

    def set_user_email(self, email: str):
        self.user_email = email

    def set_user_id(self, id: str):
        self.user_id = id

    def set_task_id(self, task_id: int):
        self.task_id = task_id

    def set_model_name_prefix(self, model_name_prefix: str):
        self.model_name_prefix = model_name_prefix

    def _investigate_validation_(self):
        res = []
        if self.auth_method == AUTH_METHOD.TOKEN:
            if self.token is None:
                res.append(SubmitTokenNotFoundError)
        elif self.auth_method == AUTH_METHOD.USERINFO:
            if self.user_id is None and self.user_email is None:
                res.append(UserInfoNotDefinedError)
            if self.task_id is None:
                res.append(TaskIDNotDefinedError)
        else:
            res = res.append(WrongAuthMethodError)
        for r in res:
            self.logger.error(r.ment)
        return res

    def submit(self):
        status = SUBMIT_RESULT.FAIL_TO_SUBMIT
        # This method submit the answer file to the server.
        cur_log_file_name = "SUBMISSION_LOG_"+datetime.now().__str__().replace(" ", "-").replace(":", "-").split(".")[0]+".log"
        log_path = os.path.join(self.log_dir, cur_log_file_name)
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s:%(module)s:%(levelname)s:%(message)s', '%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        res = self._investigate_validation_()
        def fail():
            self.logger.error("Submission Failed.")
            print("Please have a look at the logs in {} for more details.".format(log_path))
            return status
        if len(res) != 0:
            fail()
        status = SUBMIT_RESULT.SUBMIT_SUCCESS
        return status


    def release(self):
        # This method submit the answer file and the code to the server.
        pass

    def summary(self):
        if self._summary_ is None:
            self._summary_ = ">>> Contest Information <<<\n"
            self._summary_ += "Authentification Method:"
            if self.auth_method is AUTH_METHOD.TOKEN:
                self._summary_ += "Token \n"
                self._summary_ += "    Token: {} \n".format(self.user_token)
            elif self.auth_method is AUTH_METHOD.USERINFO:
                self._summary_ += "User Information \n"
                self._summary_ += "    Task ID: {}\n".format(self.task_id)
                self._summary_ += "    User ID: {}\n".format(self.user_id)
                self._summary_ += "    User e-mail: {}\n".format(self.user_email)
            if self.model_name_prefix is not None:
                self._summary_ += "Model Name Prefix: {}\n".format(self.model_name_prefix)
            return self.summary()
        else:
            print(self._summary_)
            return self._summary_


if __name__ == "__main__":
    c = Contest(user_id='newsun_0', task_id=2000)
    c.summary()
    c.submit()