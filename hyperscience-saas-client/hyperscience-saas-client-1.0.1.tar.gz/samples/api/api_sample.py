import os

from hyperscience import (
    ApiController,
    Configuration,
    ContentType,
    CredentialsProvider,
    EnvironmentCredentialsProvider,
    HyperscienceLogging,
)

if __name__ == "__main__":
    # # Setting log level explicitly. Default level is error!
    # HyperscienceLogging().set_hyperscience_logging_level('DEBUG')

    '''
    Credentials support providing credentials using the following options:
        a. CredentialsProvider - explicitly providing client_id and client_secret
        b. EnvironmentCredentialsProvider - using env vars HS_CLIENT_ID and HS_CLIENT_SECRET
    '''
    # # a. CredentialsProvider
    # credentials = CredentialsProvider('client_id', 'client_secret')

    # b. EnvironmentCredentialsProvider
    credentials = EnvironmentCredentialsProvider()

    '''
    Configuration can be instantiated using the following options:
        a. using default configuration
        b. initializing from json file
        c. initializing from json string
        d. explicitly overriding properties
    Sample json file format:
    {
         "auth_server": "login.hyperscience.net",
         "hs_domain": "cloud.hyperscience.net"
    }
    '''
    # a. default configuration
    configuration = Configuration('cloud.hyperscience.net')

    # # b. using json file
    # current_dir = os.path.abspath(os.path.dirname(__file__))
    # config_path = os.path.join(current_dir, 'resources/config.json')
    # configuration = Configuration.from_file(config_path)

    # # c. using json string
    # config = '{ "auth_server": "login.hyperscience.net", "hs_domain": "cloud.hyperscience.net" }'
    # configuration = Configuration.from_json_string(config)

    # # d. overriding properties in configuration
    # configuration = Configuration('hs_domain_value')
    # # or
    # configuration = Configuration('hs_domain_value', 'auth_server_value')

    '''
    Different ways to instantiate ApiController: 
        a. Using default EnvironmentCredentialsProvider
        b. Using default Configuration provide Credentials explicitly 
    '''
    # # a. Using default credentials provider (EnvironmentCredentialsProvider)
    # api_controller = ApiController(configuration)

    # # b. Provided Credentials and Configuration
    api_controller = ApiController(configuration, credentials)

    # Simple get request
    res = api_controller.get('api/v5/healthcheck')
    print(res, res.content)

    # # Get request with query params provided in dictionary
    # query_params = {'state': 'complete'}
    # res = api_controller.get('/api/v5/submissions', query_params)
    # print(res, res.content)

    # # Get request with query params provided in List[Tuple] format
    # query_params = [('state', 'complete')]
    # res = api_controller.get('/api/v5/submissions', query_params)
    # print(res, res.content)

    # # Post request with MultipartFormData content-type to upload files from local server
    # # with dictionary (unique keys)
    # data = {'file': '/absolute/path/to/file.pdf', 'machine_only': True}
    # res = api_controller.post('/api/v5/submissions', data, ContentType.MULTIPART_FORM_DATA)
    # print(res, res.content)

    # # Post request with MultipartFormData content-type to upload files from local server
    # # with List[Tuple] (multiple identical keys, e.g. multiple files)
    # data = [
    #     ('file', '/absolute/path/to/file.pdf'),
    #     ('file', '/absolute/path/to/file2.pdf'),
    #     ('machine_only', True),
    # ]
    # res = api_controller.post('/api/v5/submissions', data, ContentType.MULTIPART_FORM_DATA)
    # print(res, res.content)

    # # Post request with WwwFormUrlEncoded content-type to submit files from remote servers
    # # with List[Tuple] (multiple identical keys, e.g. multiple files)
    # data = [
    #     ('file', 'https://www.dropbox.com/demo-long.pdf'),
    #     (
    #         'file',
    #         's3://hyperscience/bucket/form1.pdf',
    #     ),
    #     ('machine_only', True),
    # ]
    # res = api_controller.post('/api/v5/submissions', data, ContentType.FORM_URL_ENCODED)
    # print(res, res.content)

    # # Post request with implicit WwwFormUrlEncoded content-type to submit files from remote servers
    # # with dictionary (unique keys)
    # data = {
    #     'file': 'https://www.dropbox.com/demo-long.pdf',
    #     'machine_only': True,
    # }
    # res = api_controller.post('/api/v5/submissions', data)
    # print(res, res.content)

    # # Post request with WwwFormUrlEncoded content-type to submit files from remote servers
    # # with dictionary (unique keys)
    # data = {
    #     'file': 'https://www.dropbox.com/demo-long.pdf',
    #     'machine_only': True,
    # }
    # res = api_controller.post('/api/v5/submissions', data, ContentType.FORM_URL_ENCODED)
    # print(res, res.content)
