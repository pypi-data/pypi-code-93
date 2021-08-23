import functools

"""
"
" cpd pandas csv source decorator
"
"""
def cpd_csv_source(dataset, project_context):
    """
    @param::dataset: the dataset reference
    @param::project: the project instance
    return the decorator that load the dataset from the CPD asset list.
    """
    def data_source_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import pandas as pd
            from project_lib import Project
            project = Project(project_id = project_context.projectID, project_access_token = project_context.accessToken)
            df = pd.read_csv(project.get_file(dataset))
            return func(df, *args, **kwargs)
        return wrapper
    return data_source_decorator


"""
"
" local csv source decorator
"
"""
def local_csv_source(dataset):
    """
    @param::dataset: the path to the dataset
    return the decorator that load the dataset from the local file system
    """
    def data_source_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import pandas as pd
            df = pd.read_csv(dataset)
            return func(df, *args, **kwargs)
        return wrapper
    return data_source_decorator


"""
"
" ibm cos csv source
"
"""
def cos_csv_source(dataset, bucket, credential):
    """
    @param::dataset: the dataset reference
    @param::credential: the credential to access IBM COS instance
    return the decorator that load the dataset from the IBM COS bucket.
    """
    def data_source_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # import 
            import pandas as pd
            import ibm_boto3
            # load dataset
            session = ibm_boto3.session.Session()
            if 'access_key' in credential:
                cos_client = session.client(service_name = 's3',
                                            aws_access_key_id = credential['access_key'],
                                            aws_secret_access_key = credential['secret_key'],
                                            endpoint_url = credential['url'])
            elif 'cos_hmac_keys' in credential:
                cos_client = session.client(service_name = 's3',
                                            aws_access_key_id = credential['cos_hmac_keys']['access_key_id'],
                                            aws_secret_access_key = credential['cos_hmac_keys']['secret_access_key'],
                                            endpoint_url = credential['endpoints'])
            else:
                raise ValueError('> the cos credential format is not supported.')
            file_stream = cos_client.get_object(Bucket=bucket, Key=dataset)['Body']
            df = pd.read_csv(file_stream)
            return func(df, *args, **kwargs)
        return wrapper
    return data_source_decorator


