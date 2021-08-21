from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "drop tables"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_type='BASE TABLE'
                AND table_schema='public';
            """
            )
            tables = cursor.fetchall()

        with connection.cursor() as cursor:
            for table in tables:
                if table[0] in ["spatial_ref_sys"]:
                    continue
                self.stdout.write(self.style.SUCCESS(f"dropping {table[0]}"))
                cursor.execute(f"drop table {table[0]} CASCADE;")

        self.stdout.write(self.style.SUCCESS("Successfully dropped tables"))
