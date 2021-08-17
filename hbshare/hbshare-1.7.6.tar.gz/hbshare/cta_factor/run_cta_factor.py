from hbshare.cta_factor.hsjy_to_local import (
    hsjy_fut_pro_info,
    hsjy_fut_wr,
    hsjy_fut_com_info,
    hsjy_fut_com,
    hsjy_fut_member,
)
from hbshare.cta_factor.hsjy_func import hsjy_fut_index
from hbshare.cta_factor.factor_index import run
from hbshare.cta_factor.factor_func import index_gen

hsjy_fut_pro_info()
hsjy_fut_wr()
hsjy_fut_com_info()
hsjy_fut_com()
hsjy_fut_member()
hsjy_fut_index()
run()
index_gen()
