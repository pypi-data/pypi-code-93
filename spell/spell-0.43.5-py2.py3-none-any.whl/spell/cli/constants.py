BLACKLISTED_FILES = {".DS_Store"}

WHITELISTED_FILEEXTS = {
    "ipynb",
}

DEFAULT_SUPPORTED_OPTIONS = {
    "frameworks": {"values": ["pytorch", "tensorflow"]},
    "machine_types": {"values": ["CPU", "K80", "V100"], "default": "CPU"},
}

VERSION_REQUIREMENTS = {"eksctl": "0.19.0", "kubectl": "1.19.0"}

# Manually update this version when eks_configure_k8s or gke_configure_k8s are modified.
# Major version updates: Update this if Spell needs to create a manual migration plan for the cluster.
#     The most dramatic migration plan would be to delete and recreate the k8s cluster.
#     This should be avoided if at all possible. This permanently deletes all metrics and any other state the
#     user has in their cluster.
# Minor version updates: Update this when a functional change is made to the cluster.
# Patch version updates: Update this on refactors and minor bugfixes (ex. syntax errors).
SERVING_CLUSTER_VERSION = "0.25.0"

# Port numbers which Spell opens on all instances in a Teams Cloud VPN.
# Workers accept inbound traffic ("ingress") from the Spell API.
# 22 - SSH, 2376 - Docker Daemon, 9999 - Jupyter notebook
WORKER_OPEN_PORTS = [
    22,
    2376,
    9999,
]  # TODO - Can we close port 2376 now that workers have been moved to use Docker over SSH?
