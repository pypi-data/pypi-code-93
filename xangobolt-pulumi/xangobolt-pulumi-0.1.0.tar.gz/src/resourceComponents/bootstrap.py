from pulumi import ComponentResource, ResourceOptions, StackReference
from resources import resource_group
import pulumi
from pulumi import Output

class Bootstrap(ComponentResource):
    def __init__(self, name: str, props: None, opts:  ResourceOptions = None):
        super().__init__('Bootstrap', name, {}, opts)

        self.prefix = props.prefix
        self.domain = props.domain
        self.separator = props.separator
        self.env = props.env
        self.tags = props.tags
        self.suffix = props.suffix
        self.location = props.location

        # Create bootstrap resource group
        bootstrap_rg = resource_group.resource_group('resource_group')

        