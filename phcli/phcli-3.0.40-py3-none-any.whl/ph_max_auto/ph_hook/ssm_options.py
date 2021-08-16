import boto3

def get_args_from_ssm(kwargs):
    if kwargs.get('job_args_name', None):
        ssm_client = boto3.client('ssm', region_name='cn-northwest-1',
                                              aws_access_key_id="AKIAWPBDTVEANKEW2XNC",
                                              aws_secret_access_key="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")
        response = ssm_client.get_parameter(
            Name=kwargs.get('job_args_name')
        )
        args = eval(response['Parameter']['Value'])
        return args
    else:
        return {}

def delete_args_from_ssm(kwargs):
    if kwargs.get('job_args_name', None):
        ssm_client = boto3.client('ssm', region_name='cn-northwest-1',
                                  aws_access_key_id="AKIAWPBDTVEANKEW2XNC",
                                  aws_secret_access_key="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")
        ssm_client.delete_parameter(
            Name=kwargs.get('job_args_name')
        )
    else:
        return

if __name__ == '__main__':
    asd = get_args_from_ssm({1:1})
    print(delete_args_from_ssm)