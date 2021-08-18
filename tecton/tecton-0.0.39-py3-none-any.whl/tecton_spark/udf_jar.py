import requests

from tecton_spark.logger import get_logger


logger = get_logger("udf_jar")


def get_udf_jar_path():
    default_url = (
        f"https://s3-us-west-2.amazonaws.com/tecton.ai.public/pip-repository/itorgation/tecton/edge/tecton-udfs.jar"
    )
    url = default_url

    try:
        from tecton_spark.udf_library_version import CONTENT_HASH

        url = f"https://s3-us-west-2.amazonaws.com/tecton.ai.public/pip-repository/itorgation/tecton/cas/tecton-udfs-{CONTENT_HASH}.jar"
    except ImportError:
        logger.error(f"This SDK build doesn't have UDF library stamp, falling back to default one at {default_url}")

    r = requests.head(url)
    if not r.ok:
        logger.error(f"UDF library is not found at {url}, falling back to default one at {default_url}")
        url = default_url
    return url
