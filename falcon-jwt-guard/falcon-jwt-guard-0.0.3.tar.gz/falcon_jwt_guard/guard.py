from datetime import datetime, timedelta

import falcon
import jwt

# TODO: Should support audience
# payload = {"some": "payload", "aud": ["urn:foo", "urn:bar"]}
# token = jwt.encode(payload, "secret")
# decoded = jwt.decode(token, "secret", audience="urn:foo", algorithms=["HS256"])

# TODO: Support require -> options={"require": ["exp", "iss", "sub"]}

class Guard:
    def __init__(self, secret, **kwargs):
        self.secret = secret
        self.issuer = kwargs.get('issuer', None)
        self.leeway = kwargs.get('leeway', 0)

    def verify_token(self, token):
        try:
            claims = jwt.decode(token, self.secret, leeway=self.leeway, issuer=self.issuer, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise falcon.HTTPUnauthorized(description=f'The provided token is expired.')
        except jwt.exceptions.InvalidTokenError:
            raise falcon.HTTPUnauthorized(description=f'The provided token could not be decoded.')
        else:
            return claims

    def generate_token(self, payload={}, **kwargs):
        claims = {}

        issued = datetime.utcnow()
        expires = kwargs.get('expires', timedelta(hours=24))
        starts = kwargs.get('starts', None)
        if kwargs.get('issued', None):
            claims["iat"] = issued
        if expires:
            claims["exp"] = issued + expires
        if starts:
            claims["nbf"] = issued + starts
        if self.issuer:
            claims["iss"] = self.issuer

        payload = {**payload, **claims}

        return jwt.encode(payload, self.secret, algorithm='HS256', headers=kwargs.get('headers', None))

    def __call__(self, req, resp, resource, params):
        if not req.auth:
            raise falcon.HTTPUnauthorized(description='Authorization header is missing.')
        
        # Format should follow the spec definition of Bearer <token>
        token = req.auth.split(' ')

        if len(token) != 2 or token[0] != 'Bearer':
            raise falcon.HTTPUnauthorized(description='Authorization header present but not the supported bearer schema. Format is: "Bearer <token>"')    

        req.context.claims = self.verify_token(token[1])