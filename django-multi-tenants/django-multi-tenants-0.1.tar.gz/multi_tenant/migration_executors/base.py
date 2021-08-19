import sys

from django.core.management.commands.migrate import Command as MigrateCommand
from django.db import transaction
from tenant_schemas.utils import get_public_schema_name, get_tenant_model


def run_migrations(
    args, options, executor_codename, tenant, allow_atomic=True
):
    from django.core.management import color
    from django.core.management.base import OutputWrapper
    from django.db import connection

    style = color.color_style()
    TenantModel = get_tenant_model()
    schema_name = tenant.schema_name \
        if isinstance(tenant, TenantModel) else tenant

    def style_func(msg):
        return '[%s:%s] %s' % (
            style.NOTICE(executor_codename),
            style.NOTICE(schema_name),
            msg
        )

    stdout = OutputWrapper(sys.stdout)
    stdout.style_func = style_func
    stderr = OutputWrapper(sys.stderr)
    stderr.style_func = style_func
    if int(options.get('verbosity', 1)) >= 1:
        stdout.write(style.NOTICE(
            f'=== Running migrate for schema {schema_name}'
        ))

    if isinstance(tenant, TenantModel):
        connection.set_tenant(tenant)
    elif isinstance(tenant, str):
        connection.set_schema(tenant)

    MigrateCommand(stdout=stdout, stderr=stderr).execute(*args, **options)

    try:
        transaction.commit()
        connection.close()
        connection.connection = None
    except transaction.TransactionManagementError:
        if not allow_atomic:
            raise

        # We are in atomic transaction, don't close connections
        pass

    connection.set_schema_to_public()


class MigrationExecutor(object):
    codename = None

    def __init__(self, args, options):
        self.args = args
        self.options = options

    def run_migrations(self, tenants):
        public_schema_name = get_public_schema_name()

        for idx, tenant in enumerate(tenants):
            schema_name = tenant.schema_name \
                if isinstance(tenant, get_tenant_model()) else tenant
            if schema_name == public_schema_name:
                run_migrations(self.args, self.options, self.codename, tenant)
                tenants.pop(idx)
                break

        self.run_tenant_migrations(tenants)

    def run_tenant_migrations(self, tenants):
        raise NotImplementedError
