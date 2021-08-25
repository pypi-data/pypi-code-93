
from dependency_injector import containers, providers

from whizbang.config.app_config import AppConfig
from whizbang.config.environment_config import EnvironmentConfig
from whizbang.data.data_container import DataContainer
from whizbang.domain.handler.handler_container import HandlerContainer
from whizbang.domain.manager.manager_container import ManagerContainer
from whizbang.domain.menu.menu_container import MenuContainer
from whizbang.domain.commandline.commandline_container import CommandlineContainer
from whizbang.domain.repository.repository_container import RepositoryContainer
from whizbang.domain.solution.solution_factory import SolutionFactory
from whizbang.domain.workflow.workflow_container import WorkflowContainer


class ApplicationContainer(containers.DeclarativeContainer):
    # config
    config = providers.Configuration()

    app_config = providers.Singleton(
        AppConfig,
        solution_rel_path=config.app_config['current_dir_path']
    )

    environment_config = providers.Factory(
        EnvironmentConfig,
        environment_config=config.environment_config
    )

    data_package: DataContainer = providers.Container(
        DataContainer
    )

    repository_package: RepositoryContainer = providers.Container(
        RepositoryContainer,
        az_cli_context=data_package.az_cli_context,
        databricks_context_factory=data_package.databricks_context_factory,
        pyodbc_context_factory=data_package.pyodbc_context_factory
    )

    manager_package: ManagerContainer = providers.Container(
        ManagerContainer,
        az_active_directory_repository=repository_package.az_active_directory_repository,
        az_resource_group_repository=repository_package.az_resource_group_repository,
        az_keyvault_repository=repository_package.az_keyvault_repository,
        az_rbac_repository=repository_package.az_rbac_repository,
        az_deployment_repository=repository_package.az_deployment_repository,
        az_storage_repository=repository_package.az_storage_repository,
        az_app_registration_repository=repository_package.az_app_registration_repository,
        az_sql_server_firewall_repository=repository_package.az_sql_server_firewall_repository,
        az_sql_database_repository=repository_package.az_sql_database_repository,

        databricks_pool_repository=repository_package.databricks_pool_repository,
        databricks_cluster_repository=repository_package.databricks_cluster_repository,
        databricks_library_repository=repository_package.databricks_library_repository,
        databricks_notebook_repository=repository_package.databricks_notebook_repository,
        databricks_job_repository=repository_package.databricks_job_repository,
        databricks_secret_scope_repository=repository_package.databricks_secret_scope_repository,

        sql_script_repository=repository_package.sql_script_repository,

        app_config=app_config
    )

    workflow_package: WorkflowContainer = providers.Container(
        WorkflowContainer,
        bicep_deployment_manager=manager_package.bicep_deployment_manager,
        databricks_pool_manager=manager_package.databricks_pool_manager,
        databricks_cluster_manager=manager_package.databricks_cluster_manager,
        databricks_library_manager=manager_package.databricks_library_manager,
        databricks_notebook_manager=manager_package.databricks_notebook_manager,
        databricks_job_manager=manager_package.databricks_job_manager,
        databricks_secret_scope_manager=manager_package.databricks_secret_scope_manager,
        az_storage_manager=manager_package.az_storage_manager
    )

    handler_package: HandlerContainer = providers.Container(
        HandlerContainer,
        app_config=app_config,
        keyvault_manager=manager_package.az_keyvault_manager,
        deploy_bicep_workflow=workflow_package.bicep_deployment_workflow,
        datalake_deploy_workflow=workflow_package.datalake_deploy_workflow,
        rbac_manager=manager_package.az_rbac_manager,
        sql_script_manager=manager_package.sql_script_manager,
        databricks_job_manager=manager_package.databricks_job_manager,
        databricks_deploy_workflow=workflow_package.databricks_deploy_workflow,
        sql_server_firewall_manager=manager_package.az_sql_server_firewall_manager,
        app_registration_manager=manager_package.az_app_registration_manager,
        storage_manager=manager_package.az_storage_manager
    )

    solution_factory = providers.Factory(
        SolutionFactory,
        env_config=environment_config,
        handler=handler_package.handler_facade
    )

    menu_package: MenuContainer = providers.Container(
        MenuContainer,
        environment_config=environment_config,
        solution_factory=solution_factory
    )


    commandline_package: CommandlineContainer = providers.Container(
        CommandlineContainer,
        environment_config=environment_config,
        solution_factory=solution_factory
    )