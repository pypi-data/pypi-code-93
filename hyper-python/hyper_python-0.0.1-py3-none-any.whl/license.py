import hyper
from .error import InvalidRequestError, AuthenticationError
from .mapper import Map
from .requestor import request


class License:
    @classmethod
    def create(cls, **params):
        if not hyper.api_key:
            raise AuthenticationError()

        req = request(
            method='POST',
            url=f'/licenses',
            api_key=hyper.api_key,
            data=params
        )
        if req.status_code == 200:
            return Map(req.json())

        raise InvalidRequestError(req.status_code, req.text)

    @classmethod
    def retrieve(cls, key):
        if not hyper.api_key:
            raise AuthenticationError()

        req = request(
            method='GET',
            url=f'/licenses/{key}',
            api_key=hyper.api_key
        )
        if req.status_code == 200:
            return Map(req.json())

        raise InvalidRequestError(req.status_code, req.text)

    @classmethod
    def update(cls, key, metadata):
        if not hyper.api_key:
            raise AuthenticationError()

        req = request(
            method='PATCH',
            url=f'/licenses/{key}',
            api_key=hyper.api_key,
            data={'metadata': metadata}
        )
        if req.status_code == 200:
            return Map(req.json())

        raise InvalidRequestError(req.status_code, req.text)

    @classmethod
    def delete(cls, key):
        if not hyper.api_key:
            raise AuthenticationError()

        req = request(
            method='DELETE',
            url=f'/licenses/{key}',
            api_key=hyper.api_key
        )
        if req.status_code == 202:
            return {'key': key, 'deleted': True}

        raise InvalidRequestError(req.status_code, req.text)

    @classmethod
    def list(cls, limit: int = 10, page: int = 1):
        if not hyper.api_key:
            raise AuthenticationError()

        req = request(
            method='GET',
            url=f'/licenses?limit={limit}&page={page}',
            api_key=hyper.api_key
        )
        if req.status_code == 200:
            return Map(req.json())

        raise InvalidRequestError(req.status_code, req.text)

    @classmethod
    def send(cls, key):
        if not hyper.api_key:
            raise AuthenticationError()

        req = request(
            method='POST',
            url=f'/licenses/{key}/send',
            api_key=hyper.api_key
        )
        if req.status_code == 202:
            return {'key': key, 'sent': True}

        raise InvalidRequestError(req.status_code, req.text)
