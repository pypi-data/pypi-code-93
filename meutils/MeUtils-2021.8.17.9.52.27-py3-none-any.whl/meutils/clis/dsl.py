#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : dsl
# @Time         : 2021/2/1 6:02 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :


from meutils.pipe import *

os.environ['HADOOP_HOME'] = '/home/work/tools/infra-client/bin'
from meutils.cmds import HDFS

parser = argparse.ArgumentParser(description='DSL')
parser.add_argument('--conf', default='/mipush/dsl/push_mitv/auto_debug.conf', help='zk/yaml')
parser.add_argument('--push2hdfs', default='', help='push hdfs')  # .so + .tar + .conf

args = parser.parse_args()

logger.info(f'cli args: {args.__dict__}')


class Config(BaseConfig):
    dsl_home = '/home/work/yuanjie'
    data = '/user/s_feeds/yuanjie/dsl/debug_sfile'
    biz = 'push_mitv'
    biz_conf_dir = f'{dsl_home}/dsl3/conf/{biz}'
    features = 'age,sex'
    repo_dsl = ''
    repo_build_index = ''

    debug = f"{dsl_home}/dsl3/build/debug"
    libfeature = f"{dsl_home}/dsl3/libfeature.so"
    feature_group_conf = f'{dsl_home}/dsl3/conf/feature_group.conf'


conf = Config.parse_yaml(args.conf) if Path(args.conf).is_file() else Config.parse_zk(args.conf)

# feature_group_conf
columns = ['fea_id', 'fea_name', 'component', 'fea_type', 'fea_dim', 'isOut', 'dnn_group']
df = pd.read_csv(conf.feature_group_conf, sep='\s+', names=columns, comment='#')
logger.info(f'df_feature_group_conf.shape: {df.shape}')
logger.info(f'df_feature_group_conf.max(): {df.max()}')

# git_pull
git_pull(conf.repo_dsl)
git_pull(conf.repo_build_index)

# build
magic_cmd(f"cd {conf.dsl_home}/dsl3 && sh {conf.dsl_home}/dsl3/release.sh")
magic_cmd(f"cd {conf.dsl_home}/build-index && mvn package")

magic_cmd(f"cd {conf.dsl_home}/dsl3/conf && tar -cvf {conf.dsl_home}/{conf.biz}.tar {conf.biz}/")  # {biz}.tar

# data => bin_data
debug_dir = f"{conf.dsl_home}/{conf.biz}_dsl_debug"

# Path(debug_dir).mkdir(parents=True, exist_ok=True)
magic_cmd(f'mkdir {debug_dir}')
if HDFS.check_path_isexist(f'{conf.data}/part-00000'):
    HDFS.magic_cmd(f'-get -f {conf.data}/part-00000 {debug_dir}/data.sfile')

_ = magic_cmd(f"cd {debug_dir} && {conf.dsl_home}/build-index/script/run.sh --impression data.sfile && ls")
print(_)

# debug.conf
debug_conf = f"""
--dsl_conf={conf.biz_conf_dir}
--feature_group={conf.feature_group_conf}
--data_dir={debug_dir}
--trace_id=
--item_id=
--features={conf.features}
""".strip()

with open(f'{debug_dir}/debug.conf', 'w') as f:
    f.write(debug_conf)

print(magic_cmd(f'{conf.debug} {debug_dir}/debug.conf'))


def main():
    pass


if __name__ == '__main__':
    main()
