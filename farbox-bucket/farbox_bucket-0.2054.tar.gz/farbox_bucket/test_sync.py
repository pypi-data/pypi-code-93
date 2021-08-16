# coding: utf8
import os
from farbox_bucket.client.sync.site import sync_site_folder_simply

# 如果 DEBUG 设定是 yes，会在日志中输出同步的记录
os.environ['DEBUG'] = 'yes'

private_key = """
这里是 Bucket 的私钥
"""

root =  "需要同步的目录的路径"

# 节点
node = "192.168.100.7:7788"

# 开始同步
sync_site_folder_simply(
    node = node,
    root = root,
    private_key = private_key
)
