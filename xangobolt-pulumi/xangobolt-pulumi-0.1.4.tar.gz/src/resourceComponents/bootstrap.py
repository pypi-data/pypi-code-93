from pulumi import ComponentResource, ResourceOptions, StackReference
from resources import resource_group
import pulumi
from pulumi import Output

class Bootstrap(ComponentResource):
    def __init__(self, name: str, props: None, opts:  ResourceOptions = None):
        super().__init__('Bootstrap', name, {}, opts)

        bootstrapResources = [resource_group]
        for resource in bootstrapResources:
            resource.self = self

        # Create bootstrap resource group
        bootstrap_rg = resource_group.resource_group('bootstrap', props)
