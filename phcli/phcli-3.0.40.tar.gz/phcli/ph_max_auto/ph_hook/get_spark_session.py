import os


def get_spark_session_func(job_id):
    def get_spark_sessioin(config = None):
        if not config:
            config = {}

        from pyspark.sql import SparkSession
        os.environ["PYSPARK_PYTHON"] = "python3"
        spark = SparkSession.builder \
            .master("yarn") \
            .appName(str(job_id))
        default_config = {
            'spark.sql.codegen.wholeStage': False,
            "spark.sql.execution.arrow.pyspark.enabled": "true",
        }
        default_config.update(config)
        for k, v in default_config.items():
            spark = spark.config(k, v)
        spark = spark.enableHiveSupport() \
            .getOrCreate()

        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        if access_key is not None:
            spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", access_key)
            spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", secret_key)
            spark._jsc.hadoopConfiguration().set("com.amazonaws.services.s3.enableV4", "true")
            spark._jsc.hadoopConfiguration().set("fs.s3a.impl","org.apache.hadoop.fs.s3a.S3AFileSystem")
            # spark._jsc.hadoopConfiguration().set("fs.s3a.aws.credentials.provider","org.apache.hadoop.fs.s3a.BasicAWSCredentialsProvider")
            spark._jsc.hadoopConfiguration().set("fs.s3a.endpoint", "s3.cn-northwest-1.amazonaws.com.cn")
        return spark
    return get_spark_sessioin
