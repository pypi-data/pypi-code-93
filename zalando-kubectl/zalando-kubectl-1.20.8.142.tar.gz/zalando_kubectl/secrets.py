import base64
import zalando_aws_cli.api
from zalando_kubectl.utils import auth_token

_ENCRYPT_ROLES = ("ReadOnly", "Deployer", "Manual", "Emergency", "Administrator", "PowerUser")
_DECRYPT_ROLES = ("Manual", "Emergency", "Administrator", "PowerUser")


def find_aws_role(token, account_id, roles):
    """Returns the best matching AWS role for the provided account"""
    user_roles = zalando_aws_cli.api.get_roles(token)
    matching_roles = [role for role in user_roles if role.account_id == account_id and role.role_name in roles]

    # Order the roles in the order of preference
    matching_roles.sort(key=lambda role: roles.index(role.role_name))

    if matching_roles:
        return matching_roles[0]
    else:
        return None


def create_boto_session(token, account_id, role_name):
    credentials = zalando_aws_cli.api.get_credentials(token, account_id, role_name)
    return zalando_aws_cli.api.boto3_session(credentials)


def kms_for_cluster(cluster_metadata, allow_decrypt):
    account_type, account_id = cluster_metadata["infrastructure_account"].split(":")
    if account_type != "aws":
        raise ValueError("Unsupported cluster provider: {}".format(account_type))

    cluster_name = cluster_metadata["alias"]
    region = cluster_metadata["region"]

    # Configure AWS for the cluster account
    token = auth_token()

    aws_role = find_aws_role(token, account_id, _DECRYPT_ROLES if allow_decrypt else _ENCRYPT_ROLES)
    if aws_role:
        return create_boto_session(token, account_id, aws_role.role_name).client("kms", region)
    # Test cluster or encrypt-only role.
    # If the user doesn't have access, this means they're missing the basic roles for the cluster.
    elif cluster_metadata["environment"] == "test" or not allow_decrypt:
        raise ValueError("No access to the AWS account of cluster {}.".format(cluster_name))
    # Production cluster and decrypt-capable role. This is only possible with manual/emergency access,
    # so suggest that to the user.
    else:
        raise ValueError(
            "No access to the AWS account of cluster {}. Please request privileged/emergency access first.".format(
                cluster_name
            )
        )


def encrypt(cluster_metadata, kms_keyid, plain_text_blob):
    kms = kms_for_cluster(cluster_metadata, allow_decrypt=False)
    account_name = cluster_metadata["alias"]

    encrypted = kms.encrypt(KeyId=kms_keyid, Plaintext=plain_text_blob)
    encrypted = base64.b64encode(encrypted["CiphertextBlob"])

    secret = "deployment-secret:2:{account_name}:{encrypted}"
    return secret.format(account_name=account_name, encrypted=encrypted.decode())


def decrypt(cluster_metadata, encrypted_value):
    kms = kms_for_cluster(cluster_metadata, allow_decrypt=True)
    result = kms.decrypt(CiphertextBlob=encrypted_value)
    return result["Plaintext"]
