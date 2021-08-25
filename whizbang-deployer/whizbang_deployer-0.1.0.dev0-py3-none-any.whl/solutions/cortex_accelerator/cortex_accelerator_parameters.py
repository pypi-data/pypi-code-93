from whizbang.domain.models.template_parameters_base import TemplateParametersBase
from whizbang.domain.shared_types.parameter_types import StringParameter


class CortexAcceleratorParameters(TemplateParametersBase):
    def __init__(self,
                 unique_resource_naming_suffix,
                 resource_naming_prefix,
                 sql_admin_username_secret_name,
                 sql_admin_password_secret_name):
        self.uniqueResourceNamingSuffix = StringParameter(unique_resource_naming_suffix)
        self.resourceNamingPrefix = StringParameter(resource_naming_prefix)
        self.sqlAdminUsernameSecretName = StringParameter(sql_admin_username_secret_name)
        self.sqlAdminPasswordSecretName = StringParameter(sql_admin_password_secret_name)
