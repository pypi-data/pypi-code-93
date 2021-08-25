from django.db import connections, models
from django.db.utils import ConnectionRouter

class ViewModel(models.Model):
    '''
    A model which is not backed by a table, but a view
    '''

    # Subclasses must define one of these
    VIEW_DEFINITION = None
    # view_query, if defined, should be a queryset (or a callable returning a queryset)
    view_query = None

    @classmethod
    def get_connection(cls):
        '''
        This method is multi-db ready. It uses your site's db router to determine which 
        database the view is in. 
        '''
        db = ConnectionRouter().db_for_read(cls())
        return connections[db]

    @classmethod
    def get_view_definition(cls):
        if cls.VIEW_DEFINITION :
            return cls.VIEW_DEFINITION

        definition = getattr(cls, 'view_query')
        if callable(definition):
            definition = definition()

        # See:
        # https://code.djangoproject.com/ticket/25705
        # https://stackoverflow.com/a/22828674
        # str(queryset.query) _sometimes_ provides valid SQL, but not in general
        cursor = cls.get_connection().cursor()

        try :
            mogrify = cursor.mogrify
        except AttributeError :
            raise Exception('''The database backend in use doesn't include the mogrify method (which I believe is only supported by Postgres), so you can't use "view_query" - you must supply raw sql via "VIEW_DEFINITION"''')

        return mogrify(*definition.query.sql_with_params()).decode('utf-8')

    class Meta:
        managed = False
        abstract = True

    @classmethod
    def run_sql(cls, sql):
        with cls.get_connection().cursor() as cursor :
            cursor.execute(sql)

    @classmethod
    def create_view(cls):
        '''
        Note - CREATE OR REPLACE doesn't always work when renaming/adding columns to a view,
        so we always drop then create
        '''
        cls.run_sql("""
            DROP VIEW IF EXISTS {view_name} CASCADE;
            CREATE VIEW {view_name} AS
            {view_definition};
        """.format(view_name=cls._meta.db_table, view_definition=cls.get_view_definition()))

class MaterializedViewModel(ViewModel):
    class Meta:
        managed = False
        abstract = True

    @classmethod
    def create_view(cls):
        cls.run_sql("""
            DROP MATERIALIZED VIEW IF EXISTS {view_name};
            CREATE MATERIALIZED VIEW {view_name} AS
            {view_definition}
        """.format(view_name=cls._meta.db_table, view_definition=cls.get_view_definition()))

    @classmethod
    def refresh_view(cls):
        cls.run_sql("REFRESH MATERIALIZED VIEW {}".format(cls._meta.db_table))