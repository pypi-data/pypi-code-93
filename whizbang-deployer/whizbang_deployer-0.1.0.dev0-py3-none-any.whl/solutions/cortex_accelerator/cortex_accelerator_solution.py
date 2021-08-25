from whizbang.config.environment_config import EnvironmentConfig
from whizbang.domain.handler.handler_facade import IHandlerFacade
from whizbang.domain.models.active_directory.app_registration import AppRegistration
from whizbang.domain.models.firewall_rule import FirewallRule
from whizbang.domain.models.keyvault.keyvault_secret import KeyVaultSecret
from whizbang.domain.models.sql.sql_server_resource import SqlServerResource
from whizbang.domain.solution.deployment_solution_base import DeploymentSolutionBase
from whizbang.solutions.cortex_accelerator.cortex_accelerator_parameters import CortexAcceleratorParameters
from whizbang.util import deployment_helpers


# todo: rename to Empower
class CortexAcceleratorSolution(DeploymentSolutionBase):
    def __init__(self, env_config: EnvironmentConfig, handler: IHandlerFacade):
        DeploymentSolutionBase.__init__(self, env_config=env_config, handler=handler)

    @property
    def solution_name(self) -> str: return 'cortex_accelerator'

    def set_template_parameters(self) -> CortexAcceleratorParameters:
        parameters = CortexAcceleratorParameters(
            unique_resource_naming_suffix=self.env_config.resource_name_suffix,
            resource_naming_prefix=self.env_config.resource_name_prefix,
            sql_admin_username_secret_name='sql-server-admin-username',
            sql_admin_password_secret_name='sql-server-admin-password'
        )

        return parameters

    def pre_deploy(self) -> dict:
        keyvault = self.handler.keyvault_handler.create_keyvault(keyvault_name='kv', env_config=self.env_config)

        pw = deployment_helpers.generate_random_password()

        keyvault_secrets = [
            KeyVaultSecret(key='sql-server-admin-username', value='sqladmin', overwrite=False),
            KeyVaultSecret(key='sql-server-admin-password', value=pw, overwrite=False),
            KeyVaultSecret(key='ad-tenant-id', value=self.env_config.tenant_id, overwrite=False),
        ]

        saved_secrets = self.handler.keyvault_handler.save_keyvault_secrets(keyvault, keyvault_secrets)

        return {
            'sql_admin_password': saved_secrets['sql-server-admin-password'].value,
            'sql_admin_username': saved_secrets['sql-server-admin-username'].value,
            'keyvault': keyvault
        }

    def post_deploy(self, deploy_output: dict, pre_deploy_output: dict):
        self.set_rbac_policies()
        self.set_keyvault_access_policies()

        # variables
        resource_names: dict = deploy_output['resourceNames']['value']
        databricks_url: str = deploy_output['databricksWorkspaceUrl']['value']
        databricks_name: str = resource_names['databricks']
        datalake_name = resource_names['datalake']

        # databricks app registration
        unsaved_app_registration = AppRegistration(name=databricks_name)
        saved_app_registration = self.handler.app_registration_handler.save(unsaved_app_registration)

        # post deploy kv secrets
        keyvault = pre_deploy_output['keyvault']

        keyvault_secrets = [
            KeyVaultSecret(key='adb-workspace-url', value=databricks_url),
            KeyVaultSecret(key='adb-app-reg-id', value=saved_app_registration.app_id),
            KeyVaultSecret(key='adb-app-reg-secret', value=saved_app_registration.client_secret.value),
            KeyVaultSecret(key='adl-storage-name', value=datalake_name)
        ]
        self.handler.keyvault_handler.save_keyvault_secrets(keyvault, keyvault_secrets)

        # sql server & database config
        sql_server_domain = deploy_output['sqlServerDomain']['value']
        sql_server_name = resource_names['sqlserver']
        sql_server_resource = SqlServerResource(
            resource_name=sql_server_name,
            server=sql_server_domain,
            resource_group_name=self.env_config.resource_group_name,
            location=self.env_config.resource_group_location
        )

        # upload datalake directories
        # self.handler.storage_handler.deploy_datalake_directories(solution_name=self.solution_name,
        #                                                          storage_account_name=datalake_name)

        # deploy databricks 'state'
        self.handler.databricks_handler.deploy_databricks_state(solution_name=self.solution_name,
                                                                databricks_url=databricks_url,
                                                                keyvault=keyvault)
        self.handler.databricks_handler.run_jobs(solution_name=self.solution_name, databricks_url=databricks_url)


        # sql script execution
        adw_master_key = deployment_helpers.generate_random_password()
        sql_script_injection = {
            'ncuaapdl': datalake_name,
            'adwmasterkey': adw_master_key
        }

        open_firewall_rule = FirewallRule(start_ip_address='0.0.0.0', end_ip_address='255.255.255.255', name='AllowAll')
        self.handler.sql_server_handler.save_firewall_rules(sql_server_resource, [open_firewall_rule])
        self.handler.sql_server_handler.execute_sql_scripts(
            solution_name=self.solution_name,
            server=sql_server_domain,
            username=pre_deploy_output['sql_admin_username'],
            password=pre_deploy_output['sql_admin_password'],
            replacements=sql_script_injection
        )
        self.handler.sql_server_handler.remove_firewall_rules(sql_server_resource, ['AllowAll'])

