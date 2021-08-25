"""
The module :mod:`unpoly.up` exposes the main :class:`.Unpoly` class which is used to communicate
with Unpoly via HTTP headers. All the information of the
`Unpoly server protocol <https://unpoly.com/up.protocol>`_ is exposed and easily accessable.

An example usage could look like this (`request.up` is enabled via the :ref:`Django Integration <django>`):

.. code-block:: python

    def create_user(request):
        # Set a nice <title> for unpoly
        request.up.set_title("Create user | MyDomain.com")
        if request.method == "POST":
            form = UserForm(request.POST)
        else:
            form = UserForm()
        # Do not save the form if unpoly is just trying
        # to validate a form field
        if form.is_valid() and not request.up.validate:
            instance = form.save()
            # Tell unpoly that the user was created successfully
            request.up.emit("user:created", {"id": instance.pk})
            # and also close the layer
            request.up.layer.accept()
        return render(request, "template.html", {"form": form})
"""
from datetime import datetime
from typing import Any, Mapping, Optional
from urllib.parse import parse_qs, urlencode

from .options import Options

try:
    from functools import cached_property
except ImportError:
    from backports.cached_property import cached_property


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
    def __init__(self, unpoly: "Unpoly", mode: str, context: str):
        self.unpoly = unpoly
        self.mode = mode or "root"  #: Current layer mode (`X-Up[-Fail]-Mode`).
        self.context = context  #: Current layer context (`X-Up[-Fail]-Context`).

    @property
    def is_root(self) -> bool:
        """Returns whether this is the root layer."""
        return self.mode == "root"

    @property
    def is_overlay(self) -> bool:
        """Returns whether this is an overlay layer."""
        return not self.is_root

    def emit(self, type: str, options: Mapping[str, Any]):
        """Emit events to the frontend (`X-Up-Events`).

        Similar to :meth:`.Unpoly.emit` but emits on the current layer.
        """
        options = options or {}
        self.unpoly.emit(type, dict(layer="current", **options))

    def accept(self, value: Optional[Mapping[str, Any]] = None):
        """Accept the current layer (`X-Up-Accept-Layer`).

        An optional value can be provided to be passed back to the client."""
        # assert self.is_overlay -- the client simply ignores this on the root layer
        self.unpoly.options.accept_layer = value or {}

    def dismiss(self, value: Optional[Mapping[str, Any]] = None):
        """Accept the current layer (`X-Up-Dismiss-Layer`).

        An optional value can be provided to be passed back to the client."""
        # assert self.is_overlay -- the client simply ignores this on the root layer
        self.unpoly.options.dismiss_layer = value or {}


class Cache:
    def __init__(self, unpoly):
        self.unpoly = unpoly

    def clear(self, pattern: str = "*"):
        """Tell the client to remove all caches matching the pattern (`X-Up-Clear-Cache`)."""
        self.unpoly.options.clear_cache = pattern

    def keep(self):
        """Tell the client to keep the cache."""
        self.clear("false")  # this is intentional


class Unpoly:
    """The main entrypoint for communication with Unpoly"""

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

    def __bool__(self) -> bool:
        """Returns true if the request is triggered via Unpoly.

        This basically checks if the `X-Up-Version` header is set."""
        return bool(self.options.version)

    def set_title(self, value: str):
        """Sets the title so Unpoly can update the <title> tag (`X-Up-Title`)."""
        self.options.title = value

    def emit(self, type: str, options: Mapping[str, Any]):
        """Emit events to the frontend (`X-Up-Events`)."""
        if not self.options.events:
            self.options.events = []
        self.options.events.append(dict(type=type, **options))

    @cached_property
    def cache(self) -> Cache:
        """Access to the :class:`.Cache` functionality"""
        return Cache(self)

    @property
    def version(self) -> str:
        """Unpoly version (`X-Up-Version`)."""
        return self.options.version

    @property
    def target(self) -> str:
        """Gives access to the request's target (`X-Up-Target`).
        If the server set a new target it will return that instead."""
        return self.options.server_target or self.options.target

    @target.setter
    def target(self, new_target: str):
        self.options.server_target = new_target

    @property
    def mode(self) -> str:
        """Returns the request's mode (`X-Up-Mode`)."""
        return self.options.mode

    @property
    def context(self) -> Mapping[str, Any]:
        """Returns the current context.
        Initially this is `X-Up-Context` but the server can modify the
        returned dictionary to update the values on the client."""
        return self.options.context

    @cached_property
    def layer(self) -> Layer:
        """Access the current :class:`.Layer` configuration."""
        return Layer(self, self.mode, self.context)

    @cached_property
    def reload_from_time(self) -> Optional[datetime]:
        """The time the fragment was last updated (`X-Up-Reload-From-Time`)."""
        return self.options.reload_from_time

    @property
    def validate(self) -> Optional[str]:
        """Returns the field Unpoly is trying to validate (`X-Up-Validate`)."""
        return self.options.validate

    @property
    def fail_target(self) -> str:
        """Gives access to the request's failure target (`X-Up-Fail-Target`).
        If the server set a new target it will return that instead."""
        return self.options.server_target or self.options.fail_target

    @property
    def fail_mode(self) -> str:
        """Returns the request's failure mode (`X-Up-Fail-Mode`)."""
        return self.options.fail_mode

    @property
    def fail_context(self) -> str:
        """Returns the current failure context (`X-Up-Fail-Context`)."""
        return self.options.fail_context

    @cached_property
    def fail_layer(self) -> Layer:
        """Access the current :class:`.Layer` configuration for failures."""
        return Layer(self, self.fail_mode, self.fail_context)

    @property
    def needs_cookie(self):
        """Checks whether the response should set the `_up_method` cookie."""
        return self.adapter.method != "GET" and not bool(self)

    def finalize_response(self, response):
        """Finalize the response by settings required headers & cookies.

        It should be noted that the response is passed as is to current adapter, which
        knows how to set headers on the response etc.
        """
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
