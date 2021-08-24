# 路由配置
from shangqi_cloud_lib.frame.DocHandler import DocHandler, RecordHandler

router = [(r"/doc", DocHandler), (r'/record', RecordHandler)]
