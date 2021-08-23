'''
    discordbot is a program which provides an interface to the Discord API
    Copyright (C) 2021 Gabe Millikan

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import asyncio
import time
import traceback

import websockets, requests, urllib, json
import os, shutil, pathlib
file_root = pathlib.Path(__file__).parent / "_files"
file_root.mkdir(parents = True, exist_ok = True)

from discordbot import *

class Bot:
    def default_logger(severity, contents, no_message):
        line = ''
        if severity == log_severity.error:
            line = "[ERROR]: %s" % contents
        elif severity == log_severity.warning:
            line = "[WARNING]: %s" % contents
        elif severity == log_severity.important:
            line = "[IMPORTANT]: %s" % contents
        else:
            line = "[INFO]: %s" % contents
        
        print(line)

    def __init__(self, token, sequence = 0, session_id = None, bot_identifier = "python/discordbot/v1.0"):
        try:
            assert not "active" in os.listdir(file_root)
        except:
            raise error.BotAlreadyRunning("The bot appears to already be running. If the bot is not running, then please wait up to 30 seconds for the previous bot to shut down. After that, make sure that %s exists and is EMPTY (you may delete any present files)." % file_root)
        
        with open(file_root / "active", "w+") as f:
            f.write(str(os.getpid()))
        self.created_active = True
        
        self.token = token
        self.last_received_sequence = sequence
        self.session_id = session_id
        self.bot_identifier = bot_identifier
        
        self.periodics = []
        self.periodic_task = None
        self.commands = {}
        self.event_handlers = {}
        self._rate_buckets = {}
        self._rate_bucket_lookup = {}
        
        self.gateway_endpoint = None
        self.gateway_connection = None
        
        self.ready = False
        self.stopped = False
        self.running = True
        self.reconnect = False
        
        self.logger = Bot.default_logger
        
        # register heartbeat
        self.register_periodic(45, self._heartbeat)
        
        # register logout checker
        async def logout(dt):
            if self.stopped:
                await self.gateway_connection.close(1001)
        self.register_periodic(0.1, logout)
        
        # register command handler
        self.command_prefix = "?"
        self.on_event(event.guild_message_sent, self._command_handler)
    
    def __del__(self):
        try:
            if self.created_active:
                os.remove(file_root / "active")
        except:
            pass
    
    '''
        logging
    '''
    def log(self, txt, log_only = False, severity = log_severity.info):
        self.logger(severity, txt, log_only or not self.ready)
    
    def log_error(self, err, log_only = False):
        log_only = log_only or isinstance(err, error.MessageSendFailure)
        self.log("%s\n" % traceback.format_exc() + repr(err), log_only = log_only, severity = log_severity.error)
    
    '''
        internal utils
    '''
    def _wrap_http(self, method, *args, **kwargs):
        self.log("Sending HTTP " + method.upper() + " request w/ args: " + ", ".join(args) + " and kwargs " + str(kwargs))
    
        response = None
        try:
            response = {
                "get": requests.get,
                "post": requests.post,
                "put": requests.put,
                "delete": requests.delete,
            }[method](*args, **kwargs)
        except requests.exceptions.RequestException as e:
            raise error.HTTPError(
                "HTTP %s request failed (w/ request error %s) because: %s" % (
                method.upper(),
                e.__class__.__name__,
                str(e)
            ))
        
        sc = response.status_code
        if sc in api.status_code.http_success:
            data = {}
            if sc != api.status_code.no_content:
                try:
                    data = response.json()
                except:
                    raise error.UnexpectedResponse("Invalid JSON: %s" % response.text)
            return data, response
        elif sc in api.status_code.http_bad_request:
            raise error.HTTPBadRequest("Sent an invalid request, got response: %s" % response.text)
        elif sc in api.status_code.http_insufficient_permissions:
            raise error.HTTPBadRequest("Made request with insufficient permissions, got response: %s" % response.text)
        elif sc in api.status_code.http_try_later:
            t = 5
            if sc == api.status_code.too_many_requests:
                try:
                    t = response.json()['retry_after']
                except:
                    t = 10 # just assume 10
                    self.log("Got http rate limited, but response had no retry_after parameter; %s" % response.text, severity = log_severity.warning)
                    pass
            
            self.log("HTTP will wait %.1f seconds before retrying due to global rate limit" % t)
            time.sleep(t)
            return self._wrap_http(method, *args, **kwargs)
        else:
            raise error.UnexpectedResponse("Got unknown HTTP status code: %d" % sc)
    
    def _rate_limited_http(self, method, url, *args, **kwargs):
        bucket_key = "%s / %s" % (method, url)
        
        if bucket_key in self._rate_bucket_lookup:
            bucket = self._rate_buckets[self._rate_bucket_lookup[bucket_key]]
            
            if bucket['remaining'] <= 0 and bucket['reset_at'] > time.time():
                t = bucket['reset_at'] - time.time()
                self.log("HTTP will wait %.1f seconds before retrying due to bucket rate limit" % t)
                time.sleep(t)
            
            bucket['remaining'] -= 1
            
        data, response = self._wrap_http(method, url, *args, **kwargs)
        
        # attempt to parse the rate limit
        if "X-RateLimit-Bucket" in response.headers:
            bucket_id = str(response.headers["X-RateLimit-Bucket"])
            
            bucket = None
            if bucket_id in self._rate_buckets:
                bucket = self._rate_buckets[bucket_id]
            else:
                bucket = {
                    "reset_at": time.time() + 10,
                    "limit": 5,
                    "remaining": 4
                }
                self._rate_buckets[bucket_id] = bucket
            
            self._rate_bucket_lookup[bucket_key] = bucket_id
        
            if "Date" in response.headers and "X-RateLimit-Reset" in response.headers:
                discord_current_time = util.parse_date_header(response.headers["Date"])
                discord_time_of_reset = float(response.headers["X-RateLimit-Reset"])
                bucket["reset_at"] = time.time() + discord_time_of_reset - discord_current_time
            elif "X-RateLimit-Reset-After" in response.headers:
                bucket["reset_at"] = time.time() + float(response.headers["X-RateLimit-Reset-After"])
            
            if "X-RateLimit-Limit" in response.headers:
                bucket["limit"] = int(response.headers["X-RateLimit-Limit"])
            
            if "X-RateLimit-Remaining" in response.headers:
                bucket["remaining"] = int(response.headers["X-RateLimit-Remaining"])
        
        return data, response
    
    def _get_gateway(self):
        data, _ = self._wrap_http("get", "https://discord.com/api/v9/gateway")
        if not 'url' in data:
            raise error.UnexpectedResponse("response did not contain 'url' parameter: %s" % data)
        
        return data['url']
    
    '''
        internal funcs
    '''
    async def _handle_event(self, evt, event_type, *data):
        if event_type in self.event_handlers:
            for h in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(h):
                        await h(evt.data, *data)
                    else:
                        h(evt.data, *data)
                except BaseException as e:
                    self.log_error(e)
                    raise error.CallbackError(e)
    
    async def _run_periodics(self):
        while True:
            await asyncio.sleep(0.01)
            now = time.time()
            for d in self.periodics:
                # [dt, time_last_called, callback] = d
                dt = now - d[1]
                if dt >= d[0]:
                    try:
                        if asyncio.iscoroutinefunction(d[2]):
                            await d[2](dt)
                        else:
                            d[2](dt)
                    except KeyboardInterrupt as e:
                        self.stopped = True
                        return
                    except BaseException as e:
                        self.log_error(e)
                    now = time.time()
                    d[1] = now
    
    async def _send_payload(self, pl):
        assert isinstance(pl, api.payload.OutgoingPayload), "payload must be discordbot.api.payload.OutgoingPayload"
        await self.gateway_connection.send(pl.dumps())
        
    async def _wait_for_valid_payload(self):
        while True:
            try:
                return api.payload.Payload(await self.gateway_connection.recv())
            except error.ReceivedInvalidPayload as e:
                self.log_error(e)
    
    async def _wait_for_payload(self, opcode):
        while True:
            pl = await self._wait_for_valid_payload()
            if pl.opcode == opcode:
                return pl
            else:
                self.log("Waiting for payload w/ opcode %d but got one with opcode %d" % (opcode, pl.opcode))
    
    async def _wait_for_valid_event(self):
        while True:
            try:
                return api.payload.Event(await self._wait_for_payload(api.opcode.event))
            except error.InvalidEventPayload as e:
                self.log_error(e)
    
    async def _wait_for_event(self, event_name):
        while True:
            evt = await self._wait_for_valid_event()
            if evt.name == event_name:
                return evt
            else:
                self.log("Waiting for event w/ name %s but got one with name %s" % (event_name, evt.name))
    
    async def _on_payload_received(self, pl):
        if pl.opcode == api.opcode.event:
            evt = api.payload.Event(pl)
            self.last_received_sequence = max(self.last_received_sequence, evt.sequence)
            if evt.name == 'MESSAGE_CREATE':
                evt = api.payload.MessageCreateEvent(evt)
                await self._handle_event(evt, event.guild_message_sent, evt.message)
            elif evt.name == "MESSAGE_UPDATE":
                evt = api.payload.MessageEditEvent(evt)
                if evt.after == None:
                    evt.after = self.get_message(evt.data["channel_id"], evt.data["id"])
                await self._handle_event(evt, event.guild_message_edited, evt.before, evt.after)
            elif evt.name == "MESSAGE_DELETE":
                evt = api.payload.MessageDeleteEvent(evt)
                await self._handle_event(evt, event.guild_message_deleted, evt.message)
            elif evt.name == "GUILD_CREATE":
                evt = api.payload.GuildCreateEvent(evt)
                await self._handle_event(evt, event.guild_created, evt.guild)
            elif evt.name == "MESSAGE_DELETE_BULK":
                evt = api.payload.MessageBulkDeleteEvent(evt)
                await self._handle_event(evt, event.guild_message_bulk_delete, evt.messages, evt.channel, evt.guild)
            elif evt.name == "RESUMED":
                pass
            else:
                self.log("Unknown event received: %s" % evt, severity = log_severity.warning)
        elif pl.opcode == api.opcode.heartbeat_ack:
            pass
        elif pl.opcode == api.opcode.reconnect or pl.opcode == api.opcode.session_invalidated:
            self.reconnect = True
            if pl.opcode == api.opcode.session_invalidated:
                self.session_id = None
        else:
            self.log("Unknown payload received: %s" % pl, severity = log_severity.warning)
    
    async def _heartbeat(self, dt):
        if not self.ready:
            return
        await self._send_payload(api.payload.OutgoingHeartbeat(self.last_received_sequence))
    
    async def _run(self):
        # run periodic tasks
        if self.periodic_task is None:
            self.periodic_task = asyncio.create_task(self._run_periodics())
        
        # connect to gateway
        try:
            self.gateway_endpoint = self._get_gateway()
        except BaseException as e:
            self.log_error(e)
            return 1, "Could not find gateway endpoint"
        try:
            self.gateway_connection = await websockets.connect(self.gateway_endpoint)
        except BaseException as e:
            self.log_error(e)
            return 2, "Could not connect to gateway"
        self.log("found gateway: %s" % self.gateway_endpoint)
        
        # receive the hello payload
        hello = None
        try:
            hello = api.payload.Hello(await self._wait_for_payload(api.opcode.hello))
        except BaseException as e:
            self.log_error(e)
            await self.gateway_connection.close(1000) # will not reconnect
            return 3, "Failed to receive hello payload"
        self.log("received hello")
        
        # update timings of periodic heartbeats
        for d in self.periodics:
            if d[2] == self._heartbeat:
                d[0] = hello.heartbeat_interval
                break
        
        # initial heartbeat
        try:
            await self._send_payload(api.payload.OutgoingHeartbeat(self.last_received_sequence))
        except BaseException as e:
            self.log_error(e)
            await self.gateway_connection.close(1000) # will not reconnect
            return 4, "Failed to send initial heartbeat"
        self.log("sent initial heartbeat")
            
        # wait for ACK
        try:
            await self._wait_for_payload(api.opcode.heartbeat_ack)
        except BaseException as e:
            self.log_error(e)
            await self.gateway_connection.close(1000) # will not reconnect
            return 5, "Failed to receive initial heartbeat ACK"
        self.log("received initial heartbeat ACK")
        
        # resume if possible, else identify
        if self.session_id != None:
            # resume
            r = api.payload.Resume(
                self.token,
                self.session_id,
                self.last_received_sequence
            )
            try:
                await self._send_payload(r)
            except BaseException as e:
                self.log_error(e)
                await self.gateway_connection.close(1000) # will not reconnect
                return 6, "Failed to resume"
            self.log("resumed using: %s" % r.dumps())
        else:
            # identify
            try:
                await self._send_payload(api.payload.OutgoingIdentify(
                    self.token,
                    self.intents,
                    self.bot_identifier
                ))
            except BaseException as e:
                self.log_error(e)
                await self.gateway_connection.close(1000) # will not reconnect
                return 7, "Failed to identify"
            self.log("identified")
            
            # wait for ready event
            ready = None
            try:
                ready = api.payload.ReadyEvent(await self._wait_for_event('READY'))
            except BaseException as e:
                self.log_error(e)
                await self.gateway_connection.close(1000) # will not reconnect
                return 8, "Failed to receive ready event"
            self.log("received ready event. session_id: %s" % ready.session_id)
            self.user = ready.user
            self.session_id = ready.session_id
        
            # run init
            self.ready = True
            await self._handle_event(ready, event.ready)
        
        try:
            while True:
                pl = await self._wait_for_valid_payload()
                if pl.opcode == 0:
                    self.log("received event payload: %s" % pl.raw["t"])
                else:
                    self.log("received payload opcode: %d - %s" % (pl.opcode, api.opcode.get_name(pl.opcode)))
                try:
                    await self._on_payload_received(pl)
                except error.DiscordError as e:
                    self.log_error(e)
                
                if self.reconnect:
                    self.log("Bot will reconnect to gateway.")
                    self.reconnect = False
                    try:
                        await self.gateway_connection.close(1012) # will reconnect
                    except:
                        pass
                    return await self._run()
        except (KeyboardInterrupt, asyncio.exceptions.CancelledError) as e:
            self.stopped = True
            try:
                await self.gateway_connection.close(1000) # will not reconnect
            except:
                pass
            return 0, "KeyboardInterrupt"
        except (BaseException, asyncio.IncompleteReadError) as e:
            
            if self.stopped:
                try:
                    await self.gateway_connection.close(1000) # will not reconnect
                except:
                    pass
                return 0, "Logged out."
            else:
                try:
                    await self.gateway_connection.close(1012) # will reconnect
                except:
                    pass
            
            if isinstance(e, asyncio.IncompleteReadError):
                self.log("Reconnecting due to an IncompleteReadError: %s" % e)
            else:
                self.log_error(e)
                self.log("Due to above error, the bot will reconnect to the gateway.", severity = log_severity.important)
            
            self.ready = False
            return await self._run()
    
    def _command_handler(self, raw, message):
        if not message.content.startswith(self.command_prefix):
            return
        
        if not "member" in message.raw:
            return
        if not "roles" in message.raw["member"]:
            return
        roles = [str(x) for x in message.raw["member"]["roles"]]
        
        parts = message.content.replace("\u200b", "").split()
        sent_cmd = parts[0][len(self.command_prefix):]
        sent_args = parts[1:]
        
        for cmd in self.commands:
            if not sent_cmd in cmd.split("_,_"):
                continue
            
            cmd_info = self.commands[cmd]
            if cmd_info['required_role'] != None and not cmd_info['required_role'] in roles:
                return
            
            # make sure that the correct arguments are present
            use_args = []
            for arg_info in cmd_info['args']:
            
                if len(sent_args) <= 0:
                    if 'default' in arg_info:
                        use_args.append(arg_info['default'])
                    else:
                        return # invalid
                else:
                    arg = sent_args.pop(0)
                    
                    if arg_info['type'] == "int":
                        try:    
                            arg = int(arg)
                        except:
                            return
                        if 'min' in arg_info and arg < arg_info['min']:
                            return
                        if 'max' in arg_info and arg > arg_info['max']:
                            return
                    elif arg_info['type'] == "user":
                        # try to get their ID
                        arg = ''.join([c for c in arg if '0' <= c <= '9']) # i love python
                        try:
                            n = int(arg)
                            assert n > 1_000_000
                        except:
                            return
                        
                        # convert to a user
                        user = None
                        if "mentions" in message.raw:
                            for m in message.raw["mentions"]:
                                if str(m["id"]) == arg:
                                    user = api.structure.User(m)
                                    break
                        if user is None:
                            user = api.structure.User({"id": arg})
                        
                        arg = user
                    
                    use_args.append(arg)
            
            cmd_info['handler'](message, *use_args)
            break
    
    '''
        user-exposed apis
    '''
    def on_event(self, evt, callback):
        assert issubclass(evt, event.Base), "event must be a discordbot.event"
        if not evt in self.event_handlers:
            self.event_handlers[evt] = []
        self.event_handlers[evt].append(callback)
    
    def remove_callback(self, evt, callback):
        assert evt in self.event_handlers and callback in self.event_handlers[evt], "event callback is not registered, you must Bot.on_event() it first"
        self.event_handlers[evt].remove(callback)
        if len(self.event_handlers[evt]) == 0:
            del self.event_handlers[evt]
    
    def register_periodic(self, dt, callback):
        self.periodics.append([dt, time.time(), callback])
    
    def send_message(self, channel, content = '', embeds = [], reply_to = None, force_reply = False, reply_ping = None, allowed_mentions = None):
        if isinstance(channel, api.structure.Channel):
            channel = channel.id
        
        info = {
            "content": content,
            "embeds": embeds,
        }
        
        if reply_to != None:
            if isinstance(reply_to, api.structure.Message):
                reply_to = reply_to.id
            info["message_reference"] = {
                "message_id": reply_to,
                "fail_if_not_exists": force_reply
            }
        
        if reply_ping != None:
            if allowed_mentions == None:
                allowed_mentions = {"parse": ["roles", "users", "everyone"]}
            if "replied_user" in allowed_mentions and allowed_mentions["replied_user"] != reply_ping:
                self.log("In send_message, tried to set allowed_mentions[\"replied_user\"] AND reply_ping parameter. Using reply_ping instead.", severity = log_severity.warning)
            allowed_mentions["replied_user"] = reply_ping
        info["allowed_mentions"] = allowed_mentions
        
        try:
            data, _ = self._rate_limited_http(
                "post",
                "https://discord.com/api/v9/channels/%s/messages" % channel,
                json.dumps(info),
                headers = {
                    "Authorization": "Bot %s" % self.token,
                    "Content-Type": "application/json"
                }
            )
            
            try:
                return api.structure.Message(data)
            except error.InvalidAPIObject as e:
                raise error.UnexpectedResponse("Response was not a valid Message object: %s" % e)
        except error.DiscordError as e:
            raise error.MessageSendFailure(str(e))
    
    def get_messages(self, channel, n):
        if isinstance(channel, api.structure.Channel):
            channel = channel.id
        result, response = self._rate_limited_http(
            "get",
            "https://discord.com/api/v9/channels/%s/messages" % channel,
            params = {
                "limit": n
            },
            headers = {
                "Authorization": "Bot %s" % self.token,
                "Content-Type": "application/json"
            }
        )
        if not isinstance(result, list):
            raise error.UnexpectedResponse("Did not return list, actually got:", result)
        
        for i in range(len(result)):
            try:
                result[i] = api.structure.Message(result[i])
            except error.InvalidAPIObject as e:
                raise error.UnexpectedResponse("Response had invalid message at index[%d]: %s" % (i, e))
        
        return result
    
    def get_message(self, channel, message_id):
        if isinstance(channel, api.structure.Channel):
            channel = channel.id
        if isinstance(message_id, api.structure.Message):
            message_id = message_id.id
        result, response = self._rate_limited_http(
            "get",
            "https://discord.com/api/v9/channels/%s/messages/%s" % (channel, message_id),
            headers = {
                "Authorization": "Bot %s" % self.token,
                "Content-Type": "application/json"
            }
        )
        
        try:
            result = api.structure.Message(result)
        except error.InvalidAPIObject as e:
            raise error.UnexpectedResponse("Response had invalid message w/ error: %s" % (e))
        
        return result
    
    def purge(self, channel, n):
        n = min(max(n, 1), 100)
        if isinstance(channel, api.structure.Channel):
            channel = channel.id
        
        messages = self.get_messages(channel, n)
        ids = [m.id for m in messages]
        
        result, response = self._rate_limited_http(
            "post",
            "https://discord.com/api/v9/channels/%s/messages/bulk-delete" % channel,
            json.dumps({
                "messages": ids,
            }),
            headers = {
                "Authorization": "Bot %s" % self.token,
                "Content-Type": "application/json"
            }
        )
        
        return len(ids)
    
    def kick(self, guild, member, reason = None):
        if isinstance(guild, api.structure.Guild):
            guild = guild.id
        if isinstance(member, api.structure.User):
            member = member.id
        
        headers = {
            "Authorization": "Bot %s" % self.token,
            "Content-Type": "application/json"
        }
        if reason != None:
            headers["X-Audit-Log-Reason"] = str(reason)
        
        
        data, _ = self._rate_limited_http(
            "delete",
            "https://discord.com/api/v9/guilds/%s/members/%s" % (guild, member),
            headers = headers
        )
        return data
        
    def ban(self, guild, member, reason = None, delete_message_days = 0):
        if isinstance(guild, api.structure.Guild):
            guild = guild.id
        if isinstance(member, api.structure.User):
            member = member.id
        
        headers = {
            "Authorization": "Bot %s" % self.token,
            "Content-Type": "application/json"
        }
        if reason != None:
            headers["X-Audit-Log-Reason"] = str(reason)
        
        data, _ = self._rate_limited_http(
            "put",
            "https://discord.com/api/v9/guilds/%s/bans/%s" % (guild, member),
            json.dumps({
                "delete_message_days": delete_message_days
            }),
            headers = headers
        )
        return data
    
    def stop(self):
        self.stopped = True
    logout = stop
    
    def register_command(self, cmd, description, handler, required_role = None, args = []):
        assert isinstance(cmd, (list, str)), "cmd may only be a string or list of strings"
        if isinstance(cmd, list):
            assert all(map(lambda x: isinstance(x, str), cmd)), "list of commands must only contain strings"
        
        cmd_key = cmd if isinstance(cmd, str) else "_,_".join(cmd)
        if cmd_key in self.commands:
            self.log("called register_command with command name that is already registered (\"%s\"). Overwriting." % cmd_key, severity = log_severity.warning)
        self.commands[cmd_key] = {
            "description": str(description),
            "handler": handler,
            "required_role": str(required_role) if required_role != None else None,
            "args": args
        }
    
    def register_default_commands(self):
        # just reply "pong"
        def cmd_ping(message):
            self.send_message(message.channel, "Pong!", reply_to = message, reply_ping = False)
        self.register_command("ping", "The bot will reply 'Pong!'", cmd_ping)
        
        # show commands list
        def cmd_cmds(message):
            self.send_message(message.channel, embeds = [
                {
                    "fields": [
                        {
                            "name": "%s%s %s" % (
                                self.command_prefix.replace("`", "\\`"),
                                ("{" + ', '.join(cmd.split("_,_")) + "}") if cmd.count("_,_") >= 1 else cmd,
                                ' '.join(["[%s]" % a['name'] for a in info['args']])
                            ),
                            "value": "%s\n%s" % (
                                "@everyone" if info["required_role"] is None else util.mention_role(info["required_role"]),
                                info["description"]
                            )
                        } for (cmd, info) in self.commands.items() 
                    ]
                }
            ], allowed_mentions = {
                "parse": []
            }, reply_to = message, reply_ping = False)
        self.register_command("cmds", "Shows a list of the bot's commands", cmd_cmds)
    
    def run(self, intents):
        self.intents = util.get_flags(*intents)
        self.running = True
        a,b = asyncio.run(self._run())
        self.running = False
        return a,b