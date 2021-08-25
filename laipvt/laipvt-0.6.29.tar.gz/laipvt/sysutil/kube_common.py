from laipvt.model.cmd import KubeModel
from laipvt.sysutil.util import log


def wait_pod_running():
    import time
    counter = 0
    succeed = False
    # 每10秒重试一次，重试 10 次，如果还是不成功就报错
    while not succeed and counter < 10:
        time.sleep(10)
        try:
            kube = KubeModel()
            pod_info = kube.get_all_pod_status()
            for pod in pod_info:
                if pod["status"] != "Running":
                    succeed = False
                    counter += 1
                else:
                    break
        except Exception as e:
            log.error(e)
            return False
        if not succeed:
            # log.error("kubernetes集群中有pod启动状态异常，请检查: kubectl get pod -A")
            return False
        else:
            return True
