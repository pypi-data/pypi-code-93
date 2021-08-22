#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "provide internet server connexion for clients"#information describing the purpose of this module
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
### the socket.accept() blok  while waiting clients connections
### it should be to fixable by using threads or async
import socket #Low-level networking interface.
#import socketserver # allow to make network servers easly,(includ threaded server)
#import asyncio #provides the basic infrastructure for writing asynchronous socket service clients and servers.
#import ssl# encryption and peer authentication facilities for network sockets, both client-side and server-side.
#from packet import Packet # not available in repo
#from message import Message # not available in repo



### Unix Domain sockets transfer the information between processes running on same machine
### and not between processes running on different machines.
###
### ipv4 or the new ipv6 are the main choices
IP=socket.AF_INET
#IP=socket.AF_INET6

### for TCP use SOCK_STREAM
### for UDP uses SOCK_DGRAM
TIP=socket.SOCK_STREAM

### default waiting mode for socket operations
### None = infinit wait (blocking the prog)
### 0 = dont wait (this option not give enought time for connexion with server)
### seconds =  wait this time
### When the socket module is first imported, the default timeout is None.
TIMEOUT=None

### default size in octect for recv_buffer
### 1024 octect is common
### Should consider the max size of Ethernet packets (~1500 bytes) and the max size of TCP packets (~64Kb)
BUFFER=1024

### clients index
CONNECTION_INDEX=0
STATS_INDEX=1
### stats types index
RECV_STAT_INDEX=0
SEND_STAT_INDEX=1
### stats index
TIME_STAT_INDEX=0
DONE_STAT_INDEX=1
FAIL_STAT_INDEX=2



