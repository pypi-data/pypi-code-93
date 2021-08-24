# -*- coding: utf-8 -*-

from hagworm.frame.fastapi.base import APIRouter

from controller import home


router = APIRouter(prefix=r'/demo')

router.include_router(home.router)
