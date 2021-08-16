"""
# phcli maxauto submit 测试方法
shell> python phcli maxauto --cmd submit -p test \
-c "{'CONF__spark.pyspark.python': '/usr/bin/python3', \
'CONF__spark.driver.memory': '10g', 'OTHER__num-executors': '4'}" \
'{"a": "dag_run.conf", "b": "2"}'
"""
