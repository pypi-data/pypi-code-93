from datetime import datetime
import json
import uuid
import asyncio
import pika
from aio_pika import connect, connect_robust, Message, DeliveryMode, ExchangeType
from dl2050utils.env import Config_load
from dl2050utils.log import AppLog

# https://www.rabbitmq.com
# https://aio-pika.readthedocs.io/en/latest/index.html

JOB_CREATE = 0
JOB_START = 1
JOB_DONE = 2
JOB_NOTIFY = 3
JOB_DELIVER = 4
JOB_ERROR = 99

class MQ_SYNC():
    def __init__(self, log, db, qs, user='admin', passwd='password'):
        self.LOG, self.db, self.qs, self.user, self.passwd = log, db, qs, user, passwd
        
    def connect(self):
        try:
            mq_cred = pika.PlainCredentials(self.user, self.passwd)
            mq_conn = pika.BlockingConnection(pika.ConnectionParameters('mq', 5672, '/', mq_cred))
            self.ch = mq_conn.channel()
            for q in self.qs: self.ch.queue_declare(queue=q, durable=True, auto_delete=False)
        except Exception as e:
            self.LOG.log(4, 0, label='MQ', label2='startup', msg=str(e))
            return True
        self.LOG.log(2, 0, label='MQ', label2='startup', msg='CONNECTED')
        return False

    def startup(self): return self.connect()
    
    def server(self, queue, cb):
        if self.connect(): return True
        self.ch.basic_consume(queue=queue, auto_ack=False, on_message_callback=cb)
        self.ch.start_consuming()
        
    def publish(self, qname, uid, payload):
        job = {'uid': uid, 'payload': payload, 'jstatus': JOB_CREATE, 'eta': 0, 'ts_create': datetime.now()}
        jid = asyncio.run(self.db.insert('jobs', job, return_key='jid'))
        if jid is None: return None
        try:
            payload['uid'], payload['jid'] = uid, jid
            msg = Message(body=json.dumps(payload).encode(), delivery_mode=DeliveryMode.PERSISTENT)
            self.ch.basic_publish(exchange='', routing_key=qname, body=payload, properties=pika.BasicProperties(delivery_mode=2)) 
        except Exception as e:
            self.LOG.log(4, 0, label='MQ', label2='publish', msg=str(e))
            return None
        return jid

    def job_update(self, jid, status=None, eta=None, result=None):
        job = {'jid': jid}
        if status is not None:
            job['jstatus']=status
            if status==JOB_START: job['ts_start']=datetime.now()
            if status==JOB_DONE: job['ts_done']=datetime.now()
        if eta is not None: job['eta']=eta
        if result is not None: job['result']=result
        self.LOG.log(1, 0, label='MQ', label2='job_update', msg=job)
        res = asyncio.run(self.db.update('jobs', 'jid', job))
        if res is None or res==0: return True
        return False
    def job_start(self, jid, eta=None): return self.job_update(jid, status=JOB_START, eta=eta)
    def job_update_eta(self, jid, eta): return self.job_update(jid, eta=eta)
    def job_done(self, jid): return self.job_update(jid, status=JOB_DONE)
    def job_notify(self, jid): return self.job_update(jid, status=JOB_NOTIFY)
    def job_deliver(self, jid): return self.job_update(jid, status=JOB_DELIVER)
    def job_result(self, jid, result): return self.job_update(jid, result=result)
    def job_error(self, jid): return self.job_update(jid, status=JOB_ERROR, eta=0)
    def get_jobs(self, uid, status=None): return self.db.select('jobs', {'uid':uid, 'jstatus':status})
    def get_job(self, jid): return self.db.select_one('jobs', {'jid':jid})


class MQ():
    def __init__(self, log, db, qnames, user='admin', passwd='password'):
        self.LOG, self.db, self.qnames = log, db, qnames
        self.url = f'amqp://{user}:{passwd}@mq:5672/'
        # self.loop = asyncio.get_event_loop()
        # self.futures = {}
        
    async def connect(self):
        try:
            self.con = await connect_robust(self.url)
            self.ch = await self.con.channel()
            for qname in self.qnames: await self.ch.declare_queue(qname, durable=True, auto_delete=False)
        except Exception as e:
            self.LOG.log(4, 0, label='MQ', label2='connect', msg=str(e))
            return True
        self.LOG.log(2, 0, label='MQ', label2='connect', msg='CONNECTED')
        return False

    async def startup(self): return await self.connect()
    
    async def server(self, qname, cb):
        if await self.connect(): exit(1)
        queue = await self.ch.declare_queue(qname, durable=True, auto_delete=False)
        await queue.consume(cb, no_ack=False)
    
    async def publish(self, qname, uid, payload):
        job = {'uid': uid, 'payload': payload, 'jstatus': JOB_CREATE, 'eta': 0, 'ts_create': datetime.now()}
        jid = await self.db.insert('jobs', job, return_key='jid')
        if jid is None: return None
        try:
            payload['uid'], payload['jid'] = uid, jid
            msg = Message(body=json.dumps(payload).encode(), delivery_mode=DeliveryMode.PERSISTENT)
            await self.ch.default_exchange.publish(msg, routing_key=qname)
        except Exception as e:
            self.LOG.log(4, 0, label='MQ', label2='publish', msg=str(e))
            return None
        return jid
        
    async def job_update(self, jid, status=None, eta=None, result=None):
        job = {'jid': jid}
        if status is not None:
            job['jstatus']=status
            if status==JOB_START: job['ts_start']=datetime.now()
            if status==JOB_DONE: job['ts_done']=datetime.now()
        if eta is not None: job['eta']=eta
        if result is not None: job['result']=result
        self.LOG.log(1, 0, label='MQ', label2='job_update', msg=job)
        res = await self.db.update('jobs', 'jid', job)
        if res is None or res==0: return True
        return False
    async def job_start(self, jid, eta=None): return await self.job_update(jid, status=JOB_START, eta=eta)
    async def job_update_eta(self, jid, eta): return await self.job_update(jid, eta=eta)
    async def job_done(self, jid): return await self.job_update(jid, status=JOB_DONE)
    async def job_notify(self, jid): return await self.job_update(jid, status=JOB_NOTIFY)
    async def job_deliver(self, jid): return await self.job_update(jid, status=JOB_DELIVER)
    async def job_result(self, jid, result): return await self.job_update(jid, result=result)
    async def job_error(self, jid): return await self.job_update(jid, status=JOB_ERROR, eta=0)
    async def get_jobs(self, uid, status=None): return await self.db.select('jobs', {'uid':uid, 'jstatus':status})
    async def get_job(self, jid): return await self.db.select_one('jobs', {'jid':jid})
