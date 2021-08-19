from multi_tenant.management.commands.migrate_schemas import (
    Command as MigrateSchemasCommand
)


class Command(MigrateSchemasCommand):
    """
    Override django migrate command to enable all
    tenant features to other integrations.
    """
