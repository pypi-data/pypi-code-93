import datetime
import jwt
import json
from django.conf import settings
from .aes import AesCipher


class Jwthelper:
    @staticmethod
    def generate_access_token(user):
        plaintext = json.dumps({
            'id': str(user.id),
            'is_active': user.is_active,
            'permcode': user.permcode
        })
        cipher = AesCipher()
        ciphertext = cipher.encrypt(plaintext)
        payload = {
            'user': ciphertext,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow()+settings.JWT_ACCESS_TOKEN_EXP,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token
