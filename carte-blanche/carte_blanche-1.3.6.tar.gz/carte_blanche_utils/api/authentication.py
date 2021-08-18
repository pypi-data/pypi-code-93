import json
import falcon


class Authenticator(object):
    """docstring for Authenticator"""
    def __init__(self, args={'auth_not_required': [], 'validator': None, 'args': {}}):
        super(Authenticator, self).__init__()
        self.auth_not_required = args.get('auth_not_required')
        self.validator = args.get('validator')
        self.validator_args = args.get('args')

    def authorization_exception(self, req, resp):

        response_data = {
            'meta': {
                'errors': ['Unauthorized'],
                'status': falcon.HTTP_401,
                'endpoint': req.path
            },
            'data': {}
        }

        resp.body = json.dumps(response_data)
        resp.status = falcon.HTTP_401
        resp.complete = True

        return resp

    def process_request(self, req, resp):
        """Process the request before routing it.

        Note:
            Because Falcon routes each request based on req.path, a
            request can be effectively re-routed by setting that
            attribute to a new value from within process_request().

        Args:
            req: Request object that will eventually be
                routed to an on_* responder method.
            resp: Response object that will be routed to
                the on_* responder.
        """
        if req.path in self.auth_not_required:
            pass
        else:
            success, authorization = self.validator(req, self.validator_args)
            if not success:
                return self.authorization_exception(req, resp)
            else:
                req.params['authorization'] = authorization

    def process_resource(self, req, resp, resource, params):
        """Process the request after routing.

        Note:
            This method is only called when the request matches
            a route to a resource.

        Args:
            req: Request object that will be passed to the
                routed responder.
            resp: Response object that will be passed to the
                responder.
            resource: Resource object to which the request was
                routed.
            params: A dict-like object representing any additional
                params derived from the route's URI template fields,
                that will be passed to the resource's responder
                method as keyword arguments.
        """

    def process_response(self, req, resp, resource, req_succeeded):
        """Post-processing of the response (after routing).

        Args:
            req: Request object.
            resp: Response object.
            resource: Resource object to which the request was
                routed. May be None if no route was found
                for the request.
            req_succeeded: True if no exceptions were raised while
                the framework processed and routed the request;
                otherwise False.
        """

# def validator(req):
#     print('validating request')

#     return {'jwt_token': 'foo'}


# class TestRoute(object):
#     """docstring for TestRoute"""
#     def on_get(self, req, resp):

#         print('should not hit')
#         print(req.params)
#         resp.body = json.dumps({'success': True})
#         return resp


# api = falcon.API(middleware=[Authenticator({'auth_not_required': [], 'validator': validator})])

# api.add_route('/v1/test', TestRoute())
