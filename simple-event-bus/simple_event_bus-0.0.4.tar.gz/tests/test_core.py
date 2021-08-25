# encoding: utf-8
# @Time   : 2021/8/4 11:09
# @author : zza
# @Email  : z740713651@outlook.com
# @File   : test_core.py
import pytest

from simple_event_bus import run_simple_event_source, run_simple_event_source_async


class TestCore:
    def test_event(self):
        from simple_event_bus.core import EVENT
        from simple_event_bus.errors import EVENTNameError

        with pytest.raises(EVENTNameError):
            EVENT("a event")

    def test_basic_event_bus(self):
        from simple_event_bus.core import EVENT, Event, EventBus
        from simple_event_bus.errors import MultiParamFunctionError

        app = EventBus()
        event_list = []

        @app.listening("HeartBeat")
        def count(event: Event):
            event_list.append(event)
            if len(event_list) > 5:
                app.publish_event(Event(EVENT("close_loop")))
            return True

        run_simple_event_source(app, time_interval=0.1)
        assert len(event_list) > 5

        with pytest.raises(MultiParamFunctionError):

            @app.listening("HeartBeat")
            def error_func(a, b, c):
                print("this is a error function")
                return

    @pytest.mark.asyncio
    async def test_async_event_bus(self):
        from simple_event_bus.core import EVENT, AsyncEventBus, Event

        app = AsyncEventBus()

        event_list = []
        async_event_list = []

        @app.listening("HeartBeat")
        def count(event: Event):
            event_list.append(event)
            if len(event_list) <= 5:
                return True

        @app.listening(EVENT("HeartBeat"))
        async def async_count(event: Event):
            async_event_list.append(event)
            if len(async_event_list) == 5:
                await app.publish_event("close_loop")

        await run_simple_event_source_async(app, time_interval=0.1)
        assert len(event_list) == 10
        assert len(async_event_list) == 5
        assert "async_count" in app.get_listener_name_list("HeartBeat")
        assert "async_count" in app.get_listener_name_list()

    @pytest.mark.asyncio
    async def test_no_params_function(self):
        from simple_event_bus import AsyncEventBus, EventBus

        async_app = AsyncEventBus()

        @async_app.listening("HeartBeat")
        def func_1():
            return

        @async_app.listening("HeartBeat")
        async def func_2():
            return

        await async_app.publish_event("HeartBeat")

        sync_app = EventBus()
        sync_app.add_listener("HeartBeat", func_1)
        sync_app.publish_event("HeartBeat")

    def test_duplicate_function(self):
        from simple_event_bus import EventBus
        from simple_event_bus.errors import DuplicateFunctionError

        def func_1():
            return

        sync_app = EventBus()
        sync_app.add_listener("HeartBeat", func_1)
        with pytest.raises(DuplicateFunctionError):
            sync_app.add_listener("HeartBeat", func_1)

        sync_app.add_listener("HeartBeat", func_1, duplicate_check=False)

        sync_app.remove_listener("HeartBeat", func_1, iter_delete=True)