class Server:
	"""host server for connexions with clients"""
	def __init__(self,port,localhost=False,backlog=0,timeout=TIMEOUT):
		"""host can be ip address
		if localhost is True only connection on 127.0.0.1 are accepted"""

		self.clients={}
		
		### Set the default timeout in seconds(float) for new sockets.
		socket.setdefaulttimeout(timeout)
		
		### only available in the new nodule version
		#self.serv = socket.create_server((address,port),family=IP)#, backlog=None, reuse_port=False, dualstack_ipv6=False)
		
		self.serv = socket.socket(IP,TIP)
		### open the specified network interface
		if localhost :
			### only connection on 127.0.0.1 will be accepted
			self.serv.bind(('localhost',port))
		else :
			### in this vase address='' represents INADDR_ANY, which is used to bind all interfaces,	
			self.serv.bind(('',port))
		### makes server ready to accept clients connections.
		### backlog specifie how many clients wishing to connect at the same time the server will accept.
		### if backlog parameter is not specified, a default reasonable value is chosen.
		self.serv.listen(backlog)
		
		
	def greet(self):
		"""welcoming new clients connexions attempts"""
		try :
			connection,address_port = self.serv.accept()
		except (ConnectionAbortedError) as err :
			### ConnectionAbortedError=ECONNABORTED Client sent TCP reset (RST) before server has accepted the connection.
			#print('no greetings ',err)
			return None
		except (socket.timeout,BlockingIOError) as err :
			### no clients willing to connect at this time and don't want to wait for any
			#print('no greetings ',err)
			return None
		else:
			connection.settimeout(0)# unblock and unwait future socket operations
			address=address_port[0]
			if address in self.clients :
				self.clients[address][CONNECTION_INDEX]=connection
			else:
				send_stat=[0,0,0]
				recv_stat=[0,0,0]
				stats=[recv_stat,send_stat]
				self.clients[address]=[connection,stats]
			return address


	def connection_check(self,address):
		"""check clients connexions validity"""
		if self.clients[address][CONNECTION_INDEX] :
			return True
		else:
			return False
		
		
	def send(self,data,address):
		"""send the giving data to the clients"""
		#print("send data")
		client=self.clients[address]
		client_stats=client[STATS_INDEX][SEND_STAT_INDEX]
		try :
			start_time=time.perf_counter()
			### MSG_DONTWAIT allow to not waiting indefinitely
			### MSG_DONTWAIT is useful only if the socket timeout is None
			reply = client[CONNECTION_INDEX].sendall(data,socket.MSG_DONTWAIT)# None is returned on success.
			### cannot assume that every send() will result in exactly one recv() with exactly the same number of bytes.
			laps=time.perf_counter()-start_time#to measure time intervals
			client_stats[TIME_STAT_INDEX]+=laps
			if not reply == None :
				raise ConnectionError("ERR:received anomalous reply")# raised ConnectionError is not catch by BrokenPipeError,ConnectionResetError
		except (socket.timeout,BrokenPipeError,ConnectionResetError,ConnectionError) as err :# ConnectionError catch raised BrokenPipeError,ConnectionResetError
			### connection with client is lost
			### socket.timeout means that the deadline for sending data has been exceeded
			### BrokenPipeError=EPIPE and ESHUTDOWN means connection was closed with no data left unread in the socket buffer.
			### ConnectionResetError=ECONNRESET  means connection closed while still there unhandled data in the socket buffer.
			print("send data fail: ",err)
			client_stats[FAIL_STAT_INDEX]+=1
			client[CONNECTION_INDEX]=None
			return False
		except (BlockingIOError) as err :
			### cannot send data at this time and dont want to wait for that
			#print("send dont wait: ",err)
			return False
		else:
			client_stats[DONE_STAT_INDEX]+=1
			return True
		
		
	def receive(self,size,address):
		"""receive data from the clients"""
		#print("receive data")
		client=self.clients[address]
		client_stats=client[STATS_INDEX][RECV_STAT_INDEX]
		try :
			### With ancillary <Unix sockets> can communicate information that cannot be communicated by network.
			#data = self.s.recvmsg(bufsize[, ancbufsize[, flags]])
			### "bytearray" as buffer can be use instead "bytes string"
			### "bytearray" are immutable(editable), "bytes string" are not
			### both have the same non-mutating methods and the same indexing and slicing behavior.
			#self.s.recvmsg_into(buffers[, ancbufsize[, flags]])
			#self.s.recv_into(self.buffer,flags=socket.MSG_DONTWAIT)
			start_time=time.perf_counter()
			buffer=b''
			while size :
				### MSG_DONTWAIT allow to not waiting indefinitely
				### MSG_DONTWAIT is useful only if the socket timeout is None
				data = client[CONNECTION_INDEX].recv(size,socket.MSG_DONTWAIT)
				### The size of recv(size) is a maximum size.
				### recv(size) can return fewer bytes if fewer are available.
				if not data :# recv returns an empty string if the client is disconnected
					raise ConnectionError("ERR:received nothing")# raised ConnectionError is not catch by BrokenPipeError,ConnectionResetError
				else :
					buffer+=data
					size -= len(data)
			laps=time.perf_counter()-start_time#to measure time intervals
			client_stats[TIME_STAT_INDEX]+=laps
		except (socket.timeout,ConnectionResetError,BrokenPipeError) as err :
			### connection with client is lost
			### socket.timeout means that the deadline for sending data has been exceeded
			### BrokenPipeError=EPIPE and ESHUTDOWN means connection was closed with no data left unread in the socket buffer.
			### ConnectionResetError=ECONNRESET  means connection closed while still there unhandled data in the socket buffer.
			print("recv data fail: ",err)
			client_stats[FAIL_STAT_INDEX]+=1
			client[CONNECTION_INDEX]=None
			return b''
		except (BlockingIOError,ConnectionError) as err :# ConnectionError catch raised BrokenPipeError,ConnectionResetError
			### no data at this time and dont want to wait for it
			#print("recv dont wait: ",err)
			return b''
		else:
			client_stats[DONE_STAT_INDEX]+=1
			return buffer
				
	def stop(self,address):
		"""stop the connexion properly with client"""
		###  to close the connection in a timely fashion, call shutdown() before close().
		self.clients[address][CONNECTION_INDEX].shutdown(socket.SHUT_RDWR) #further sends and receive are disallowed
	def close(self,address):
		"""close the connexion with client"""
		self.clients[address][CONNECTION_INDEX].close()
		#del self.clients[address]
		
		
	def get_stats(self,address):
		"""returns quality stats history concerning the specified client"""
		client_stats= self.clients[address][STATS_INDEX]
		stats={'sending':{},'receiving':{}}
		
		send_stats=client_stats[SEND_STAT_INDEX]
		stats['sending']['times']=send_stats[TIME_STAT_INDEX]
		stats['sending']['success']=send_stats[DONE_STAT_INDEX]
		stats['sending']['fails']=send_stats[FAIL_STAT_INDEX]
		
		recv_stats=client_stats[RECV_STAT_INDEX]
		stats['receiving']['times']=recv_stats[TIME_STAT_INDEX]
		stats['receiving']['success']=recv_stats[DONE_STAT_INDEX]
		stats['receiving']['fails']=recv_stats[FAIL_STAT_INDEX]

		return stats
	
