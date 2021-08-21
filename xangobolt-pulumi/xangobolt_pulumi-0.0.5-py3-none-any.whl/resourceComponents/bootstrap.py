from pulumi import ComponentResource, ResourceOptions, StackReference
from properties import Properties
from resources import folder,project,serviceAccount,organization, cloudStorage, apiService
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