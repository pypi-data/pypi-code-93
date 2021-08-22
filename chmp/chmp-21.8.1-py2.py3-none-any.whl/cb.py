import inspect
import enum
from typing import Any, Iterable


class Callbacks:
    def __init__(
        self, callbacks: Iterable[Any] = (), optional_events: Iterable[str] = ()
    ):
        self.callbacks = list(callbacks)
        self.optional_events = set(optional_events)

        self._checker = ConsistencyChecker(self)
        self._dispatcher = Dispatcher(self)

    @property
    def events(self):
        return self._dispatcher.events

    def __repr__(self):
        return f"<Callbacks {self.callbacks}>"

    def __add__(self, other: "Callbacks") -> "Callbacks":
        assert type(self) is type(other)
        return type(self)(
            self.callbacks + other.callbacks,
            self.optional_events | other.optional_events,
        )

    def __getattr__(self, key):
        if not key.startswith("on_"):
            raise AttributeError(key)

        def forward(**kwargs):
            self._checker.on_event(key)
            self._dispatcher.dispatch(key, kwargs)

        forward.__name__ = key

        return forward


class Dispatcher:
    def __init__(self, cbs):
        self._cb_map = {}

        for cb in cbs.callbacks:
            for key in _get_events(cb):
                cb_impl = getattr(cb, key)
                cb_spec = CallbackSpec.from_impl(cb_impl)

                self._cb_map.setdefault(key, []).append(cb_spec)

        self._required_args = {}
        for key, specs in self._cb_map.items():
            self._required_args[key] = {arg for spec in specs for arg in spec.required}

    @property
    def events(self):
        return set(self._cb_map)

    def dispatch(self, key, kwargs):
        missing = self._required_args.get(key, set()) - set(kwargs)
        if missing:
            raise RuntimeError(f"Missing arguments for event {key}: {missing}")

        for cb in self._cb_map.get(key, []):
            cb.call(kwargs)


class ConsistencyChecker:
    def __init__(self, cbs):
        self.events = {key for cb in cbs.callbacks for key in _get_events(cb)}
        self.optional_events = set(cbs.optional_events)

        self._ev_types = {}
        self._stack = []
        self._called = set()

        self._outer_ev = None

        for cb in cbs.callbacks:
            for key in _get_events(cb):
                # pre-cache all known events
                self._get_ev_type(key)

    def on_event(self, key):
        ev_type, ev = self._get_ev_type(key)
        exit_ev = self._modify_state(key, ev_type, ev)

        try:
            self._check_first_event(key, ev_type, ev, exit_ev)
            self._check_reentrant(key, ev_type, ev, exit_ev)
            self._check_balancing(key, ev_type, ev, exit_ev)
            self._check_missing(key, ev_type, ev, exit_ev)

        finally:
            self._reset_after_last(key, ev_type, ev, exit_ev)

    def _get_ev_type(self, key):
        if key not in self._ev_types:
            self._ev_types[key] = self._extract_ev_type(key)

        return self._ev_types[key]

    @staticmethod
    def _extract_ev_type(key):
        assert key.startswith("on_")

        if key.endswith("_start"):
            return EventType.start, key[len("on_") : -len("_start")]

        elif key.endswith("_end"):
            return EventType.end, key[len("on_") : -len("_end")]

        else:
            return EventType.event, key[len("on_") :]

    def _modify_state(self, key, ev_type, ev):
        self._called.add(key)

        if self._outer_ev is None and ev_type == EventType.start:
            self._outer_ev = ev

        if ev_type is EventType.start:
            self._stack.append(ev)
            return None

        elif ev_type is EventType.end:
            try:
                return self._stack.pop()

            except IndexError:
                return None

        else:
            return None

    def _is_last_event(self, ev_type, ev):
        return ev_type is EventType.end and ev == self._outer_ev

    def _reset_after_last(self, key, ev_type, ev, exit_ev):
        if not self._is_last_event(ev_type, ev):
            return

        self._outer_ev = None
        self._called = set()

    def _check_first_event(self, key, ev_type, ev, exit_ev):
        if self._outer_ev is None:
            raise RuntimeError(
                f"The first callback must be a start event 'on_*_start', got: {key}"
            )

    def _check_reentrant(self, key, ev_type, ev, exit_ev):
        count_ev = sum(ev == e for e in self._stack)
        if self._stack.count(ev) >= 2:
            raise RuntimeError(f"Reentrant event {key}")

    def _check_balancing(self, key, ev_type, ev, exit_ev):
        if ev_type is EventType.end and exit_ev != ev:
            raise RuntimeError(
                f"Unbalanced callback stack. Expected {exit_ev}, found {ev}"
            )

    def _check_missing(self, key, ev_type, ev, exit_ev):
        if not self._is_last_event(ev_type, ev):
            return

        missing = self.events - self._called - self.optional_events
        if missing:
            raise RuntimeError(f"Events not called: {missing}")


def _get_events(cb):
    events = []

    for key in vars(type(cb)):
        if not key.startswith("on_"):
            continue

        events += [key]

    return events


class EventType(int, enum.Enum):
    start = enum.auto()
    end = enum.auto()
    event = enum.auto()


class CallbackSpec:
    @classmethod
    def from_impl(cls, cb_impl):
        cb_kwargs, cb_required = cls._get_cb_args(cb_impl)
        return CallbackSpec(cb_impl, cb_kwargs, cb_required)

    def __init__(self, cb, kwargs, required):
        self.cb = cb
        self.kwargs = bool(kwargs)
        self.required = set(required)

    def call(self, kwargs):
        missing = self.required - set(kwargs)
        if missing:
            raise RuntimeError(f"Missing callback arguments for {self.cb}: {missing}")

        if self.kwargs:
            return self.cb(**kwargs)

        else:
            return self.cb(**{key: kwargs[key] for key in self.required})

    @staticmethod
    def _get_cb_args(func):
        sig = inspect.signature(func)

        required = set()
        kwargs = False

        for p in sig.parameters.values():
            if p.kind is inspect.Parameter.VAR_KEYWORD:
                kwargs = True

            elif p.kind in {
                inspect.Parameter.KEYWORD_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            }:
                required.add(p.name)

            else:
                raise RuntimeError(
                    f"Cannot handle callbacks with arguments of type {p.kind.name}"
                )

        return kwargs, required
