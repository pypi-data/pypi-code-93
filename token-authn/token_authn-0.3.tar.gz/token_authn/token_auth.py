from fastapi import Request, HTTPException, Response, status
import jose.jwt as jwt
import secMgr
import os
import traceback as tb
import json
import datetime
import time


def verify_token(req: Request, response: Response):
    if 'authorization' in req.headers.keys():
        token = req.headers["authorization"].split(' ')[1]
    else:
        return False
    #TODO add expiration time as part of a json
    exp_time = 24*60*60

    # Get the JWT token secret
    try:
        env = os.environ.get('ECS_CLUSTER_NAME')
        secrets = secMgr.get_secret(env)#os.environ.get('ECS_CLUSTER_NAME'))
        secrets = json.loads(secrets)
        jwt_secret_token = secrets['JWT_TOKEN_SECRET']
    except Exception as e:
        print(str(e))
        print(tb.format_exc())
        secrets = []
        return False

    try:
        payload = jwt.decode(
            token,
            key=jwt_secret_token
        )
        expiration = payload['exp'] if 'exp' in payload.keys() else 0
        if expiration == 0:
            if payload['iat']+exp_time>time.mktime(datetime.date.today().timetuple()):
                return True
            else:
                return False
            
        else:
            if datetime(expiration)>datetime.now():
                return True
            else:
                return False
        return True
    except Exception as e:
        print(str(e))
        print(tb.format_exc())
        return False