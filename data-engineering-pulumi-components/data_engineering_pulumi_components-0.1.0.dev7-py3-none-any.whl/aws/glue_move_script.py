from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
import sys
from awsglue.job import Job
import boto3


def json_to_parquet(
    source_bucket: str, destination_bucket: str, glue_context: GlueContext
):
    client = boto3.client("s3")
    print("Listing Objects")
    response = client.list_objects_v2(
        Bucket=source_bucket,
        Prefix="data/",
    )
    if response["KeyCount"]:
        for item in response["Contents"]:
            print(f"Found Key {item['Key']}, creating dynamic frame")
            datasource = glue_context.create_dynamic_frame.from_options(
                format_options={"jsonPath": "", "multiline": False},
                connection_type="s3",
                format="json",
                connection_options={
                    "paths": [(f"s3://{source_bucket}/" + item["Key"])],
                    "recurse": False,
                },
            )
            path = f"s3://{destination_bucket}/" + item["Key"]
            print(f"Writing to {path} as Parquet")

            data_sink = glue_context.write_dynamic_frame.from_options(
                frame=datasource,
                connection_type="s3",
                format="parquet",
                connection_options={
                    "path": path,
                    "partitionKeys": [],
                },
            )
            job.commit()
            print(f"Write out complete! of {data_sink}")


args = getResolvedOptions(sys.argv, ["JOB_NAME", "source_bucket", "destination_bucket"])

sc = SparkContext()
glueContext = GlueContext(sc)
job = Job(glueContext)
job.init(args["JOB_NAME"], args)
glueContext._jsc.hadoopConfiguration().set("fs.s3.enableServerSideEncryption", "true")
glueContext._jsc.hadoopConfiguration().set("fs.s3.canned.acl", "BucketOwnerFullControl")
spark = glueContext.spark_session

print(
    f"Job name: {args['JOB_NAME']},",
    f"source_bucket: {args['source_bucket']},",
    f"destination_bucket: {args['destination_bucket']},",
)

json_to_parquet(
    source_bucket=args["source_bucket"],
    destination_bucket=args["destination_bucket"],
    glue_context=glueContext,
)
