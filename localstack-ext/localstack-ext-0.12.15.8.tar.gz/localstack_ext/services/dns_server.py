import logging
egvJc=int
egvJW=object
egvJF=isinstance
egvJI=len
egvJT=dict
egvJK=None
egvJN=property
egvJt=super
egvJa=Exception
egvJY=False
egvJM=bytes
egvJi=getattr
egvJu=str
egvJd=True
egvJp=next
egvJf=StopIteration
import os
import re
import sys
import threading
import traceback
from datetime import datetime
import dns.flags
import dns.message
import dns.query
from dnslib import(AAAA,CNAME,MX,NS,QTYPE,RCODE,RD,RR,SOA,TXT,A,DNSHeader,DNSLabel,DNSQuestion,DNSRecord)
from dnslib.server import DNSHandler,DNSServer
from localstack.constants import LOCALHOST_HOSTNAME
from localstack.utils.common import in_docker,is_root,load_file,run,to_bytes,to_str
from localstack_ext import config as config_ext
from localstack_ext.bootstrap.local_daemon import create_network_interface_alias
EPOCH=datetime(1970,1,1)
SERIAL=egvJc((datetime.utcnow()-EPOCH).total_seconds())
DEFAULT_DNS_SERVER="8.8.8.8"
RCODE_REFUSED=5
SERVERS=[]
DNS_PORT=53
REQUEST_TIMEOUT_SECS=7
TYPE_LOOKUP={A:QTYPE.A,AAAA:QTYPE.AAAA,CNAME:QTYPE.CNAME,MX:QTYPE.MX,NS:QTYPE.NS,SOA:QTYPE.SOA,TXT:QTYPE.TXT}
LOG=logging.getLogger(__name__)
MAC_INTERFACE="en0"
THREAD_LOCAL=threading.local()
class Record(egvJW):
 def __init__(self,rdata_type,*args,**kwargs):
  rtype=kwargs.get("rtype")
  rname=kwargs.get("rname")
  ttl=kwargs.get("ttl")
  if egvJF(rdata_type,RD):
   self._rtype=TYPE_LOOKUP[rdata_type.__class__]
   rdata=rdata_type
  else:
   self._rtype=TYPE_LOOKUP[rdata_type]
   if rdata_type==SOA and egvJI(args)==2:
    args+=((SERIAL,60*60*1,60*60*3,60*60*24,60*60*1))
   rdata=rdata_type(*args)
  if rtype:
   self._rtype=rtype
  self._rname=rname
  self.kwargs=egvJT(rdata=rdata,ttl=self.sensible_ttl()if ttl is egvJK else ttl,**kwargs)
 def try_rr(self,q):
  if q.qtype==QTYPE.ANY or q.qtype==self._rtype:
   return self.as_rr(q.qname)
 def as_rr(self,alt_rname):
  return RR(rname=self._rname or alt_rname,rtype=self._rtype,**self.kwargs)
 def sensible_ttl(self):
  if self._rtype in(QTYPE.NS,QTYPE.SOA):
   return 60*60*24
  else:
   return 300
 @egvJN
 def is_soa(self):
  return self._rtype==QTYPE.SOA
 def __str__(self):
  return "{} {}".format(QTYPE[self._rtype],self.kwargs)
class NonLoggingHandler(DNSHandler):
 def handle(self,*args,**kwargs):
  try:
   THREAD_LOCAL.client_address=self.client_address
   THREAD_LOCAL.server=self.server
   THREAD_LOCAL.request=self.request
   return egvJt(NonLoggingHandler,self).handle(*args,**kwargs)
  except egvJa:
   pass
def get_host_list():
 result=DEFAULT_HOSTS_LIST
 if config_ext.DNS_RESOLVE_IP!=config_ext.LOCALHOST_IP:
  result=[Record(A,config_ext.DNS_RESOLVE_IP),Record(CNAME,"localhost")]
 return result
DEFAULT_HOSTS_LIST=[Record(A,config_ext.LOCALHOST_IP),Record(CNAME,"localhost")]
SKIP_PATTERNS=[r".*(forums|console|docs|clientvpn|boto3|(signin(\-reg)?))\.([^\.]+\.)?(aws\.amazon|amazonaws)\.com",r".*captcha-prod\.s3\.amazonaws\.com",r"^aws\.amazon\.com",r"^github-production-release-.*\.s3\.amazonaws\.com",r"^aws-glue-etl-artifacts\.s3\.amazonaws\.com"]
ZONES={".*.amazonaws.com":get_host_list,".*aws.amazon.com":get_host_list,".*cloudfront.net":get_host_list,".*%s"%LOCALHOST_HOSTNAME:get_host_list}
def get_zones_map():
 result={DNSLabel(to_bytes(key)):func()for key,func in ZONES.items()}
 return result
class NoopLogger(egvJW):
 def __init__(self,*args,**kwargs):
  pass
 def log_pass(self,*args,**kwargs):
  pass
 def log_prefix(self,*args,**kwargs):
  pass
 def log_recv(self,*args,**kwargs):
  pass
 def log_send(self,*args,**kwargs):
  pass
 def log_request(self,*args,**kwargs):
  pass
 def log_reply(self,*args,**kwargs):
  pass
 def log_truncated(self,*args,**kwargs):
  pass
 def log_error(self,*args,**kwargs):
  pass
 def log_data(self,*args,**kwargs):
  pass
