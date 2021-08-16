#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
from munch import Munch


class InnerFdCode(object):

    def __init__(self, site: str, project: str, code: str):
        self.site = site
        self.project = project
        self.code = code

    def __hash__(self):
        result = 1
        result = 31 * result + (hash(self.site) if self.site is not None else 0)
        result = 31 * result + (hash(self.project) if self.project is not None else 0)
        result = 31 * result + (hash(self.code) if self.code is not None else 0)
        return result

    def source_name(self):
        return f"fd_{self.site}_{self.project}_{self.code}"

    def __eq__(self, other):
        return self.site == other.site and self.project == other.project and self.code == other.code


class InnerCrawl(InnerFdCode):

    def __init__(self, site: str, project: str, code: str, type: str, connection: str, credentials: str):
        super().__init__(site, project, code)
        self.connection = connection
        self.type = type
        self.credentials = credentials

    def source_name(self):
        return f"crawl_{self.site}_{self.project}_{self.code}"


def fold_ref_fds(factDatasource, result: list = None) -> list:
    """
    把Ref的FactDatasource平面的展开
    :param result:
    :param factDatasource:
    :return:
    """
    if result is None:
        result = list()

    result.append(factDatasource)
    if "ref" in factDatasource and len(factDatasource["ref"]) != 0:
        fold_ref_fds(Munch(factDatasource.ref), result)

    return result
