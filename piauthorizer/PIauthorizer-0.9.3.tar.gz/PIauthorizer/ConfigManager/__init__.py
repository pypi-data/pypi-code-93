import logging
import logging.config
import os
from typing import Callable

from fastapi import APIRouter, Depends

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'logging/logging.conf')
logging.config.fileConfig(filename, disable_existing_loggers=False)
numba_logger = logging.getLogger('numba')
numba_logger.setLevel(logging.WARNING)
urllib_logger = logging.getLogger('urllib3')
urllib_logger.setLevel(logging.WARNING)

from .ConfigManager import *


def get_config_router(config_keys:list=[]) -> Callable:
    config_manager = ConfigManager()
    config_router = APIRouter()

    @config_router.get("/configuration", tags=["Configurations"])
    def get_config(token_info=Depends(config_manager.get_current_user)):
        return token_info.tenant_config
    
    return config_router

async def override():
    return True


