from __future__ import annotations
from atomic.channels.configuration import ChannelConfiguration
from atomic.quarks import QuarkManager
from atomic.particles import ParticleFactory, Particle


def atom(name, output=None):

  def decorator(f):
    AtomBuilder.get_instance().set_name(name)
    AtomBuilder.get_instance().set_output(output)
    return f

  return decorator


def add_particle(name, package):

  def decorator(f):
    AtomBuilder.get_instance().add_particle(name, package)
    return f

  return decorator


class Atom:

  def __init__(self):
    self.__particles = []

  def add(self, particle: Particle):
    self.__particles.append(particle)

  def run(self):
    for service in self.__particles:
      service.run()

  def stop(self):
    for service in self.__particles:
      service.stop()


class AtomBuilder:
  _instance = None

  @classmethod
  def get_instance(cls) -> AtomBuilder:
    if cls._instance is None:
      cls._instance = AtomBuilder()
    return cls._instance

  def __init__(self):
    self.__name = None
    self.__output = None
    self.__amqp_uri = "amqp://guest:guest@localhost:5672/"
    self.__max_threads = 4
    self.__heartbeat = 0
    self.__particles = []
    self.__prefetch_count = 1000
    self.__confirm_sent = True
    self.__confirm_delivery = True

  def set_name(self, name):
    self.__name = name

  def add_particle(self, name, package):
    self.__particles.append({'name': name, 'package': package})

  def set_output(self, output):
    self.__output = output

  def set_amqp_uri(self, amqp_uri):
    self.__amqp_uri = amqp_uri

  def set_max_thread(self, max_threads):
    self.__max_threads = max_threads

  def set_heartbeat(self, heartbeat):
    self.__heartbeat = heartbeat

  def set_prefetch_count(self, prefetch_count):
    self.__prefetch_count = prefetch_count

  def set_confirm_sent(self, confirm_sent):
    self.__confirm_sent = confirm_sent

  def set_confirm_delivery(self, confirm_delivery):
    self.__confirm_delivery = confirm_delivery

  def build(self):
    atom = Atom()

    for particle in self.__particles:
      # Load handlers packages
      __import__(particle['package'])

      config_receiver = ChannelConfiguration()
      config_receiver.uri = self.__amqp_uri
      config_receiver.exchange.name = self.__name
      config_receiver.queue.name = '%s.%s' % (self.__name, particle['name'])

      for routing_key in QuarkManager.get_instance().get_routing_keys():
        config_receiver.queue.add_routing_key(routing_key)

      config_receiver.max_threads = self.__max_threads
      config_receiver.heartbeat = self.__heartbeat
      config_receiver.prefetch_count = self.__prefetch_count
      config_receiver.confirm_sent = self.__confirm_sent
      config_receiver.confirm_delivery = self.__confirm_delivery

      config_sender = ChannelConfiguration()
      config_sender.uri = self.__amqp_uri
      config_sender.exchange.name = self.__output if self.__output is not None else self.__name
      config_sender.heartbeat = self.__heartbeat
      config_sender.confirm_sent = self.__confirm_sent
      config_sender.confirm_delivery = self.__confirm_delivery

      quark_manager = QuarkManager.get_instance().clone()
      particle = ParticleFactory.create(
          name=particle['name'],
          config_sender=config_sender,
          config_receiver=config_receiver,
          quark_manager=quark_manager)
      QuarkManager.get_instance().clear()
      atom.add(particle)
    return atom
