"""Class implementation for mouse move interface.
"""

from typing import Any
from typing import Dict
from typing import Optional

from apysc._event.handler import Handler
from apysc._event.handler import HandlerData
from apysc._event.mouse_event_interface_base import MouseEventInterfaceBase


class MouseMoveInterface(MouseEventInterfaceBase):

    _mouse_move_handlers: Dict[str, HandlerData]

    def mousemove(
            self, handler: Handler,
            options: Optional[Dict[str, Any]] = None) -> str:
        """
        Add mouse move event listener setting.

        Parameters
        ----------
        handler : Handler
            Callable that called when mouse is moved on this instance.
        options : dict or None, default None
            Optional arguments dictionary to be passed to handler.

        Returns
        -------
        name : str
            Handler's name.

        References
        ----------
        - Mousemove interface document
            - https://simon-ritchie.github.io/apysc/mousemove.html
        """
        import apysc as ap
        from apysc._validation.variable_name_validation import \
            validate_variable_name_interface_type
        with ap.DebugInfo(
                callable_=self.mousemove, locals_=locals(),
                module_name=__name__, class_=MouseMoveInterface):
            import apysc as ap
            from apysc._event.handler import append_handler_expression
            from apysc._event.handler import get_handler_name
            from apysc._type.variable_name_interface import \
                VariableNameInterface
            self_instance: VariableNameInterface = \
                validate_variable_name_interface_type(instance=self)
            self._initialize_mouse_move_handlers_if_not_initialized()
            name: str = get_handler_name(handler=handler, instance=self)
            self._set_mouse_event_handler_data(
                handler=handler, handlers_dict=self._mouse_move_handlers,
                options=options)
            self._append_mouse_event_binding_expression(
                name=name, mouse_event_type=ap.MouseEventType.MOUSEMOVE)
            e: ap.MouseEvent = ap.MouseEvent(this=self_instance)
            append_handler_expression(
                handler_data=self._mouse_move_handlers[name],
                handler_name=name, e=e)
            return name

    def _initialize_mouse_move_handlers_if_not_initialized(self) -> None:
        """
        Initialize _mouse_move_handlers attribute if it is not
        initialized yet.
        """
        if hasattr(self, '_mouse_move_handlers'):
            return
        self._mouse_move_handlers = {}

    def unbind_mousemove(self, handler: Handler) -> None:
        """
        Unbind specified handler's mouse move event.

        Parameters
        ----------
        handler : Handler
            Callable to be unbinded.

        References
        ----------
        - Mousemove interface document
            - https://simon-ritchie.github.io/apysc/mousemove.html
        """
        import apysc as ap
        with ap.DebugInfo(
                callable_=self.unbind_mousemove, locals_=locals(),
                module_name=__name__, class_=MouseMoveInterface):
            self._initialize_mouse_move_handlers_if_not_initialized()
            self._unbind_mouse_event(
                handler=handler, mouse_event_type=ap.MouseEventType.MOUSEMOVE,
                handlers_dict=self._mouse_move_handlers)

    def unbind_mousemove_all(self) -> None:
        """
        Unbind all mouse move events.

        References
        ----------
        - Mousemove interface document
            - https://simon-ritchie.github.io/apysc/mousemove.html
        """
        import apysc as ap
        with ap.DebugInfo(
                callable_=self.unbind_mousemove_all, locals_=locals(),
                module_name=__name__, class_=MouseMoveInterface):
            self._initialize_mouse_move_handlers_if_not_initialized()
            self._unbind_all_mouse_events(
                mouse_event_type=ap.MouseEventType.MOUSEMOVE,
                handlers_dict=self._mouse_move_handlers)
