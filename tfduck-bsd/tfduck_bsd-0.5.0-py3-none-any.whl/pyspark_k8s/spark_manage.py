"""
auhtor: yuanxiao
datetime: 20210423
python3.8
pyspark 提交阿里云ask集群管理器
pip install kubernetes==12.0.1

新的tfduck容器需要将 /data/spark-3.1.1-bin-hadoop2.7 拷贝到 /mydata/spark-3.1.1-bin-hadoop2.7
"""
import json
from tfduck.common.defines import BMOBJ, Et
from tfduck.oss.oss import AliyunOss
try:
    from tfduck.pyspark_k8s.k8s_manage import K8sManage
except:
    from k8s_manage import K8sManage
from kubernetes import client, config
import uuid
import arrow
import time
import os
import base64
import subprocess


class SparkManage(object):
    """
    """

    def __init__(self, ctx, code_path, is_async=False, is_log=False,
                 s3_support=False, max_run_time=7200, task_params={},
                 spark_config={'task_name': 'default',
                               'driver_cores': '1',
                               'driver_memory': '1G',
                               'executor_instances': '1',
                               'executor_cores': '1',
                               'executor_memory': '1G',
                               'image_url': 'registry-intl-vpc.us-east-1.aliyuncs.com/talefun/pyspark247:1.0'
                               },
                 is_debug=False,
                 s3_params={}
                 ):
        """
        需要k8s的~/.kube/config文件
        需要/Users/yuanxiao/workspace/djcelery44/djcelery44/scripts/tools/spark_oss.conf文件
        需要/Users/yuanxiao/workspace/djcelery44/djcelery44/scripts/tools/spark_s3.conf文件
        生产环境路需要拷贝下
        """
        """
        校验
        """
        task_sub_name = spark_config.get('task_name', 'default')
        if task_sub_name is None:
            raise Et(2, "spark task name must not be none")
        task_sub_name = task_sub_name.strip()
        if task_sub_name == '':
            raise Et(2, "spark task name must not be '' ")
        if task_sub_name.find("-") != -1:
            raise Et(2, "spark task name not clude - char")
        """
        全局初始化
        """
        self.ctx = ctx
        self.is_debug = is_debug  # 如果为true，就在mac本地调试
        self.k8s_address = "https://47.253.49.211:6443"
        self.oss_bucket = "pyspark-data"
        if self.is_debug:  # mac本地测试环境
            self.spark_path = "/Users/yuanxiao/workspace/a_spark_study/spark-3.1.1-bin-hadoop2.7"
        else:  # 生产环境修改这个
            self.spark_path = "/mydata/spark-3.1.1-bin-hadoop2.7"
        self.log_timeout = 86400  # 接收日志最大
        self.max_run_time = max_run_time  # spark task最大运行时间
        self.code_path = code_path
        self.is_async = is_async
        self.is_log = is_log
        self.spark_config = spark_config
        self.s3_support = s3_support
        self.task_params = task_params  # 任务参数
        self.driver_pod_name = f"tfspark-{task_sub_name}-{self.max_run_time}-driver-{uuid.uuid1().hex}"
        """
        系统spark_oss的配置
        """
        # oss_config_file = "/opt/spark_oss.conf"
        if self.is_debug:  # mac本地测试环境
            oss_config_file = '/Users/yuanxiao/workspace/djcelery44/djcelery44/scripts/tools/spark_oss.conf'
        else:
            oss_config_file = '/opt/djcelery44/djcelery44/scripts/tools/spark_oss.conf'
        with open(oss_config_file, 'r') as f:
            oss_config = json.loads(f.read())
        self.oss_config = oss_config
        """
        系统spark_s3的配置
        """
        # oss_config_file = "/opt/spark_oss.conf"
        if self.is_debug:  # mac本地测试环境
            s3_config_file = '/Users/yuanxiao/workspace/djcelery44/djcelery44/scripts/tools/spark_s3.conf'
        else:
            s3_config_file = '/opt/djcelery44/djcelery44/scripts/tools/spark_s3.conf'
        with open(s3_config_file, 'r') as f:
            s3_config = json.loads(f.read())
        if s3_params: # 如果有传s3的配置，则用传入的s3配置
            s3_config = s3_params # {"bucket":"", "endpoint":"http://s3.us-west-2.amazonaws.com", "access_key":"", "secret_key":""}
        self.s3_config = s3_config
        """
        生成k8s客户端
        """
        self.k8s_client = K8sManage(ctx)

    def upload_code(self):
        """
        上传执行代码到spark_oss
        """
        now = arrow.utcnow()
        now_str = now.format("YYYY-MM-DD")
        oss_config = self.oss_config
        ctx = self.ctx
        uoss = AliyunOss(oss_config['bucket'], oss_config['access_key'],
                         oss_config['secret_key'], oss_config['endpoint'])
        local_file_path = BMOBJ.get_file_path(self.code_path)
        if not local_file_path.startswith("/"):
            local_file_path = f"/{local_file_path}"
        oss_file_path = f"code/{now_str}/{uuid.uuid1().hex}/"  # 注意必须斜杠结尾
        uoss.upload_oss(ctx, local_file_path, oss_file_path,
                        False, False, isrm=True, isdel=False)  # 递归查找, 不删除本地文件
        # uoss.download_oss(ctx, local_file_path+"xx", oss_file_path, isrm=True, isdel=False)  # 测试下载
        self.real_code_path = os.path.join("/oss_data", oss_file_path)

    def get_submit_spark_cmd(self):
        """
        构建spark执行命令---注意命令里面不能有回车--\后面不能有空格
        执行upload_code才能执行这个任务
        """
        """
        基础配置
        --name {task_sub_name}-{self.max_run_time} 修改为
        --conf spark.kubernetes.driver.pod.name={task_sub_name}-{self.max_run_time}
        认证配置---在./bin/spark-submit之前加环境变量KUBECONFIG即可,KUBECONFIG的值为k8s的认证文件
        """
        # 加入PYSPARK_PYTHON和PYSPARK_DRIVER_PYTHON环境变量，这两个环境变量会被外部python环境污染
        # 这两个需要传入容器内部的环境变量，其他环境变量传提交命令的机器的环境变量
        base_cmd = f"""KUBECONFIG=~/.kube/config \
PYSPARK_PYTHON=/usr/bin/python3 \
PYSPARK_DRIVER_PYTHON=/usr/bin/python3 \
./bin/spark-submit \
--master k8s://{self.k8s_address} \
--deploy-mode cluster \
--conf spark.kubernetes.driver.pod.name={self.driver_pod_name} \
--conf spark.executor.instances={self.spark_config.get('executor_instances', '1')} \
--conf spark.kubernetes.executor.deleteOnTermination=true \
--conf spark.kubernetes.submission.waitAppCompletion={'false' if self.is_async else 'true'} \
--conf spark.hadoop.fs.s3a.connection.ssl.enabled=false \
--conf spark.kubernetes.container.image={self.spark_config.get('image_url', 'registry-intl-vpc.us-east-1.aliyuncs.com/talefun/pyspark247:1.0')} \
--conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
--conf spark.kubernetes.driverEnv.PYSPARK_PYTHON=/usr/bin/python3 \
--conf spark.kubernetes.executorEnv.PYSPARK_PYTHON=/usr/bin/python3 \
--conf spark.kubernetes.pyspark.pythonVersion="3" \
--conf spark.driver.cores={self.spark_config.get('driver_cores', '1')} \
--conf spark.driver.memory={self.spark_config.get('driver_memory', '1G')} \
--conf spark.executor.cores={self.spark_config.get('executor_cores', '1')} \
--conf spark.executor.memory={self.spark_config.get('executor_memory', '1G')} \
"""
        """
        持久化配置
        """
        volum_cmd = """--conf spark.kubernetes.driver.volumes.persistentVolumeClaim.data.mount.path=/oss_data \
--conf spark.kubernetes.driver.volumes.persistentVolumeClaim.data.mount.readOnly=false \
--conf spark.kubernetes.driver.volumes.persistentVolumeClaim.data.options.claimName=spark-pvc \
--conf spark.kubernetes.executor.volumes.persistentVolumeClaim.data.mount.path=/oss_data \
--conf spark.kubernetes.executor.volumes.persistentVolumeClaim.data.mount.readOnly=false \
--conf spark.kubernetes.executor.volumes.persistentVolumeClaim.data.options.claimName=spark-pvc \
"""
        """
        s3 配置
        """
        s3_cmd = f"""--conf spark.hadoop.fs.s3a.endpoint={self.s3_config['bucket']} \
--conf spark.hadoop.fs.s3a.connection.ssl.enabled=false \
--conf spark.hadoop.fs.s3a.access.key={self.s3_config['access_key']} \
--conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
--conf spark.hadoop.fs.s3a.fast.upload=true \
--conf spark.hadoop.fs.s3a.path.style.access=true \
--conf spark.hadoop.fs.s3a.secret.key="{self.s3_config['secret_key']}" \
--conf spark.hadoop.fs.s3a.multipart.size=104857600 \
--conf com.amazonaws.services.s3a.enableV4=true \
    """
        """
        # 执行代码配置---执行main.py文件
        """
        param_b64_content = base64.b64encode(json.dumps(self.task_params).encode(
            'utf8')).decode()  # 将参数编辑为base64，防止出现特殊字符分割参数
        # 解码
        # ds = json.loads(base64.b64decode(param_b64_content).decode('utf8'))
        code_cmd = f"""local://{self.real_code_path}main.py {param_b64_content}
"""
        """
        拼接命令
        """
        submit_cmd = base_cmd+volum_cmd + \
            (s3_cmd if self.s3_support else "") + code_cmd
        return submit_cmd

    def submit_spark_task(self):
        """
        提交pyspark的任务
        """
        result = True
        ctx = self.ctx
        """
        执行任务
        """
        submit_cmd = self.get_submit_spark_cmd()
        # print(submit_cmd)
        if self.is_log:  # 管道输出日志的方式
            p = subprocess.Popen(submit_cmd,
                                 cwd=self.spark_path, universal_newlines=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        else:  # 不输出日志--不在std里面输出日志，因为日志太大了，通过k8s命令获取日志---目前先输出日志，后期边走边看
            with open(os.devnull, 'wb') as DEVNULL:  # 不在std里面输出日志，因为日志太大了，通过k8s命令获取日志
                # with open('./log.txt', 'wb') as DEVNULL: # 输出到文件

                p = subprocess.Popen(submit_cmd,
                                     cwd=self.spark_path, universal_newlines=True,
                                     stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL, shell=True)
        try:
            out, errout = None, None
            out, errout = p.communicate(timeout=self.log_timeout)
            # p.wait(timeout=self.log_timeout)
        except BaseException as e:
            try:
                p.kill()
            except:
                pass
            raise e
        if errout:
            # BMOBJ.log_error(f"errout----: {errout[:1024*100]}")
            # return_error_log = errout[:1024*100]
            BMOBJ.clog(ctx, f"errout----: {errout[:1024*10]}")
        if out:
            # return_out_log = errout[:1024*100]
            BMOBJ.clog(ctx, f"out----: {out[:1024*10]}")
        """
        判断任务是否完成---不从日志里面去判断，这样会拉回来很多日志
        """
        pod_obj = self.k8s_client.get_pod_info(self.driver_pod_name)
        if self.is_async:
            BMOBJ.clog(ctx, pod_obj.status.phase)
            if pod_obj.status.phase == "Pending":
                BMOBJ.clog(ctx, "task success runing")
            else:
                BMOBJ.clog(ctx, "task fail")
                result = False
        else:
            if pod_obj.status.phase == "Succeeded":
                BMOBJ.clog(ctx, "task success complated")
            else:
                BMOBJ.clog(ctx, "task fail-------------------error log:")
                error_log = self.k8s_client.get_pod_log(
                    self.driver_pod_name, 1000)
                BMOBJ.clog(ctx, error_log)
                result = False
        return result


if __name__ == "__main__":
    """
    由于我在提交的地方做了环境变量纠正，所以这里也不用再加了
    下面是纠正环境变量----现在不用了
    """
    # 因为executors.py在import的时候加载了以前的环境变量，污染了k8s需要提交的环境变量---需要设置为k8s容器内的path
    # "容器内path，没有被污染也可以不设置"
    # os.environ["PYSPARK_PYTHON"] = "/usr/bin/python332432423423"
    # # "容器内path，没有被污染也可以不设置"
    # os.environ["PYSPARK_DRIVER_PYTHON"] = "/usr/bin/python342342342342"

    if 1:  # 同步
        sm = SparkManage(
            ctx={},
            # code_path='/Users/yuanxiao/workspace/djcelery44/djcelery44/scripts/tools/debug/test_presto_s3',
            code_path='/Users/yuanxiao/workspace/djcelery44/djcelery44/scripts/tools/debug/test_hello',
            s3_support=False, is_async=False,
            spark_config={"task_name": "test"},
            task_params={'config': {'test': '哈哈',
                                    'a': '测试参数'}, 'config1': '测试'},
            is_log=True,  # 线上环境关闭日志
            is_debug=True)
        sm.upload_code()
        sm.submit_spark_task()
    else:  # 异步
        sm = SparkManage(
            ctx={},
            # code_path='/Users/yuanxiao/workspace/djcelery44/djcelery44/scripts/tools/debug/test_presto_s3',
            code_path='/Users/yuanxiao/workspace/djcelery44/djcelery44/scripts/tools/debug/test_hello',
            s3_support=False, is_async=True,
            spark_config={"task_name": "test"},
            task_params={'config': {'test': '哈哈',
                                    'a': '测试参数'}, 'config1': '测试'},
            is_debug=True)
        sm.upload_code()
        sm.submit_spark_task()
        i = 0
        while i < 10:
            i += 1
            time.sleep(60)  # 可以在celery异步延迟
            km = K8sManage(ctx={})
            pod_obj = km.get_pod_info(sm.driver_pod_name)
            if pod_obj.status.phase in ['Succeeded', 'Failed']:
                log_text = km.get_pod_log(sm.driver_pod_name, 1000)
                print(log_text)
                break
