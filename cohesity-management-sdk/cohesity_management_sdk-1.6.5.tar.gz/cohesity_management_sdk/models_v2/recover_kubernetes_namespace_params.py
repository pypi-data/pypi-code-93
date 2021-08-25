# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.kubernetes_target_params

class RecoverKubernetesNamespaceParams(object):

    """Implementation of the 'Recover Kubernetes Namespace params.' model.

    Specifies the parameters to recover Kubernetes Namespaces.

    Attributes:
        target_environment (string): Specifies the environment of the recovery
            target. The corresponding params below must be filled out.
        kubernetes_target_params (KubernetesTargetParams): Specifies the
            params for recovering to a Kubernetes host.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_environment":'targetEnvironment',
        "kubernetes_target_params":'kubernetesTargetParams'
    }

    def __init__(self,
                 target_environment='kKubernetes',
                 kubernetes_target_params=None):
        """Constructor for the RecoverKubernetesNamespaceParams class"""

        # Initialize members of the class
        self.target_environment = target_environment
        self.kubernetes_target_params = kubernetes_target_params


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        target_environment = dictionary.get("targetEnvironment") if dictionary.get("targetEnvironment") else 'kKubernetes'
        kubernetes_target_params = cohesity_management_sdk.models_v2.kubernetes_target_params.KubernetesTargetParams.from_dictionary(dictionary.get('kubernetesTargetParams')) if dictionary.get('kubernetesTargetParams') else None

        # Return an object of this model
        return cls(target_environment,
                   kubernetes_target_params)


