# -*- coding: utf-8 -*-

from phcli.ph_errs.ph_err import PhException
from phcli.ph_data_clean.clean.cpa_gyc_data_clean import CpaGycDataClean
from phcli.ph_data_clean.clean.chc_data_clean import ChcDataClean
from phcli.ph_data_clean.clean.product_data_clean import ProductDataClean
from phcli.ph_data_clean.clean.universe_data_clean import UniverseDataClean


class CleanerFactory(object):
    """
    清洗算法的生成工厂
    """

    all_clean = {
        ('CPA', 'GYC', 'CPA&GYC', 'GYC&CPA', 'CPA&PTI&DDD&HH'): CpaGycDataClean,
        ('CHC',): ChcDataClean,
        ('universe',): UniverseDataClean,
        ('product',): ProductDataClean,
    }

    def get_specific_cleaner(self, source, company=''):
        """
        根据源和公司获取特定的清洗算法

        :param source: 清洗的元数据类型
        :param company: 清洗的公司名称

        :return: [DataClean] 特定清洗算法


        """

        finded = [clean for clean in self.all_clean.items()
                  if source.lower() in [item.lower() for item in clean[0]]]

        if len(finded) == 1:
            return finded[0][1]()
        elif len(finded) > 1:
            raise PhException("Find more Cleaner" + str(finded))
        else:
            raise PhException("Not find Cleaner, source=%s, company=%s" % (source, company))

