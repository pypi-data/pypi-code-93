import sys, logging, time
from datetime import datetime

LOG_FORMAT = '\
%(name)s  %(levelname)s - %(asctime)s - %(product)s:%(client)s:%(instance)s:%(service)s:%(process)s - \
%(label)s - %(label2)s - %(duration).3f - %(message)s'

def parse_msg(d, level=0):
    if d is None: return 'null'
    if type(d) in [int, float]: return str(d)
    if isinstance(d, str): return d.replace("\n", " ")
    if isinstance(d, datetime): return d.strftime("%Y-%m-%Y %H:%M:%S")
    if type(d) is list: return f'[#{len(d)}]: [' + ', '.join(f'{v}' for v in d[:10]) + ']'
    if type(d) is not dict: return f'OBJECT-{type(d)}'
    s = '{'
    for key, val in d.items():
        if isinstance(d[key], dict):
            s += f'{key}={parse_msg(d[key],level+1)[:-1]}'
            continue
        if type(d[key]) is list:
            s += f'{key}[#{len(d[key])}]: '
            s += '[' + ', '.join(f'{v}' for v in d[key][:10]) + ']'
        else:
            s += f'{key}={val}'
        s += ','
    s = s[:-1]+'}, '
    if level==0 and s[-1]==' ': s=s[:-2]
    return s

class AppLog():
    def __init__(self, cfg=None, product='_PRODUCT_', client='_CLIENT_', instance='_INSTANCE_', service='_SERVICE_'):
        log_format = logging.Formatter(LOG_FORMAT)
        logger = logging.getLogger('APPLOG')
        self.logger = logger
        handler = logging.StreamHandler()
        # handler.flush = sys.stdout.flush
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(log_format)
        self.handler = handler
        self.LOG_LEVELS = {
            1: logger.debug,
            2: logger.info,
            3: logger.warning,
            4: logger.error,
            5: logger.critical
        }
        self.msg_prefix = {}
        self.msg_prefix['service'] = service
        if cfg is not None:
            try:
                self.msg_prefix['product']  = cfg['app']['product']
                self.msg_prefix['client'] = cfg['app']['client']
                self.msg_prefix['instance'] = cfg['app']['instance']
                return
            except Exception as e:
                pass
        self.msg_prefix['product'] = product
        self.msg_prefix['client'] = client
        self.msg_prefix['instance'] = instance
                    
    def setup(self):
        for key in logging.Logger.manager.loggerDict:
            logging.getLogger(key).setLevel(logging.CRITICAL)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

            
    def log(self, level, ts0=0, label=None, label2=None, msg=''):
        if not isinstance(level, int) or level<1 or level>5: return
        log_f = self.LOG_LEVELS[level]
        log_msg = self.msg_prefix
        log_msg['label'] = label
        log_msg['label2'] = label2
        log_msg['duration'] = ts0
        s = parse_msg(msg)
        log_f(s, extra=log_msg)