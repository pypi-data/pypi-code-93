#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "provide client for internet server connexion"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "2.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2008"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### moduls for internet connection 
#import ipaddress# convert check ip adress
import socket #Low-level networking interface.
#import asyncio #provides the basic infrastructure for writing asynchronous socket service clients and servers.
#import ssl# encryption and peer authentication facilities for network sockets, both client-side and server-side.
#from packet import Packet # not available in repo
#from message import Message # not available in repo



### default waiting mode for create_connection and recv()
### None = infinit wait (bad option because blocking the prog)
### 0 = dont wait (this option not give enought time for connexion with server)
### seconds =  wait this time
### When the socket module is first imported, the default timeout is None.
TIMEOUT=None

### default size in octect for recv_buffer
### 1024 octect is common
### Should consider the max size of Ethernet packets (~1500 bytes) and the max size of TCP packets (~64Kb)
BUFFER=1024

### stats index
TIME_STAT_INDEX=0
DONE_STAT_INDEX=1
FAIL_STAT_INDEX=2



def get_interface_qantum():
	"""returns the quantity of available connection interfaces"""
	return len(socket.if_nameindex())

def get_interface(index):
	"""from the given index returns the specified connection interface name"""
	return socket.if_indextoname(index)



class Client:
	"""client for connexion by internet on server"""
	def __init__(self,host,port):
		"""need an host name or IP address and a port number"""
		self.connection= None
		
		self.host= host
		self.port= port

		self.connect_stat=[0,0,0]
		self.send_stat=[0,0,0]
		self.recv_stat=[0,0,0]
		
		
	def connect(self,timeout=TIMEOUT):
		"""attempt connexion on server (timeout is seconds)"""
		try :
			start_time=time.perf_counter()#to measure time intervals
			### use Ephemeral port interface for (bind_addr,bind_port) IANA suggests 49152 to 65535
			self.connection = socket.create_connection((self.host,self.port),timeout)#,(bind_addr,bind_port))
			laps=time.perf_counter()-start_time#to measure time intervals
			self.connect_stat[TIME_STAT_INDEX]+=laps
		except (ConnectionRefusedError) as err :
			### ConnectionRefusedError=ECONNREFUSED means connection was refused by the server or server not listening on the specified port
			print(err)
			self.connect_stat[FAIL_STAT_INDEX]+=1
			self.connection= None# normaly no need because still None
			return False
		except (socket.timeout,BlockingIOError) as err :
			### cannot conect with the server this time
			print(err)
			self.connect_stat[FAIL_STAT_INDEX]+=1
			self.connection= None# normaly no need because still None
			return False
		else:
			self.connect_stat[DONE_STAT_INDEX]+=1
			self.connection.settimeout(0)# unblock and unwait future socket operations
			return True


	def connection_check(self):
		"""check server connexion validity"""
		if self.connection :
			return True
		else:
			return False
				
		
	def send(self,data):
		"""send the giving data to the server"""
		#print("send data")
		try :
			start_time=time.perf_counter()
			### MSG_DONTWAIT allow to not waiting indefinitely
			### MSG_DONTWAIT is useful only if the socket timeout is None
			reply = self.connection.sendall(data,socket.MSG_DONTWAIT)# None is returned on success.
			### cannot assume that every send() will result in exactly one recv() with exactly the same number of bytes.
			laps=time.perf_counter()-start_time#to measure time intervals
			self.send_stat[TIME_STAT_INDEX]+=laps
			if not reply == None :
				raise ConnectionError("ERR:received anomalous reply")# raised ConnectionError is not catch by BrokenPipeError,ConnectionResetError
		except (socket.timeout,BrokenPipeError,ConnectionResetError,ConnectionError) as err :# ConnectionError catch raised BrokenPipeError,ConnectionResetError
			### connection with server is lost
			### socket.timeout means that the deadline for sending data has been exceeded
			### BrokenPipeError=EPIPE and ESHUTDOWN means connection was closed with no data left unread in the socket buffer.
			### ConnectionResetError=ECONNRESET  means connection closed while still there unhandled data in the socket buffer.
			print("send data fail: ",err)
			self.send_stat[FAIL_STAT_INDEX]+=1
			self.connection= None
			return False
		except (BlockingIOError) as err :
			### cannot send data at this time and dont want to wait for that
			print("send dont wait: ",err)
			return False
		else:
			self.send_stat[DONE_STAT_INDEX]+=1
			return True
		
		
	def receive(self,size):
		"""receive data from the server"""
		#print("receive data")
		try :
			start_time=time.perf_counter()
			buffer=b''
			while size :
				### With ancillary <Unix sockets> can communicate information that cannot be communicated by network.
				#data = self.s.recvmsg(bufsize[, ancbufsize[, flags]])
				### "bytearray" as buffer can be use instead "bytes string"
				### "bytearray" are immutable(editable), "bytes string" are not
				### both have the same non-mutating methods and the same indexing and slicing behavior.
				#self.s.recvmsg_into(buffers[, ancbufsize[, flags]])
				#self.s.recv_into(self.buffer,flags=socket.MSG_DONTWAIT)
				### MSG_DONTWAIT allow to not waiting indefinitely
				### MSG_DONTWAIT is useful only if the socket timeout is None
				data = self.connection.recv(size,socket.MSG_DONTWAIT)
				### The size in recv() is a maximum size.
				### recv() can return fewer bytes if fewer are available.
				if not data :# recv returns an empty string if the socket is disconnected
					raise ConnectionError("ERR:received nothing")# raised ConnectionError is not catch by BrokenPipeError,ConnectionResetError
				else :
					buffer+=data
					size -= len(data)
			laps=time.perf_counter()-start_time#to measure time intervals
			self.recv_stat[TIME_STAT_INDEX]+=laps
		except (socket.timeout,ConnectionResetError,BrokenPipeError) as err :
			### connection with server is lost
			### socket.timeout means that the deadline for sending data has been exceeded
			### BrokenPipeError=EPIPE and ESHUTDOWN means connection was closed with no data left unread in the socket buffer.
			### ConnectionResetError=ECONNRESET  means connection closed while still there unhandled data in the socket buffer.
			print("recv data fail: ",err)
			self.recv_stat[FAIL_STAT_INDEX]+=1
			self.connection = None
			return b''
		except (BlockingIOError,ConnectionError) as err :# ConnectionError catch raised BrokenPipeError,ConnectionResetError
			### no data at this time and dont want to wait for it
			print("recv not wait: ",err)
			return b''
		else:
			self.recv_stat[DONE_STAT_INDEX]+=1
			return buffer
		

	def get_stats(self):
		"""returns quality stats history of the connexion"""
		stats={'connecting':{},'sending':{},'receiving':{}}
		
		stats['connecting']['times']=self.connect_stat[TIME_STAT_INDEX]
		stats['connecting']['success']=self.connect_stat[DONE_STAT_INDEX]
		stats['connecting']['fails']=self.connect_stat[FAIL_STAT_INDEX]

		stats['sending']['times']=self.send_stat[TIME_STAT_INDEX]
		stats['sending']['success']=self.send_stat[DONE_STAT_INDEX]
		stats['sending']['fails']=self.send_stat[FAIL_STAT_INDEX]
		
		stats['receiving']['times']=self.recv_stat[TIME_STAT_INDEX]
		stats['receiving']['success']=self.recv_stat[DONE_STAT_INDEX]
		stats['receiving']['fails']=self.recv_stat[FAIL_STAT_INDEX]

		return stats


	def stop(self):
		"""stop the connexion properly with server"""
		###  to close the connection in a timely fashion, call shutdown() before close().
		self.connection.shutdown(socket.SHUT_RDWR) #further sends and receive are disallowed
	def close(self):
		"""close the connexion with server"""
		self.connection.close()
