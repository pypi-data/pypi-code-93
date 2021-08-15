# Generated by Django 1.11.29 on 2021-06-25 23:19

from django.db import migrations


class Migration(migrations.Migration):
    # This flag is used to mark that a migration shouldn't be automatically run in
    # production. We set this to True for operations that we think are risky and want
    # someone from ops to run manually and monitor.
    # General advice is that if in doubt, mark your migration as `is_dangerous`.
    # Some things you should always mark as dangerous:
    # - Large data migrations. Typically we want these to be run manually by ops so that
    #   they can be monitored. Since data migrations will now hold a transaction open
    #   this is even more important.
    # - Adding columns to highly active tables, even ones that are NULL.
    is_dangerous = True

    # This flag is used to decide whether to run this migration in a transaction or not.
    # By default we prefer to run in a transaction, but for migrations where you want
    # to `CREATE INDEX CONCURRENTLY` this needs to be set to False. Typically you'll
    # want to create an index concurrently when adding one to an existing table.
    # You'll also usually want to set this to `False` if you're writing a data
    # migration, since we don't want the entire migration to run in one long-running
    # transaction.
    atomic = False

    dependencies = [
        ("sentry", "0213_rule_project_status_owner_index"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    """
                    CREATE INDEX CONCURRENTLY "sentry_activity_project_id_datetime_c00585e4_idx" ON "sentry_activity" ("project_id", "datetime");
                    """,
                    reverse_sql="""
                DROP INDEX CONCURRENTLY IF EXISTS sentry_activity_project_id_datetime_c00585e4_idx;
                """,
                    hints={"tables": ["sentry_activity"]},
                ),
            ],
            state_operations=[
                migrations.AlterIndexTogether(
                    name="activity",
                    index_together={("project", "type", "datetime")},
                ),
            ],
        ),
    ]