class Resolver:
 def resolve(self,request,handler):
  reply=request.reply()
  found=egvJY
  try:
   if not self.should_skip(request):
    found=self.resolve_zones(request,reply)
  except egvJa as e:
   LOG.info("Unable to get DNS result: %s"%(e))
  dns_server=get_fallback_dns_server()
  if not found and dns_server:
   req_parsed=egvJK
   try:
    req_parsed=dns.message.from_wire(egvJM(request.pack()))
    r=dns.query.udp(req_parsed,dns_server,timeout=REQUEST_TIMEOUT_SECS)
    result=self.map_response_dnspython_to_dnslib(r)
    return result
   except egvJa as e:
    if egvJi(req_parsed,"question",egvJK):
     q_name=req_parsed.question[0].name
     result=dns.resolver.query(q_name)
     if result and result.response.answer:
      result=self.map_response_dnspython_to_dnslib(result.response)
      return result
    LOG.info("Unable to get DNS result from fallback server %s: %s"%(dns_server,e))
  if not reply.rr:
   reply.header.set_rcode(RCODE.SERVFAIL)
   return egvJK
  return reply
 def should_skip(self,request):
  request_name=to_str(egvJu(request.q.qname))
  for p in SKIP_PATTERNS:
   if re.match(p,request_name):
    return egvJd
  if config_ext.DNS_LOCAL_NAME_PATTERNS:
   for pattern in re.split(r"[,;\s]+",config_ext.DNS_LOCAL_NAME_PATTERNS):
    if re.match(pattern,request_name):
     return egvJY
   return egvJd
 def resolve_zones(self,request,reply):
  zones=get_zones_map()
  zone=zones.get(request.q.qname)
  found=egvJY
  if zone is not egvJK:
   for zone_records in zone:
    rr=zone_records.try_rr(request.q)
    if rr:
     found=egvJd
     reply.add_answer(rr)
  else:
   for zone_label,zone_records in zones.items():
    if re.match(egvJu(zone_label),egvJu(request.q.qname)):
     for record in zone_records:
      rr=record.try_rr(request.q)
      if rr:
       found=egvJd
       reply.add_answer(rr)
    elif request.q.qname.matchSuffix(zone_label):
     try:
      soa_record=egvJp(r for r in zone_records if r.is_soa)
     except egvJf:
      continue
     else:
      found=egvJd
      reply.add_answer(soa_record.as_rr(zone_label))
      break
  return found
 def map_response_dnspython_to_dnslib(self,response):
  flags=dns.flags.to_text(response.flags)
  def flag(f):
   return 1 if f.upper()in flags else 0
  questions=[]
  for q in response.question:
   questions.append(DNSQuestion(qname=egvJu(q.name),qtype=q.rdtype,qclass=q.rdclass))
  result=DNSRecord(DNSHeader(qr=flag("qr"),aa=flag("aa"),ra=flag("ra"),id=response.id),q=questions[0])
  parts=egvJu(response).split(";ANSWER")
  for line in parts[1].split("\n"):
   line=line.strip()
   if line and not line.startswith(";"):
    result.add_answer(*RR.fromZone(line))
  return result
def add_resolv_entry():
 from localstack.services.edge import ensure_can_use_sudo
 resolv_conf="/etc/resolv.conf"
 if os.path.exists(resolv_conf):
  content=load_file(resolv_conf)
  comment="# The following line is required by LocalStack"
  line="nameserver %s"%config_ext.DNS_ADDRESS
  if line not in content:
   sudo_cmd="" if is_root()else "sudo"
   ensure_can_use_sudo()
   for new_line in("",line,comment):
    run(('''%s python -c "import sys; f=open(sys.argv[1]).read(); open(sys.argv[1], 'w').write('%s\\n' + f)\" %s''')%(sudo_cmd,new_line,resolv_conf))
def get_fallback_dns_server():
 return config_ext.DNS_SERVER or DEFAULT_DNS_SERVER
def setup_network_configuration():
 if not config_ext.use_custom_dns():
  return
 create_network_interfaces()
 if config_ext.DNS_ADDRESS!="0.0.0.0" or in_docker():
  add_resolv_entry()
def create_network_interfaces():
 if in_docker():
  config_ext.DNS_ADDRESS="0.0.0.0"
  return
 try:
  run("ifconfig | grep {addr}".format(addr=config_ext.DNS_ADDRESS),print_error=egvJY)
  return
 except egvJa:
  pass
 from localstack.services.edge import ensure_can_use_sudo
 ensure_can_use_sudo()
 try:
  create_network_interface_alias(config_ext.DNS_ADDRESS,interface=MAC_INTERFACE)
 except egvJa:
  config_ext.DNS_ADDRESS="0.0.0.0"
def start_servers():
 global SERVERS
 if SERVERS:
  return
 if not config_ext.use_custom_dns():
  return
 try:
  print("Starting DNS servers (tcp/udp port %s on %s)..."%(DNS_PORT,config_ext.DNS_ADDRESS))
  resolver=Resolver()
  nlh=NonLoggingHandler
  SERVERS=[DNSServer(resolver,handler=nlh,logger=NoopLogger(),port=DNS_PORT,address=config_ext.DNS_ADDRESS,tcp=egvJY),DNSServer(resolver,handler=nlh,logger=NoopLogger(),port=DNS_PORT,address=config_ext.DNS_ADDRESS,tcp=egvJd)]
  for s in SERVERS:
   s.start_thread()
 except egvJa as e:
  print("WARN: Unable to start DNS server: %s %s"%(e,traceback.format_exc()))
  sys.stdout.flush()
def stop_servers():
 for s in SERVERS:
  s.stop()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
