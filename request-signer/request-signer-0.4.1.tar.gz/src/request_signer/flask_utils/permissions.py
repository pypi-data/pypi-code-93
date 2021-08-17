from functools import wraps
import simplejson as json

from flask import Response, request, current_app
from ..core.signer import Signer


def abort(status_code, message):
    payload = json.dumps({'message': message})
    response = Response(payload, mimetype='application/json')
    response.status_code = status_code
    return response


def signature_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # get signature
        api_signature = request.headers.get('X-SignedRequest-Signature')
        if api_signature is None:
            return abort(403, 'Signature required')
        # get context
        company_id = request.args.get('rs_company_id', None)
        request.rs_company_id = int(company_id) if company_id else company_id
        user_id = request.args.get('rs_user_id', None)
        request.rs_user_id = int(user_id) if user_id else user_id
        payload = f'{request.method}.{request.path}.{request.data.decode()}.{company_id}.{user_id}'
        # verify signature
        secret_key = current_app.config.get('SIGNED_REQUEST_API_KEY')
        signer = Signer(secret_key)
        if not signer.verify(signature=api_signature, payload=payload.encode('utf-8')):
            return abort(403, 'Signature required')
        return fn(*args, **kwargs)

    return wrapper
