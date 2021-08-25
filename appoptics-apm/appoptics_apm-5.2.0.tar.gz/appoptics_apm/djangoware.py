#    Copyright 2021 SolarWinds, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""AppOptics APM instrumentation for Django
"""
import functools
import importlib
import logging
import sys
import threading
import time

from appoptics_apm import config, util
from appoptics_apm.transaction_filter import UrlGetter

logger = logging.getLogger(__name__)

try:
    from django.utils.deprecation import MiddlewareMixin as AppOpticsApmMiddlewareBase
except ImportError:
    AppOpticsApmMiddlewareBase = object

# django middleware for passing values to appoptics_apm
__all__ = ("AppOpticsApmDjangoMiddleware", "install_appoptics_apm_middleware")


def _import_and_wrap(module_name, hook=None):
    """ Import the module provided in module_name and execute the provided hook on the imported module. hook is expected
    to be a callable receiving a module as the only argument and should take care of wrapping the necessary objects of
    the provided module."""

    try:
        importlib.import_module(module_name)
    except ImportError as error:
        logger.debug("Failed to import %s with %s", module_name, error)
        return
    hook(sys.modules[module_name])


class DjangoUrlGetter(UrlGetter):
    """Reconstructs and stores the request URL"""
    def __init__(self, request):
        UrlGetter.__init__(self)
        self.request = request

    def set_url(self):
        self._url = self.request.build_absolute_uri()


class AppOpticsApmWSGIHandler:
    """Wrapper WSGI Handler for Django's django.core.handlers.wsgi:WSGIHandler.
    Can be used as a replacement for Django's WSGIHandler, e.g. with uWSGI.
    """
    def __init__(self):
        """ Import and instantiate django.core.handlers.WSGIHandler,
        now that the load_middleware wrapper below has been initialized. """
        from django.core.wsgi import get_wsgi_application
        self._handler = get_wsgi_application()
        logger.warning(
            "AppOpticsApmWSGIHandler class is obsolete. Please refer to the AppOptics documentation on " +
            "how to set up instrumentation of Django applications.")

    def __call__(self, environ, start_response):
        return self._handler(environ, start_response)


# Middleware hooks listed here: http://docs.djangoproject.com/en/dev/ref/middleware/
class AppOpticsApmDjangoMiddleware(AppOpticsApmMiddlewareBase):
    def __init__(self, *args, **kwargs):
        from django.conf import settings
        try:
            self.layer = settings.APPOPTICS_APM_BASE_LAYER
        except AttributeError:
            self.layer = 'django'
        super(AppOpticsApmDjangoMiddleware, self).__init__(*args, **kwargs)

    def _singleline(self, e):  # some logs like single-line errors better
        return str(e).replace('\n', ' ').replace('\r', ' ')

    def process_request(self, request):
        try:
            xtr_hdr = request.META.get("HTTP_X-Trace", request.META.get("HTTP_X_TRACE"))
            url = DjangoUrlGetter(request)
            ctx, start_evt = util.Context.start_trace(self.layer, xtr=xtr_hdr, url_getter=url)
            if ctx:
                # needs to be set regardless of sampling for metrics reporting
                setattr(util.Context.transaction_dict, 'url_tran', url.get_url())
                if ctx.is_sampled():
                    ctx.report(start_evt)
            request.META.setdefault('APPOPTICS_APM_SPAN_START', str(int(time.time() * 1000000)))

        except Exception as e:
            logger.error("AppOptics APM middleware error: %s" % self._singleline(e))

    def process_view(self, request, view_func, view_args, view_kwargs):
        ctx = util.Context.get_default()
        if not ctx:
            return
        try:
            controller = getattr(view_func, '__module__', None)
            action = getattr(view_func, '__name__', None)

            if controller and action:
                request.META.setdefault('APPOPTICS_APM_SPAN_TRANSACTION', '{c}.{a}'.format(c=controller, a=action))

            if ctx.is_sampled():
                kvs = {
                    'Controller': controller,
                    'Action': action,
                }
                util.log('info', None, keys=kvs, store_backtrace=False)
        except Exception as e:
            logger.error("AppOptics APM middleware error: %s" % self._singleline(e))

    def process_response(self, request, response):
        """Process the response, record some information and send the end_trace out
        """
        ctx = util.Context.get_default()

        try:
            if ctx:
                # even if the request is not sampled, we need to gather this information to report metrics
                if not ctx.get_transaction_name():
                    ctx.set_transaction_name(request.META.pop('APPOPTICS_APM_SPAN_TRANSACTION', None))
                # exit event needs it. will be processed there
                setattr(
                    util.Context.transaction_dict, 'forwarded_host', request.META.get('HTTP_X_FORWARDED_HOST', None))

                setattr(util.Context.transaction_dict, 'domain', request.META.get('HTTP_HOST', 'localhost'))
                setattr(util.Context.transaction_dict, 'start_time', request.META.pop('APPOPTICS_APM_SPAN_START', None))
                setattr(util.Context.transaction_dict, 'request_method', request.META.get('REQUEST_METHOD', 'GET'))
                setattr(util.Context.transaction_dict, 'status_code', response.status_code)

            x_trace = util.end_http_trace(self.layer)
            if x_trace:
                response['X-Trace'] = x_trace
                logger.debug("djangoware process_response x_trace: {x}".format(x=x_trace))
        except Exception as e:
            logger.error("AppOptics APM middleware error: %s" % self._singleline(e))

        return response

    def process_exception(self, request, exception):
        try:
            util.log_exception()
        except Exception as e:
            logger.error("AppOptics APM middleware error: %s" % self._singleline(e))


def middleware_hooks(module, objname):
    try:
        # wrap middleware callables we want to wrap
        cls = getattr(module, objname, None)
        logger.info('middleware_hooks module {m}'.format(m=module))
        if not cls:
            return
        for method in ['process_request',
                       'process_view',
                       'process_response',
                       'process_template_response',
                       'process_exception']:
            fn = getattr(cls, method, None)
            if not fn:
                continue
            profile_name = '%s.%s.%s' % (module.__name__, objname, method)
            setattr(cls, method, util.profile_function(profile_name)(fn))
    except Exception as e:
        logger.error("AppOptics APM error: %s" % str(e))


load_middleware_lock = threading.Lock()


def on_load_middleware():
    """ wrap Django middleware from a list """

    # protect middleware wrapping: only a single thread proceeds
    global load_middleware_lock  # lock gets overwritten as None after init
    if not load_middleware_lock:  # already initialized? abort
        return
    mwlock = load_middleware_lock
    mwlock.acquire()  # acquire global lock
    if not load_middleware_lock:  # check again
        mwlock.release()  # abort
        return
    load_middleware_lock = None  # mark global as "init done"

    try:
        # middleware hooks
        from django.conf import settings

        # settings.MIDDLEWARE_CLASSES is a tuple versions prior 1.9 and is list
        # in later versions. Versions since 1.10 use MIDDLEWARE instead of MIDDLEWARE_CLASSES.
        # however both attributes may exist in versions 1.10 and above.
        # The real type and value of settings.MIDDLEWARE and
        # settings.MIDDLEWARE_CLASSES are determined by the value in setting
        # file. Django.core.handler(1.11.16): load_middleware checks MIDDLEWARE first,
        # If it is none, it uses MIDDLEWARE_CLASSES, otherwise it uses
        # MIDDLEWARE. It doesn't check it's tuple or list, just iterate it.
        using_middleware_attr = True
        middleware = getattr(settings, 'MIDDLEWARE', None)
        if middleware is None:
            middleware = getattr(settings, 'MIDDLEWARE_CLASSES', None)
            using_middleware_attr = False

        for i in [] if middleware is None else middleware:
            if i.startswith('appoptics_apm'):
                continue
            dot = i.rfind('.')
            if dot < 0 or dot + 1 == len(i):
                continue
            objname = i[dot + 1:]
            _import_and_wrap(i[:dot], functools.partial(middleware_hooks, objname=objname))
        # ORM
        if config['inst_enabled']['django_orm']:
            from appoptics_apm import inst_django_orm
            # The wrapper path BaseDatabaseWrapper has changed in Django 1.8 and onwards. Thus, we need to import here
            # so we are able to catch the ImportError depending on the running Django version
            try:
                import django.db.backends.base.base  # pylint: disable-msg=unused-import
                _import_and_wrap('django.db.backends.base.base', inst_django_orm.wrap)
            except ImportError as e:
                logger.debug('AppOptics on_load_middleware: {e}, try loading dummy.base'.format(e=e))
                _import_and_wrap('django.db.backends.dummy.base', inst_django_orm.wrap)

        # templates
        if config['inst_enabled']['django_templates']:
            from appoptics_apm import inst_django_templates
            _import_and_wrap('django.template.base', inst_django_templates.wrap)

        # load pluggable instrumentation
        from .loader import load_inst_modules
        load_inst_modules()
        apm_middleware = 'appoptics_apm.djangoware.AppOpticsApmDjangoMiddleware'
        if isinstance(middleware, list):
            middleware.insert(0, apm_middleware)
        elif isinstance(middleware, tuple):
            if using_middleware_attr:
                settings.MIDDLEWARE = (apm_middleware, ) + middleware
            else:
                settings.MIDDLEWARE_CLASSES = (apm_middleware, ) + middleware
        else:
            logger.error(
                "AppOptics APM error: settings middleware attribute should be either a tuple or a list,"
                "got {mw_type}".format(mw_type=str(type(middleware))))
    except Exception as e:
        logger.error('AppOptics APM error in on_load_middleware: {e}'.format(e=e))

    finally:  # release instrumentation lock
        mwlock.release()


def install_appoptics_apm_middleware():
    def base_handler_wrapper(func):
        @functools.wraps(func)
        def wrap_method(*f_args, **f_kwargs):
            on_load_middleware()
            return func(*f_args, **f_kwargs)

        return wrap_method

    try:
        import django.core.handlers.base

        # wrap Django load_middleware method
        cls = getattr(django.core.handlers.base, 'BaseHandler', None)
        if cls is None:
            raise Exception('Could not load Django BaseHandler class')
        if getattr(cls, 'APPOPTICS_APM_MIDDLEWARE_LOADER', None):
            return
        # add attribute to prevent class from being wrapped multiple times
        cls.APPOPTICS_APM_MIDDLEWARE_LOADER = True
        fn = getattr(cls, 'load_middleware', None)
        if not callable(fn):
            raise Exception('Could not locate load_middleware method')
        setattr(cls, 'load_middleware', base_handler_wrapper(fn))

        util.report_layer_init(layer='django')
    except Exception as e:
        # gracefully exit if Django lib not present or loaded properly
        logger.error("Unable to load and instrument Django: %s" % e)
        return


if util.ready():
    install_appoptics_apm_middleware()
