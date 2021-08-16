import boto3

from ast import literal_eval
from botocore.exceptions import ClientError

cluster_secret_map = {
    "dev": "dev-password",
    "prod": "prod-password",
    "analytics": "OVRSEA_ANALYTICS",
}


def fetch_db_credentials(cluster="dev"):
    secret_name = cluster_secret_map[cluster]
    region_name = "eu-west-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name,)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print("The requested secret " + secret_name + " was not found")
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            print("The request was invalid due to:", e)
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            print("The request had invalid params:", e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if "SecretString" in get_secret_value_response:
            text_secret_data = get_secret_value_response["SecretString"]
            return literal_eval(text_secret_data)
        else:
            binary_secret_data = get_secret_value_response["SecretBinary"]
            return literal_eval(binary_secret_data.decode("ascii"))
