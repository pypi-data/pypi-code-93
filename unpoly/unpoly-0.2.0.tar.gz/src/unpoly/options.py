import copy
from datetime import datetime, timezone
from functools import partial
from typing import Any, List, Mapping, Optional

import attr

RENDER_OPTS = {
    "accept_layer",
    "dismiss_layer",
    "clear_cache",
    "events",
    "title",
    "events",
}


def ts_to_datetime(data: str) -> Optional[datetime]:
    try:
        ts = int(data)
        return datetime.fromtimestamp(ts, timezone.utc)
    except (ValueError, TypeError):
        return datetime.fromtimestamp(0, timezone.utc)


@attr.define(kw_only=True)
class Options:
    # mostly request options
    version: Optional[str] = None
    target: Optional[str] = None
    mode: Optional[str] = None
    context: Optional[Mapping[str, Any]] = None
    fail_target: Optional[str] = None
    fail_mode: Optional[str] = None
    fail_context: Optional[Mapping[str, Any]] = None
    validate: Optional[str] = None
    reload_from_time: Optional[datetime] = None

    # internal params
    server_target: Optional[str] = attr.field(init=False, default=None)
    initial_context: Optional[Mapping[str, Any]] = attr.field(init=False)

    # explicit response options
    title: Optional[str] = None
    clear_cache: Optional[str] = None
    accept_layer: Optional[str] = None
    dismiss_layer: Optional[str] = None
    events: List[Mapping[str, Any]] = None

    def __attrs_post_init__(self):
        if self.context is None:
            self.context = {}
        self.initial_context = copy.deepcopy(self.context)

    @property
    def target_changed(self):
        return self.server_target and self.server_target != self.target

    @property
    def context_diff(self):
        old = self.initial_context
        new = self.context
        old_keys = set(old)
        new_keys = set(new)
        result = {}
        for key in old_keys - new_keys:
            result[key] = None
        for key in new_keys - old_keys:
            result[key] = new[key]
        for key in new_keys & old_keys:
            if old[key] != new[key]:
                result[key] = new[key]
        return result

    @classmethod
    def parse(cls, options, adapter):
        if "reload_from_time" in options:
            options["reload_from_time"] = ts_to_datetime(options["reload_from_time"])
        for opt in {
            "events",
            "context",
            "context_diff",
            "fail_context",
            "dismiss_layer",
            "accept_layer",
            "context_diff",
        }:
            if opt in options:
                options[opt] = adapter.deserialize_data(options[opt])
                if opt in {"accept_layer", "dismiss_layer"}:
                    options[opt] = {}
        context_diff = options.pop("context_diff", None)

        options = cls(**options)
        # Apply the passed context diff
        if context_diff:
            for k, v in context_diff.items():
                if v is None and k in options.context:
                    del options.context[k]
                else:
                    options.context[k] = v
        return options

    def _serialize(self, inst, field, value, *, adapter):
        if field.name in {"accept_layer", "dismiss_layer", "events"}:
            return "null" if value == {} else adapter.serialize_data(value)
        return value

    def serialize(self, adapter):
        serialized_options = attr.asdict(
            self,
            filter=lambda attr, value: attr.name in RENDER_OPTS and value is not None,
            value_serializer=partial(self._serialize, adapter=adapter),
        )

        # Update with new target, if it changed
        if self.target_changed:
            serialized_options["target"] = self.server_target

        # Update with context changes, see https://unpoly.com/X-Up-Context
        diff = self.context_diff
        if diff:
            serialized_options["context"] = adapter.serialize_data(diff)

        return serialized_options
