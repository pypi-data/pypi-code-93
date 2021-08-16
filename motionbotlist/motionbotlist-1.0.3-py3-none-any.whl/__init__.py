# v1

# REQUIRED MODULES:
import requests # version 2.24.0 required

# OTHER MODULES (Made by us)
from MotionBotList import Exceptions, Objects

# SETUP CLASS
class connect:
    def __init__(self, token:str, url="https://www.motiondevelopment.top/api", api_version="v1.2"):
        self.token = token
        self.url = str(url)+"/"+str(api_version)+"/"
    
    # ALL METHODS

    def get_bot(self, bot_id):
        try:
            int(bot_id)
        except:
            raise Exceptions.IntError("bot_id")
        
        url=self.url+"bots/{}".format(bot_id)
        headers={"key": self.token}
        try:
            req = requests.get(url, headers=headers)
        except requests.ConnectionError:
            raise Exceptions.ConnectionError()
        except Exception as error:
            raise Exceptions.ServerError(error)


        if req.status_code == 200:
            try:
                return Objects.botobj(req.json())
            except:
                return None
        
        if req.status_code == 404:
            raise Exceptions.BotNotFound(bot_id)

        return None

    def update(self, bot_id, server_count):
        try:
            int(bot_id)
        except:
            raise Exceptions.IntError("bot_id")
        try:
            int(server_count)
        except:
            raise Exceptions.IntError("server_count")
        
        url=self.url+"bots/{}/stats".format(bot_id)
        data={"guilds": server_count}
        headers={"key": self.token, "Content-Type": "application/json"}
        try:
            req = requests.post(url, headers=headers, json=data)
        except requests.ConnectionError:
            raise Exceptions.ConnectionError()
        except Exception as error:
            raise Exceptions.ServerError(error)

        if req.status_code == 200:
            return None

        if req.status_code == 403:
            raise Exceptions.Forbidden()

        if req.status_code == 404:
            raise Exceptions.BotNotFound(bot_id)

        return req.text

    
    def get_votes(self, bot_id):
        try:
            int(bot_id)
        except:
            raise Exceptions.IntError("bot_id")
        
        url=self.url+"bots/{}/votes".format(bot_id)
        headers={"key": self.token}
        try:
            req = requests.get(url, headers=headers)
        except requests.ConnectionError:
            raise Exceptions.ConnectionError()
        except Exception as error:
            raise Exceptions.ServerError(error)


        if req.status_code == 200:
            l=[]
            for b in req.json():
                try:
                    a=Objects.voteobj(b)
                    l.append(a)
                except:
                    pass
            return l

        if req.status_code == 404:
            raise Exceptions.BotNotFound(bot_id)

        return req.text




