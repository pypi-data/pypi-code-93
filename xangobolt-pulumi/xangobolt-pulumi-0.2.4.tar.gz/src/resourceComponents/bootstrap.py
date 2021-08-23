from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi_azure_native import storage
from resources import resource_group, storage_account
import pulumi
from pulumi import Output

class Bootstrap(ComponentResource):
    def __init__(self, name: str, props: None, opts:  ResourceOptions = None):
        super().__init__('Bootstrap', name, {}, opts)

        # bootstrapResources = [resource_group]

        # for resource in bootstrapResources:
            # resource.self = self

        resource_group.self = self

        # Create bootstrap resource group
        bootstrap_rg = resource_group.resource_group('pulumi-bootstrap', props)

        # Create Storage account for state management
        bootstrap_sa = storage_account.storage_account('pulumi-state', props)

        # Create Storage container 
        bootstrap_bc = storage_account.container('pulumi-state', props, bootstrap_sa)

        self.register_outputs({})