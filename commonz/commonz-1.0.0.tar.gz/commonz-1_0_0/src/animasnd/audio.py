#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "provide audio support"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "3.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2008"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### importable audio modules https://wiki.python.org/moin/Audio/
#	PyMedia		obsolete since version python 2.5 2004
#	pysonic		FMOD wrapper last version pySonic 0.8 2005 ( not in repo)
#	playsound	without any option just play an audio file on cross platform(not py3,not in repo)
#	wave			support only WAV sound format.  (too limited)
#	Pyglet		cross-platform windowing and multimedia library.(not specific to audio)
#	Pygame		designed for writing games. (is not specific to audio)
#	GStreamer	a pipeline-based multimedia framework written in C. crossplatform android
#	PyAudio		cross-platform bindings for PortAudio,(py3,in repo)
#	Simpleaudio	OSX,Windows,Linux MIT license,less options than Pyaudio (Py3 but not in repo)
#	pyOpenAL		Cross Platform 3D Audio

### PyGObject is a Python package which provides bindings for GObject
### The GLib Object System( or GObject), allow to manipulating objects in C programming language
import gi
### GStreamer is crossplatform(android) pipeline-based multimedia framework written in C
gi.require_version('Gst', '1.0')
from gi.repository import Gst



### Sampling rates in Hz
### rates higher than about 50 kHz to 60 kHz cannot supply more usable information for human listeners.
INTERCOM_FREQ = 8000   # same as cheap intercoms
RADIO_FREQ = 32000   # same as transmission FM radio
CD_FREQ = 44100   # same as audio CD
DAT_FREQ = 48000   # same as profesional digital DAT tape
HD_FREQ = 96000   # same high DVD BD records

### Bits depth
CD_SAMPLES = 8 
CD_SAMPLES = 16 # CD quality audio
CD_SAMPLES = 24 



def init_gst(options=None):
	"""Initializes the GStreamer library"""
	### with None arguments, no command line options will be parsed by GStreamer.
	Gst.init(options)



class Player1:
	"""audio file player"""
	def __init__(self,music_file):
		"""Initialize player with a audio file"""
		###Creating a gst pipeline
		self.pipeline = Gst.Pipeline.new("new_pipeline")


		### Create elements and add theme in pipeline
		### creating the sourcefile element and it in pipeline
		self.filesrc = Gst.ElementFactory.make("filesrc", "filesrc")
		self.filesrc.set_property("location", music_file)
		self.pipeline.add(self.filesrc)
		
		###creating and adding the decodebin element
		### a "magic" element able to configure itself to decode pretty much anything
		self.decoder = Gst.ElementFactory.make("decodebin","decode")
		### the output will be created at runtime when the decoder start receiving some data
		self.decoder.connect("pad-added",self.decod_src_created) 
		self.pipeline.add(self.decoder)
		
		### add output element,for "play" the sound it receives
		self.sink = Gst.ElementFactory.make('autoaudiosink',"sink")
		self.pipeline.add(self.sink)


		### linking elements
		###  file_src -> decoder
		self.filesrc.link(self.decoder)
		
		
	def decod_src_created(self, element, pad):
		"""linking the decoder's source pad to the sink"""
		pad.link( self.sink.get_static_pad("sink") )
		
		
	def play(self):
		"""play sound"""
		self.pipeline.set_state(Gst.State.PLAYING)


	def __del__(self):
		"""free ressources at del time"""
		self.player.set_state(Gst.State.NULL)



class Player2(object):
	"""audio file player"""
	def __init__(self,music_file):
		"""Initialize player with a audio file"""
		self.player = Gst.ElementFactory.make("playbin", "player")
		self.player.set_property("uri", "file://"+music_file)
		
		#fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
		#self.player.set_property("video-sink", fakesink)
		#print(dir(self.player))
		
		self.bus = self.player.get_bus()
		self.bus.add_signal_watch()
		self.bus.connect("message", self.on_message)		
		
	def on_message(self, bus, message):
		"""manage bus messages"""
		#print(bus, message)
		t = message.type
		if t == Gst.MessageType.EOS:
				self.player.set_state(Gst.State.NULL)
		elif t == Gst.MessageType.ERROR:
				self.player.set_state(Gst.State.NULL)
				err, debug = message.parse_error()
				print("Error: %s" % err, debug)
		

	def play(self):
		"""play sound"""
		self.player.set_state(Gst.State.PLAYING)
		
	def stop(self):
		"""stop sound"""
		self.player.set_state(Gst.State.READY)
		
	def pause(self):
		"""pause sound"""
		self.player.set_state(Gst.State.PAUSED)		
			
	def set_volume(self,volume):
		"""la valeur volume passe en argument doit etre entre 0 et 1"""
		self.player.set_delay(10004040)
		self.player.volume=volume*10
		
	def __del__(self):
		"""free ressources at del time"""
		self.player.set_state(Gst.State.NULL)


