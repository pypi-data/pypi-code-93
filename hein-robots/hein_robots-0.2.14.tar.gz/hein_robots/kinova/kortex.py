from typing import Optional, List, Callable, Dict
import logging
import threading
import queue
import time
from kortex_api.TCPTransport import TCPTransport
from kortex_api.RouterClient import RouterClient, RouterClientSendOptions
from kortex_api.SessionManager import SessionManager
from kortex_api.autogen.messages import Session_pb2
from kortex_api.autogen.client_stubs.ControlConfigClientRpc import ControlConfigClient
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient
from kortex_api.autogen.client_stubs.GripperCyclicClientRpc import GripperCyclicClient
from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2, Common_pb2, ControlConfig_pb2

logger = logging.getLogger(__name__)


class KortexError(Exception):
    pass


class KortexActionError(KortexError):
    pass


class KortexActionAbortedError(KortexActionError):
    pass


class KortexActionTimeoutError(KortexActionError):
    pass


class KortexActionNotFoundError(KortexActionError):
    pass


class KortexConnection:
    def __init__(self, host: str = '192.168.1.10', port: int = 10000, username: str = 'admin', password: str = 'admin', connect: bool = True, action_timeout: float = 60.0):
        self.logger = logger.getChild(self.__class__.__name__)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connected = False
        self.action_timeout = action_timeout
        self.notification_listeners: Dict[int, List[Callable]] = {}

        self.transport = TCPTransport()
        self.router = RouterClient(self.transport, RouterClient.basicErrorCallback)
        self.session_manager: Optional[SessionManager] = None
        self.client: Optional[BaseClient] = None
        self.cyclic_client: Optional[BaseCyclicClient] = None
        self.control_client: Optional[ControlConfigClient] = None
        self.subscription: Optional[Base_pb2.NotificationHandle] = None

        if connect:
            self.connect()

    def connect(self):
        if self.connected:
            return

        self.transport.connect(self.host, self.port)

        session = Session_pb2.CreateSessionInfo()
        session.username = self.username
        session.password = self.password
        session.session_inactivity_timeout = 10000
        session.connection_inactivity_timeout = 2000

        self.session_manager = SessionManager(self.router)
        self.session_manager.CreateSession(session)
        self.client = BaseClient(self.router)
        self.cyclic_client = BaseCyclicClient(self.router)
        self.control_client = ControlConfigClient(self.router)
        self.subscription = self.client.OnNotificationActionTopic(self.dispatch_notification, Base_pb2.NotificationOptions())

        self.connected = True

    def disconnect(self):
        self.client.Unsubscribe(self.subscription)

    def dispatch_notification(self, notification: Base_pb2.ActionNotification):
        if notification.action_event in self.notification_listeners:
            for listener in self.notification_listeners[notification.action_event]:
                listener(notification)

    def add_notification_listener(self, listener: Callable, *action_types: int):
        for action_type in action_types:
            if action_type not in self.notification_listeners:
                self.notification_listeners[action_type] = []

            self.notification_listeners[action_type].append(listener)

    def remove_notification_listener(self, listener: Callable, *action_types: int):
        for action_type in action_types:
            if action_type not in self.notification_listeners or listener not in self.notification_listeners[action_type]:
                raise TypeError(f'Cannot remove listener, no matching listener with action_type "{action_type}" found')

            self.notification_listeners[action_type].remove(listener)

    def wait_for_notification(self, action_type: int, raise_on_abort: bool = True, timeout: Optional[float] = None) -> Base_pb2.ActionNotification:
        if timeout is None:
            timeout = self.action_timeout

        notification_queue = queue.Queue()
        action_types = [action_type, Base_pb2.ACTION_ABORT] if raise_on_abort else [action_type]
        self.add_notification_listener(lambda n: notification_queue.put(n), *action_types)

        try:
            notification = notification_queue.get(timeout=timeout)
        except queue.Empty:
            raise KortexActionTimeoutError(f'Kortex action timeout')

        if raise_on_abort and notification.action_event == Base_pb2.ACTION_ABORT:
            raise KortexActionAbortedError(f'Kortex action aborted: {Base_pb2.SubErrorCodes.Name(notification.abort_details)}')

        return notification

    def wait_for_action_end(self, timeout: Optional[float] = None, raise_on_abort: bool = True):
        self.wait_for_notification(Base_pb2.ACTION_END, raise_on_abort=raise_on_abort, timeout=timeout)

    def execute_action(self, action: Base_pb2.Action, wait: bool = True, timeout: Optional[float] = None):
        self.client.ExecuteAction(action)

        if wait:
            self.wait_for_action_end(timeout=timeout)

    def execute_gripper_command(self, command: Base_pb2.GripperCommand):
        self.client.SendGripperCommand(command)

    def execute_existing_action(self, name: str, action_type: int, raise_on_abort: bool = True, timeout: Optional[float] = None, wait: bool = True):
        requested_action_type = Base_pb2.RequestedActionType()
        requested_action_type.action_type = action_type
        action_list = self.client.ReadAllActions(requested_action_type)
        action_handle = None

        for action in action_list.action_list:
            if action.name == name:
                action_handle = action.handle

        if action_handle is None:
            raise KortexActionNotFoundError(f'Action not found: {name}')

        self.client.ExecuteActionFromReference(action_handle)

        if wait:
            self.wait_for_action_end(timeout=timeout, raise_on_abort=raise_on_abort)
