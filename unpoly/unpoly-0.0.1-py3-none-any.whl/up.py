from functools import cached_property
from urllib.parse import parse_qs, urlencode

from .options import Options


def header_to_opt(header: str) -> str:
    return header[5:].lower().replace("-", "_")


def opt_to_header(opt: str) -> str:
    parts = map(lambda x: x.capitalize(), opt.split("_"))
    return f"X-Up-{'-'.join(parts)}"


def param_to_opt(param: str) -> str:
    return param[4:]


def opt_to_param(opt: str) -> str:
    return f"_up_{opt}"


class Layer:
    def __init__(self, unpoly, mode, context):
        self.unpoly = unpoly
        self.mode = mode or "root"
        self.context = context

    @property
    def is_root(self):
        return self.mode == "root"

    @property
    def is_overlay(self):
        return not self.is_root

    def emit(self, type, options=None):
        options = options or {}
        self.unpoly.emit(type, dict(layer="current", **options))

    def accept(self, value=None):
        assert self.is_overlay
        self.unpoly.options.accept_layer = value or {}

    def dismiss(self, value=None):
        assert self.is_overlay
        self.unpoly.options.dismiss_layer = value or {}


class Cache:
    def __init__(self, unpoly):
        self.unpoly = unpoly

    def clear(self, pattern="*"):
        self.unpoly.options.clear_cache = pattern

    def keep(self):
        self.clear("false")  # this is intentional


class Unpoly:
    def __init__(self, adapter):
        self.adapter = adapter

    @cached_property
    def options(self) -> Options:
        headers = dict(self.adapter.request_headers())
        params = self.adapter.request_params()

        options = {
            header_to_opt(k): v for k, v in headers.items() if k.startswith("X-Up-")
        }
        options.update(
            {param_to_opt(k): v for k, v in params.items() if k.startswith("_up_")}
        )
        return Options.parse(options, self.adapter)

    def __bool__(self):
        return bool(self.options.version)

    def set_title(self, value):
        self.options.title = value

    def emit(self, type, options):
        if not self.options.events:
            self.options.events = []
        self.options.events.append(dict(type=type, **options))

    @cached_property
    def cache(self):
        return Cache(self)

    @property
    def version(self):
        return self.options.version

    @property
    def target(self):
        return self.options.server_target or self.options.target

    @target.setter
    def target(self, new_target):
        self.options.server_target = new_target

    @property
    def mode(self):
        return self.options.mode

    @property
    def context(self):
        return self.options.context

    @cached_property
    def layer(self):
        return Layer(self, self.mode, self.context)

    @cached_property
    def reload_from_time(self):
        return self.options.reload_from_time

    @property
    def validate(self):
        return self.options.validate

    @property
    def fail_target(self):
        return self.options.server_target or self.options.fail_target

    @property
    def fail_mode(self):
        return self.options.fail_mode

    @property
    def fail_context(self):
        return self.options.fail_context

    @cached_property
    def fail_layer(self):
        return Layer(self, self.fail_mode, self.fail_context)

    @property
    def needs_cookie(self):
        return self.adapter.method != "GET" and not bool(self)

    def finalize_response(self, response):
        self.adapter.set_cookie(response, self.needs_cookie)

        if not self:
            return

        redirect_uri = self.adapter.redirect_uri(response)
        serialized_options = self.options.serialize(self.adapter)
        # Handle redirects
        if redirect_uri:
            if "context" in serialized_options:
                serialized_options["context_diff"] = serialized_options.pop("context")
            params = {opt_to_param(k): v for k, v in serialized_options.items()}
            sep = "&" if "?" in redirect_uri else "?"
            if params:
                redirect_uri += sep + urlencode(params)
            self.adapter.set_redirect_uri(response, redirect_uri)
        else:
            loc = self.adapter.location
            if "?" in loc and "_up_" in loc:  # Not 100% exact, but will do
                loc, qs = loc.split("?", 1)
                qs = {k: v for k, v in parse_qs(qs).items() if not k.startswith("_up_")}
                if qs:
                    loc = f"{loc}?{urlencode(qs, doseq=True)}"
            serialized_options["location"] = loc
            serialized_options["method"] = self.adapter.method
            headers = {opt_to_header(k): v for k, v in serialized_options.items()}
            self.adapter.set_headers(response, headers)
