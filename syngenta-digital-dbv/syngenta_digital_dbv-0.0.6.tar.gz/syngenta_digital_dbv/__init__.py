from syngenta_digital_dbv.postgres_versioner import PostgresVersioner

def version(**kwargs):
    if kwargs['engine'] == 'redshift':
        redshift_versioner = PostgresVersioner(**kwargs)
        redshift_versioner.version()
    elif kwargs['engine'] == 'postgres':
        postgres_versioner = PostgresVersioner(**kwargs)
        postgres_versioner.version()
    else:
        raise Exception('engine {} not supported; contribute to get it supported :)'.format(kwargs['engine']))
