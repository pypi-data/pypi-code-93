# coding: utf-8
from __future__ import unicode_literals, absolute_import

import datetime

from fias.importer.client import client
from fias.importer.signals import pre_fetch_version, post_fetch_version
from fias.models import Version


def get_or_create_version(version_id, version_text):
    dumpdate = datetime.datetime.strptime(version_text[-10:], "%d.%m.%Y").date()
    version = Version.objects.filter(
        ver=version_id,
    ).first()

    if version:
        ver = version

        if version.dumpdate < dumpdate:
            version.dumpdate = dumpdate
            version.save()
            created = True
        else:
            created = False
    else:
        ver = Version.objects.create(
            ver=version_id,
            dumpdate=dumpdate,
        )
        created = True

    return ver, created


def parse_item_as_dict(item, update_all=False):
    """
    Разбор данных о версии как словаря
    """
    ver, created = get_or_create_version(item['VersionId'], item['TextVersion'])

    if created or update_all:
        setattr(ver, 'complete_xml_url', item['FiasCompleteXmlUrl'] or '')
        setattr(ver, 'complete_dbf_url', item['FiasCompleteDbfUrl'] or '')
        setattr(ver, 'delta_xml_url', item.get('FiasDeltaXmlUrl', ''))
        setattr(ver, 'delta_dbf_url', item.get('FiasDeltaXmlUrl', ''))

        ver.save()


def fetch_version_info(update_all=False):

    pre_fetch_version.send(object.__class__)

    versions = client.get_all_download_file_info()
    for item in versions:
        parse_item_as_dict(item=item, update_all=update_all)

    post_fetch_version.send(object.__class__)
