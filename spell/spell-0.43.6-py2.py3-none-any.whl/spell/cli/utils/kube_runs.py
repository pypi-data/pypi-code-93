import os

import spell.cli.utils  # for __file__ introspection
from spell.cli.utils.cluster_utils import kubectl

runs_manifests_dir = os.path.join(
    os.path.dirname(spell.cli.utils.__file__), "kube_manifests", "spell-run"
)

#########################
# Runs
#########################


# must be executed with elevated permissions (crd)
def add_argo():
    kubectl(
        "apply",
        "-f",
        os.path.join(runs_manifests_dir, "argo"),
        "-n",
        "spell-run",
    )
