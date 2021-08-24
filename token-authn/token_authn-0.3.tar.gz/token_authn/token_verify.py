from boto3 import resource
from token_auth import verify_token
from fastapi import Depends, Response, status

def verify(response: Response, authorized: bool = Depends(verify_token)):
    if not authorized:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'error': 'Unauthorized'}