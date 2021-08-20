import typing as tp
import logging

from flask import Response, request, Request

logger = logging.getLogger(__name__)
__version__ = '0.1'


def FlaskRequestsLogging(app, default_level_mapping: tp.Optional[tp.Dict[int, int]] = None,
                         log_template: tp.Callable[[Request, Response], str] = \
                                 lambda req,
                                        resp: f'Request {req.method} {str(req.url_rule)} finished '
                                              f'with {resp.status_code}',
                         extra_args_gen: tp.Callable[[Request, Response], dict] = \
                                 lambda req, resp: {'url': str(req.url_rule), 'method': req.method,
                                                    'status_code': resp.status_code}):
    """
    Instantiate Flask-Requests-Logging

    :param app: app to use
    :param default_level_mapping: a mapping of either leftmost digit to error code, or entire
        error code to level mapping. Default is log 2xx and 3xx with INFO, 4xx with WARN
        and 5xx with ERROR. If not given, request will be logged with INFO.
    :param log_template: a function that called with two arguments, flask request and Reponse,
        will return the logging message. Defaults to 'Request {method} {url rule} returned with
        {status_code}'
    :param extra_args_gen: generator of a dictionary that will be attached as extras to the logging
        entry. By default returns a dict of ('method'=> Method, 'url' => URL rule, 'status_code' =>
        status_code)
    """
    default_level_mapping = default_level_mapping or {2: logging.INFO,
                                                      3: logging.INFO,
                                                      4: logging.WARN,
                                                      5: logging.ERROR}

    @app.after_request
    def after_request(r: Response):
        level = logging.INFO
        if r.status_code in default_level_mapping:
            level = default_level_mapping[r.status_code]
        else:
            p = r.status_code // 100
            if p in default_level_mapping:
                level = default_level_mapping[p]

        logger.log(level, log_template(request, r), extra=extra_args_gen(request, r))

        return r
