# -*- coding: utf-8 -*-

from pypinyin import lazy_pinyin


class MappingFactory(object):
    """
    匹配规则的生成工厂
    """

    def get_specific_mapping(self, source, company):
        """
        根据源和公司获取特定的匹配规则

        :param source: 清洗的元数据类型
        :param company: 清洗的公司名称

        :return: [dict] 返回指定的匹配规则
        """
        source = source.replace("&", "_")
        company = "".join(lazy_pinyin(company))
        ipt_module = __import__('phcli.ph_data_clean.mapping.%s_%s' % (source.lower(), company.lower()))
        ph_data_clean_pkg = getattr(ipt_module, 'ph_data_clean')
        mapping_pkg = getattr(ph_data_clean_pkg, 'mapping')
        mapping_file = getattr(mapping_pkg, '%s_%s' % (source.lower(), company.lower()))
        mapping_table = getattr(mapping_file, 'mapping')
        return mapping_table()

