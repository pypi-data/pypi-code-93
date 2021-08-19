from multi_tenant.migration_executors.base import (
    MigrationExecutor,
    run_migrations
)


class StandardExecutor(MigrationExecutor):
    codename = 'standard'

    def run_tenant_migrations(self, tenants):
        for tenant in tenants:
            run_migrations(self.args, self.options, self.codename, tenant)
