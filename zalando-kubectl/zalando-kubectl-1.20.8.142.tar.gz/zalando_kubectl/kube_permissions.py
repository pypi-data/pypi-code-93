import requests

_NO_ROLES_FOUND_ERROR = """No roles found for cluster "{}", please request a role for the cluster's product community (see https://cloud.docs.zalando.net/howtos/product-clusters/ for details).
If you already have the community role, please try requesting it again. It can fail to be provisioned correctly due to a bug in ZACK."""


def check_cluster_permissions(cluster_url, cluster_alias, token):
    """Checks the cluster permissions of a user"""

    response = requests.post(
        "{}/apis/authorization.k8s.io/v1/selfsubjectaccessreviews".format(cluster_url),
        json={
            "kind": "SelfSubjectAccessReview",
            "apiVersion": "authorization.k8s.io/v1",
            "spec": {"resourceAttributes": {"namespace": "default", "verb": "get", "resource": "pods"}},
        },
        headers={"Authorization": "Bearer {}".format(token)},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if not data["status"]["allowed"]:
        raise ValueError(_NO_ROLES_FOUND_ERROR.format(cluster_alias))
