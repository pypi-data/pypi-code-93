#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "provide video support"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "2.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2008"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules

### PyGObject is a Python package which provides bindings for GObject
### The GLib Object System( or GObject), allow to manipulating objects in C programming language
import gi
### GStreamer is crossplatform(android) pipeline-based multimedia framework written in C
gi.require_version('Gst', '1.0')
from gi.repository import Gst

import time



### constants
FRAMERATE = 30 # TV frames by seconds



def init_gst(options=None):
	"""Initializes the GStreamer library"""
	### with None arguments, no command line options will be parsed by GStreamer.
	Gst.init(options)
	
	
def get_frame(video_file,moment,output_image_file):
	""" save as image a frame from video"""
	caps = Gst.Caps('image/png')
	
	pipeline = Gst.ElementFactory.make("playbin", "new_playbin")
	pipeline.set_property('uri',"file://" + video_file)
	pipeline.set_state(Gst.State.PLAYING)
	
	#Allow time for it to start
	time.sleep(0.5)
	
	# jump to the right moment
	seek_time = moment * Gst.SECOND
	pipeline.seek(1.0, Gst.Format.TIME,(Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE),Gst.SeekType.SET, seek_time , Gst.SeekType.NONE, -1)

	#Allow video to run to prove it's working, then take snapshot
	time.sleep(1)
	buffer = pipeline.emit('convert-sample', caps)
	buff = buffer.get_buffer()
	result, map = buff.map(Gst.MapFlags.READ)
	if result:
		data = map.data
		pipeline.set_state(Gst.State.NULL)
		with open(output_image_file, 'wb') as snapshot :
			snapshot.write(data)
		return True
	else:
		return False

