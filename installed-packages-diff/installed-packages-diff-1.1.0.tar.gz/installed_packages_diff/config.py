from yaml import load
import logging

try:
  from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
  from yaml import Loader, Dumper


class Server(object):
  def __init__(self, raw, *, type_from_group=None):
    self.hostname = raw["hostname"]
    self.username = raw.get("username", None)
    self.excludes = {e for e in raw.get("excludes", [])}
    self.type = raw.get("type", type_from_group)


class Group(object):
  def __init__(self, name, raw):
    self.name = name
    type = raw.get("type", "rpm")
    self.servers = [Server(server, type_from_group=type) for server in
                    raw["servers"]]


class Config(object):
  def __init__(self, raw):
    self.raw = raw
    groups_dict = self.raw.get("groups", {})
    self.groups = [Group(name, groups_dict[name]) for name in groups_dict]


def load_config(input):
  if isinstance(input, str):
    logging.info(f"Opening config {input}...")
    input = open(input, 'rb')

  with input as stream:
    data = load(stream, Loader=Loader)
    return Config(data)
