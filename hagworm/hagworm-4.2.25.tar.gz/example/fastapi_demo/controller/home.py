# -*- coding: utf-8 -*-

from service.base import DataSource

from hagworm.frame.fastapi.base import APIRouter, Request
from hagworm.frame.fastapi.response import ErrorResponse


router = APIRouter()


@router.get(r'/')
async def default(request: Request):

    return request.client_ip


@router.get(r'/error')
async def error(request: Request):

    raise ErrorResponse(-1, request.client_ip, 400)


@router.get(r'/health')
async def health():

    return await DataSource().health()
