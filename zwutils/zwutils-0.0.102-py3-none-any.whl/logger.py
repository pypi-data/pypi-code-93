import os
import json
import logging
import logging.config
from pathlib import Path
from logging.handlers import RotatingFileHandler

LEVEL = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'WARN': logging.WARN,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET
}
def logger(name=__name__, cfg=None, filesuffix=None):
    '''Get logger with name'''
    cfg = cfg  or 'conf/log.json'
    is_init = logging.getLogger().hasHandlers()
    if not is_init:
        if os.path.exists(cfg):
            with open(cfg, 'r') as f:
                config = json.load(f)
                handlers = config['handlers']
                # create parent dir if needed
                for h,o in handlers.items():
                    if 'filename' in o and not Path(o['filename']).parent.exists():
                        Path(o['filename']).parent.mkdir(parents=True, exist_ok=True)
                # add filename suffix is needed
                if filesuffix and handlers['logfile']:
                    logpath = Path(handlers['logfile']['filename'])
                    logpath = logpath.parent / ('%s_%s%s'%(logpath.stem, filesuffix, logpath.suffix))
                    handlers['logfile']['filename'] = str(logpath)
                logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name)
    return logger

def cologger(name=__name__, procname=None, cfg=None, filesuffix=None):
    cfg = cfg  or 'conf/log.json'
    log = logger(name, cfg, filesuffix)
    log.propagate = False
    procname = procname or ''
    if os.path.exists(cfg):
        with open(cfg, 'r') as f:
            config = json.load(f)
        handlers = config['handlers']
        formaters = config['formatters']
        logfile = handlers['logfile']
        if logfile:
            maxBytes = logfile['maxBytes']
            backupCount = logfile['backupCount']
            encoding = logfile['encoding']
            level = LEVEL[logfile['level']]

            logpath = Path(logfile['filename'])
            logname = '%s_%s_%s%s'%(logpath.stem, procname, filesuffix, logpath.suffix) if filesuffix \
                else '%s_%s%s'%(logpath.stem, procname, logpath.suffix)
            logpath = logpath.parent / logname

            if all( str(Path(o.baseFilename).resolve()) != str(logpath.resolve()) for o in log.handlers):
                formatter = formaters[logfile['formatter']]['format']
                formatter = logging.Formatter(formatter)
                handler = RotatingFileHandler(filename=logpath, maxBytes=maxBytes, backupCount=backupCount, encoding=encoding)
                handler.setLevel(level)
                handler.setFormatter(formatter)
                log.addHandler(handler)
                log.setLevel(level)
    return log
