from ..db.mysql_pool import mysql_fetch_data


def get_unit_price(tariff_db_config, **kwargs):
    """
    :param tariff_db_config: 电价表数据库
    :kwargs
        :param province_code: 省份代码，身份证号前六位
        :param tou: 分时/未分时
        :param is_single: 单一制/两部制
        :param elec_type: 电价类型
        :param p_level: 电压等级
        :param season_code: 季节代码
        :param basic_type: 基本电费类型
        :param basic_type_cn: 基本电费类型（中文）
        :param oa_prize_type: OA电价码
    """
    unit_price = mysql_fetch_data(tariff_db_config, "SELECT * FROM `faladi`.code_tariff")
    for arg in kwargs:
        unit_price = unit_price.loc[(unit_price[arg] == kwargs[arg])]

    if unit_price.shape[0] == 1:
        return unit_price.to_dict(orient="records")[0]
    else:
        raise IndexError("CANNOT MATCH UNIQUE TARIFF RECORD!")
