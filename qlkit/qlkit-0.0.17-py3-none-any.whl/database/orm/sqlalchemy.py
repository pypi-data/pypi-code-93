#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64
import typing as t
from collections import Iterable
from ..transaction import Transaction, TransactionFactory
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, Query
from sqlalchemy import create_engine, desc
from sqlalchemy.future import create_engine as f_create_engine
from sqlalchemy.engine import URL


class SessionFactory(TransactionFactory):

    def __init__(self, sqlalchemy_session_class: sessionmaker, engine):
        self.session_class = sqlalchemy_session_class
        self.engine = engine
        self.scoped_session = scoped_session(self.session_class)

    def get_transaction(self) -> Transaction:
        """获取一个绑定到ThreadLocal的session"""
        return self.scoped_session()

    def remove(self):
        """从ThreadLocal移除session"""
        self.scoped_session.remove()


class BaseQuery(Query):

    def _encode_page_token(self, cursor: int) -> str:
        cursor_byte = str(cursor).encode()
        token = base64.b64encode(cursor_byte)
        return token.decode()

    def _decode_page_token(self, page_token: str) -> int:
        if page_token:
            offset = base64.b64decode(page_token)
            cursor = int(offset.decode())
        else:
            cursor = 0
        return cursor

    def paginate_with_cursor(self, page_token, page_size, cursor_field) -> \
            t.Tuple[list, str]:
        cursor = self._decode_page_token(page_token)
        if cursor == 1:
            # 最后一个元素
            page = self.filter(cursor_field == cursor).all()
        elif cursor == 0:
            # 第一页
            page = self.filter(cursor_field >= cursor).order_by(
                desc(cursor_field)
            ).limit(page_size + 1).all()
        else:
            page = self.filter(cursor_field <= cursor).order_by(
                desc(cursor_field)
            ).limit(page_size + 1).all()    # limit 需要多拿一个元素，以判断是否还有下一页

        if not page:
            return [], ""

        if len(page) > page_size:
            # 有下一页
            last_row = page.pop(-1)
            if isinstance(last_row, Iterable):
                for r in last_row:
                    # 多表联合查询，需要依据cursor_field找到游标的表
                    if r.__class__ == cursor_field.class_:
                        next_cursor = getattr(r, cursor_field.key)
                        next_page_token = self._encode_page_token(next_cursor)
                        return page, next_page_token
                raise Exception("Found cursor failed")
            else:
                next_cursor = getattr(last_row, cursor_field.key)
                next_page_token = self._encode_page_token(next_cursor)
                return page, next_page_token
        else:
            return page, ""


def create_session_factory(engine_url: URL, engine_options: dict = None,
                           session_options: dict = None) -> TransactionFactory:
    """
    create sqlalchemy sessionmaker.
    https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine
    :return: sessionmaker
    """

    if engine_options:
        if engine_options.get("future", False):
            engine = f_create_engine(engine_url, **engine_options)
        else:
            engine = create_engine(engine_url, **engine_options)
    else:
        engine = create_engine(engine_url)

    if session_options:
        sqlalchemy_session_class = sessionmaker(**session_options)
    else:
        sqlalchemy_session_class = sessionmaker(**session_options)
    sqlalchemy_session_class.configure(bind=engine, query_cls=BaseQuery)
    return SessionFactory(sqlalchemy_session_class, engine)


def create_model():
    """model should bind with process"""
    return declarative_base()
