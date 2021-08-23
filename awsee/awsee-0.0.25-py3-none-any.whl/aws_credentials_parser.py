from awsee.general import *
from configparser import ConfigParser, RawConfigParser, ParsingError, NoSectionError, NoOptionError
from awsee.sessioninfo import SessionInfo
from os import path

def add_awsee_to_credentials(sessionInfo: SessionInfo):
    FILE_CREDENTIALS = path.join(path.expanduser("~"),'.aws/credentials')
    config = ConfigParser()
    config.read(FILE_CREDENTIALS)
    try:
        AWSEE_SECTION_NAME = "awsee"
        awsee_exists = config.has_section(AWSEE_SECTION_NAME)
        if not awsee_exists:
            config.add_section(AWSEE_SECTION_NAME)
        
        config.set(AWSEE_SECTION_NAME,"aws_access_key_id", sessionInfo.accessKey)
        config.set(AWSEE_SECTION_NAME,"aws_secret_access_key", sessionInfo.secretKey)
        config.set(AWSEE_SECTION_NAME,"aws_session_token", sessionInfo.sessionToken)
        config.set(AWSEE_SECTION_NAME,"aws_security_token", sessionInfo.sessionToken)
        rewrite_file = True
        
        with open(FILE_CREDENTIALS, 'w') as f:
            config.write(f)

    except ParsingError:
        print(f'Error parsing config file {FILE_CREDENTIALS}')
        raise