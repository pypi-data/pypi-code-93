#!/usr/bin/env python

import os
import asyncio
from contextlib import AsyncExitStack
from asyncio_mqtt import Client, MqttError
import json
from . import config
import logging


_LOGGER = logging.getLogger(__name__)
# _LOGGER.setLevel( logging.DEBUG )
DEBUG_ASYNCIO = False

DEFAULT_RECONNECT_SECONDS = 60
DEFAULT_BASE_TOPIC        = "driver"
DEFAULT_MQTT_SERVER       = "shasta.tath-home.com"
DEFAULT_MQTT_PORT         = 1883
DEFAULT_QOS               = 2

# MQTT_LOGGER = logging.getLogger('mqtt')
# MQTT_LOGGER.setLevel(logging.INFO)


class MqttDriverCommand :

    def __init__ ( self, topicFilter : str, callback ):

        self.topicFilter = topicFilter
        self.callback = callback


class MqttDriver :

    def __init__ ( self, configuration : config.Config ):

        self.commands = []

        queueConfig = configuration.value( "MQTT" )

        self.reconnectSeconds = config.dictread( queueConfig, "ReconnectSeconds", DEFAULT_RECONNECT_SECONDS )
        self.mqttServer       = config.dictread( queueConfig, "MqttServer", DEFAULT_MQTT_SERVER )
        self.clientId         = config.dictread( queueConfig, "ClientId", 'mqttdriver-%s' % os.getpid() )
        self.port             = config.dictread( queueConfig, "MqttPort", DEFAULT_MQTT_PORT )
        self.username         = config.dictread( queueConfig, "username" )
        self.password         = config.dictread( queueConfig, "password" )
        self.qos              = config.dictread( queueConfig, "qos", DEFAULT_QOS )

        self.keepLooping = False

        self.client = None
        self.tasks = set()

        self.loop = None

    def addCommand ( self, topicFilter : str, callback, _notAsync : bool = False ) :

        command = MqttDriverCommand( topicFilter, callback )
        self.commands.append( command )

    async def runListen( self ):

        async with AsyncExitStack() as stack:

            try:

                # Keep track of the asyncio tasks that we create, so that
                # we can cancel them on exit
                stack.push_async_callback( MqttDriver.cancelTasks, self.tasks )

                # Connect to the MQTT broker
                self.client = Client( self.mqttServer, port=self.port, username=self.username,
                                      password=self.password, client_id=self.clientId, logger=_LOGGER )
                await stack.enter_async_context( self.client )

                for command in self.commands :

                    # Listen for generic messages for us
                    manager = self.client.filtered_messages( command.topicFilter )
                    messages = await stack.enter_async_context( manager )
                    task     = asyncio.create_task( self.processGenericMessages( command, messages ))
                    self.tasks.add( task )

                # Subscribe to topic(s)
                # 🤔 Note that we subscribe *after* starting the message
                # loggers. Otherwise, we may miss retained messages.
                for command in self.commands :
                    await self.client.subscribe( command.topicFilter )

            finally:
                # Wait for everything to complete (or fail due to, e.g., network errors)
                try:
                    await asyncio.gather( *self.tasks )
                finally:
                    self.tasks  = set()
                    self.client = None

    @staticmethod
    async def processGenericMessages ( command : MqttDriverCommand, messages ):

        async for message in messages:

            msg   = message.payload
            topic = message.topic

            _LOGGER.debug( "Received generic message on topic {}: {}".format( topic, msg ))

            topics = topic.split('/')

            if len(msg) > 0:
                try:
                    payload = json.loads(msg.decode('utf-8', 'ignore'))
                except json.JSONDecodeError:
                    payload = msg.decode('utf-8', 'ignore')
            else:
                payload = None

            try:
                await command.callback( topics, payload )
            except Exception as e:
                _LOGGER.error( f'Failed to process message {msg} with exception {e}', exc_info=True)

    def postMessage ( self, topic, data ):

        asyncio.run_coroutine_threadsafe( self.publishMessage(topic, data), self.getMessageLoop() )

    async def publishMessage( self, topic, data ):

        await self.client.publish( topic, data )

    @staticmethod
    async def cancelTasks ( tasks ):

        _LOGGER.debug( f'mqttDriver Cleaning up tasks with cancelTasks()')
        for task in tasks:
            if task.done():
                continue
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    def quitLoop ( self ) :
        self.keepLooping = False
        asyncio.run(MqttDriver.cancelTasks(self.tasks))

    async def messageLoop( self ):

        self.keepLooping = True
        self.loop = asyncio.get_event_loop()
        while self.keepLooping:
            try:
                await self.runListen()
            except asyncio.CancelledError:
                self.keepLooping = False
                await self.cancelTasks(self.tasks)
                _LOGGER.info( f'Run loop was cancelled.  Exiting loop.')
            except MqttError as error:
                _LOGGER.info( f'Error "{error}". Reconnecting in {self.reconnectSeconds} seconds.')
            finally:
                if self.keepLooping:
                    await asyncio.sleep( self.reconnectSeconds )
        _LOGGER.info( f'Exiting the mqttdriver message loop')

    def getMessageLoop ( self ) :
        return self.loop

    def runMessageLoop ( self ) :
        asyncio.run( self.messageLoop(), debug=DEBUG_ASYNCIO )
