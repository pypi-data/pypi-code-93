from flask_restx import Api
from jwt import exceptions as jwt_exception
from flask_jwt_extended import exceptions as jwt_extended_exception
from flask_jwt_extended import get_jwt_identity
from werkzeug.exceptions import NotFound
api = Api()


@api.errorhandler(NotFound)
def handle_no_result_exception(e):
    ''' Return a custom not found error message and 404 status code '''
    return {'message': 'No result found'}, 404


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    return {'message': message}, 500


@api.errorhandler(jwt_extended_exception.NoAuthorizationError)
def handle_auth_error(e):
    return {'message': str(e)}, 401


@api.errorhandler(jwt_extended_exception.CSRFError)
def handle_auth_error(e):
    return {'message': str(e)}, 401


@api.errorhandler(jwt_exception.ExpiredSignatureError)
def handle_expired_error(e):
    return {'mgs': 'The token has expired'}, 422


@api.errorhandler(jwt_extended_exception.InvalidHeaderError)
def handle_invalid_header_error(e):
    return {'mgs': str(e)}, 422


@api.errorhandler(jwt_exception.InvalidTokenError)
def handle_invalid_token_error(e):
    return {'mgs': str(e)}, 422


@api.errorhandler(jwt_extended_exception.JWTDecodeError)
def handle_jwt_decode_error(e):
    return {'mgs': str(e)}, 422


@api.errorhandler(jwt_extended_exception.WrongTokenError)
def handle_wrong_token_error(e):
    return {'mgs': str(e)}, 422


@api.errorhandler(jwt_extended_exception.RevokedTokenError)
def handle_revoked_token_error(e):
    return {'mgs': 'Token has been revoked'}, 401


@api.errorhandler(jwt_extended_exception.FreshTokenRequired)
def handle_fresh_token_required(e):
    return {'mgs': 'Fresh token required'}, 401


@api.errorhandler(jwt_extended_exception.UserLookupError)
def handler_user_load_error(e):
    # The identity is already saved before this exception was raised,
    # otherwise a different exception would be raised, which is why we
    # can safely call get_jwt_identity() here
    identity = get_jwt_identity()
    return {'mgs': "Error loading the user {}".format(identity)}, 401


@api.errorhandler(jwt_extended_exception.UserClaimsVerificationError)
def handle_failed_user_claims_verification(e):
    return {'mgs': 'User claims verification failed'}, 400
